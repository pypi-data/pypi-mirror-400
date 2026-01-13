"""LIGER teacher for batch correction.

Uses the rliger R package for integrative non-negative matrix factorization.
"""

import numpy as np
import pandas as pd
from typing import Optional
from pathlib import Path

from .base import (
    BaseTeacher,
    RScriptRunner,
    generate_r_header,
    generate_data_loading_code,
    generate_data_saving_code,
)


class LIGERTeacher(BaseTeacher):
    """LIGER (Linked Inference of Genomic Experimental Relationships) teacher.

    Uses integrative non-negative matrix factorization (iNMF) for batch
    correction via the rliger R package.

    Note: LIGER produces very small-scale embeddings, so needs_normalization=True.

    Parameters
    ----------
    k : int, default=20
        Number of factors for NMF.
    lambda_param : float, default=5.0
        Regularization parameter.
    rscript_path : str, default="Rscript"
        Path to Rscript executable.

    Examples
    --------
    >>> teacher = LIGERTeacher()
    >>> Z_corrected = teacher.fit_transform(X_pca, batch_labels, adata=adata, batch_key="batch")
    """

    name = "LIGER"
    needs_normalization = True  # LIGER has very small-scale embeddings

    def __init__(
        self,
        k: int = 20,
        lambda_param: float = 5.0,
        rscript_path: str = "Rscript",
    ):
        super().__init__()
        self.k = k
        self.lambda_param = lambda_param
        self.runner = RScriptRunner(rscript_path)

    def fit_transform(
        self,
        X_pca: np.ndarray,
        batch_labels: np.ndarray,
        obs: Optional[pd.DataFrame] = None,
        verbose: bool = True,
        adata=None,
        batch_key: str = "batch",
        **kwargs,
    ) -> np.ndarray:
        """Apply LIGER batch correction.

        Parameters
        ----------
        X_pca : np.ndarray
            PCA embeddings (n_cells, n_pcs). Not used directly - LIGER
            works on gene expression.
        batch_labels : np.ndarray
            Batch labels (n_cells,).
        obs : pd.DataFrame, optional
            Cell metadata.
        verbose : bool
            Print progress.
        adata : AnnData
            Full AnnData object. Required for LIGER.
        batch_key : str
            Key in adata.obs for batch labels.

        Returns
        -------
        Z_corrected : np.ndarray
            LIGER-corrected embeddings.
        """
        if adata is None:
            raise ValueError(
                "LIGER requires the full AnnData object. "
                "Pass adata=adata to fit_transform()."
            )

        if verbose:
            print(f"{self.name}: k={self.k}, lambda={self.lambda_param}")

        # Create temp directory
        self.runner.create_temp_dir("liger_")

        try:
            # Save data for R
            data_paths = self.runner.save_anndata_for_r(
                adata, self.runner.temp_dir, prefix="input"
            )

            # Generate and run R script
            r_script = self._generate_r_script(
                expr_path=data_paths['expression'],
                obs_path=data_paths['obs'],
                var_path=data_paths['var'],
                batch_key=batch_key,
            )
            script_path = self.runner.temp_dir / "run_liger.R"
            script_path.write_text(r_script)

            if verbose:
                print("  Running LIGER via rliger...")

            self.runner.run_r_script(script_path, verbose=verbose)

            # Load results
            adata_corrected = self.runner.load_anndata_from_r(
                self.runner.temp_dir, prefix="corrected", original_adata=adata
            )

            if "X_emb" in adata_corrected.obsm:
                self.Z_corrected = adata_corrected.obsm["X_emb"]
            else:
                raise ValueError("LIGER did not produce embeddings (X_emb)")

            self._is_fitted = True

            if verbose:
                print(f"  Corrected shape: {self.Z_corrected.shape}")
                norm = np.mean(np.linalg.norm(self.Z_corrected, axis=1))
                print(f"  Mean L2 norm: {norm:.4f} (very small scale - normalization needed)")

            return self.Z_corrected

        finally:
            # Cleanup temp files
            self.runner.cleanup()

    def _generate_r_script(
        self,
        expr_path: Path,
        obs_path: Path,
        var_path: Path,
        batch_key: str,
    ) -> str:
        """Generate R script for LIGER.

        Parameters
        ----------
        expr_path : Path
            Path to expression matrix CSV.
        obs_path : Path
            Path to obs metadata CSV.
        var_path : Path
            Path to var metadata CSV.
        batch_key : str
            Batch column name.

        Returns
        -------
        str
            R script content.
        """
        header = generate_r_header(['rliger'])
        data_loading = generate_data_loading_code(expr_path, obs_path, var_path)

        liger_code = f'''
# Split data by batch
cat("Splitting data by batch...\\n")
batch_labels <- obs_df[["{batch_key}"]]
unique_batches <- unique(batch_labels)

# Create list of expression matrices per batch
batch_list <- list()
for (batch in unique_batches) {{
  batch_idx <- which(batch_labels == batch)
  batch_mat <- expr_mat_t[, batch_idx, drop=FALSE]
  batch_list[[as.character(batch)]] <- batch_mat
}}

cat("Creating LIGER object...\\n")
liger_obj <- createLiger(batch_list)

cat("Processing data...\\n")
liger_obj <- normalize(liger_obj)

# Select genes with fallback for small datasets
result <- tryCatch({{
  selectGenes(liger_obj, thresh = 0.001, combine = "union")
}}, error = function(e) {{
  cat("selectGenes() failed:", conditionMessage(e), "\\n")
  return(NULL)
}})

# Check if genes were selected using NEW API (rliger 2.x)
if (!is.null(result) && length(varFeatures(result)) > 0) {{
  liger_obj <- result
  cat("Selected", length(varFeatures(liger_obj)), "variable genes\\n")
}} else {{
  # Fallback: use all genes as variable genes (NEW API)
  cat("Using all genes as variable genes\\n")
  all_genes <- rownames(liger_obj@datasets[[1]]@rawData)
  varFeatures(liger_obj) <- all_genes
  cat("Set", length(varFeatures(liger_obj)), "genes as variable features\\n")
}}

liger_obj <- scaleNotCenter(liger_obj)

# Run integrative NMF
cat("Running integrative NMF (k={self.k}, lambda={self.lambda_param})...\\n")
liger_obj <- runIntegration(liger_obj, k = {self.k}, lambda = {self.lambda_param}, method = "iNMF")

# Quantile normalization
cat("Running quantile normalization...\\n")
n_cells_total <- ncol(getMatrix(liger_obj, slot = "rawData", returnList = FALSE))
min_cells_param <- max(2, min(20, n_cells_total %/% 10))
cat("Using minCells =", min_cells_param, "\\n")
liger_obj <- quantileNorm(liger_obj, minCells = min_cells_param)

# Extract corrected embedding (H.norm)
cat("Extracting corrected data...\\n")
embedding_mat <- slot(liger_obj, "H.norm")
cat("Embedding extracted:", nrow(embedding_mat), "x", ncol(embedding_mat), "\\n")

# Get normalized data from each dataset and combine
all_cells <- rownames(obs_df)
corrected_list <- list()
cell_mapping <- data.frame(original = character(), liger = character(), stringsAsFactors = FALSE)

for (ds_name in names(datasets(liger_obj))) {{
  ds <- dataset(liger_obj, ds_name)
  norm_data <- slot(ds, "normData")
  corrected_list[[ds_name]] <- norm_data

  # Build cell name mapping
  liger_cells <- colnames(norm_data)
  batch_mask <- batch_labels == ds_name
  orig_cells <- all_cells[batch_mask]

  cat("Batch", ds_name, ":", length(liger_cells), "cells in LIGER,", length(orig_cells), "cells in original\\n")

  if (length(liger_cells) == length(orig_cells)) {{
    new_mapping <- data.frame(original = orig_cells, liger = liger_cells, stringsAsFactors = FALSE)
    cell_mapping <- rbind(cell_mapping, new_mapping)
  }}
}}

# Combine batches
corrected_mat <- do.call(cbind, corrected_list)
cat("Normalized data combined:", nrow(corrected_mat), "x", ncol(corrected_mat), "\\n")

# Reorder to match original cell order
if (nrow(cell_mapping) == length(all_cells)) {{
  cat("Using cell name mapping to reorder...\\n")

  liger_order <- match(cell_mapping$liger[match(all_cells, cell_mapping$original)], colnames(corrected_mat))
  corrected_mat <- corrected_mat[, liger_order, drop=FALSE]
  colnames(corrected_mat) <- all_cells

  emb_liger_names <- cell_mapping$liger[match(all_cells, cell_mapping$original)]
  emb_order <- match(emb_liger_names, rownames(embedding_mat))

  if (any(is.na(emb_order))) {{
    cat("Warning: Some cells not found in embedding_mat\\n")
    valid_idx <- !is.na(emb_order)
    embedding_mat <- embedding_mat[emb_order[valid_idx], , drop=FALSE]
    rownames(embedding_mat) <- all_cells[valid_idx]
    corrected_mat <- corrected_mat[, valid_idx, drop=FALSE]
    obs_df <- obs_df[valid_idx, , drop=FALSE]
  }} else {{
    embedding_mat <- embedding_mat[emb_order, , drop=FALSE]
    rownames(embedding_mat) <- all_cells
  }}
}} else {{
  cat("Warning: Cell mapping incomplete, using index-based matching\\n")
  n_cells <- min(ncol(corrected_mat), nrow(embedding_mat), length(all_cells))
  corrected_mat <- corrected_mat[, 1:n_cells, drop=FALSE]
  colnames(corrected_mat) <- all_cells[1:n_cells]
  embedding_mat <- embedding_mat[1:n_cells, , drop=FALSE]
  rownames(embedding_mat) <- all_cells[1:n_cells]
  obs_df <- obs_df[1:n_cells, , drop=FALSE]
}}

cat("Final corrected_mat:", nrow(corrected_mat), "x", ncol(corrected_mat), "\\n")
cat("Final embedding_mat:", nrow(embedding_mat), "x", ncol(embedding_mat), "\\n")
'''

        data_saving = generate_data_saving_code(
            self.runner.temp_dir, prefix="corrected", save_embedding=True
        )

        return header + data_loading + liger_code + data_saving

    def cleanup(self):
        """Clean up temporary files."""
        self.runner.cleanup()

    def __repr__(self) -> str:
        return f"LIGERTeacher(k={self.k}, lambda={self.lambda_param})"

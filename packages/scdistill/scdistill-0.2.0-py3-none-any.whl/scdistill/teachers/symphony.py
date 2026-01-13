"""Symphony teacher for batch correction.

Uses the symphony R package for reference-based batch correction.
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


class SymphonyTeacher(BaseTeacher):
    """Symphony batch correction teacher.

    Uses reference-based batch correction via the symphony R package.
    Symphony is based on Harmony and builds a reference from all batches,
    then maps cells to the integrated space.

    Note: Symphony produces normal-scale embeddings, so needs_normalization=False.

    Parameters
    ----------
    n_pcs : int, default=20
        Number of PCA components.
    theta : float, default=2.0
        Soft clustering parameter (same as Harmony).
    rscript_path : str, default="Rscript"
        Path to Rscript executable.

    Examples
    --------
    >>> teacher = SymphonyTeacher()
    >>> Z_corrected = teacher.fit_transform(X_pca, batch_labels, adata=adata, batch_key="batch")
    """

    name = "Symphony"
    needs_normalization = False  # Symphony has normal-scale embeddings

    def __init__(
        self,
        n_pcs: int = 20,
        theta: float = 2.0,
        rscript_path: str = "Rscript",
    ):
        super().__init__()
        self.n_pcs = n_pcs
        self.theta = theta
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
        """Apply Symphony batch correction.

        Parameters
        ----------
        X_pca : np.ndarray
            PCA embeddings (n_cells, n_pcs). Not used directly.
        batch_labels : np.ndarray
            Batch labels (n_cells,).
        obs : pd.DataFrame, optional
            Cell metadata.
        verbose : bool
            Print progress.
        adata : AnnData
            Full AnnData object. Required for Symphony.
        batch_key : str
            Key in adata.obs for batch labels.

        Returns
        -------
        Z_corrected : np.ndarray
            Symphony-corrected embeddings.
        """
        if adata is None:
            raise ValueError(
                "Symphony requires the full AnnData object. "
                "Pass adata=adata to fit_transform()."
            )

        if verbose:
            print(f"{self.name}: n_pcs={self.n_pcs}, theta={self.theta}")

        # Create temp directory
        self.runner.create_temp_dir("symphony_")

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
            script_path = self.runner.temp_dir / "run_symphony.R"
            script_path.write_text(r_script)

            if verbose:
                print("  Running Symphony via symphony package...")

            self.runner.run_r_script(script_path, verbose=verbose)

            # Load results
            adata_corrected = self.runner.load_anndata_from_r(
                self.runner.temp_dir, prefix="corrected", original_adata=adata
            )

            if "X_emb" in adata_corrected.obsm:
                self.Z_corrected = adata_corrected.obsm["X_emb"]
            else:
                raise ValueError("Symphony did not produce embeddings (X_emb)")

            self._is_fitted = True

            if verbose:
                print(f"  Corrected shape: {self.Z_corrected.shape}")
                norm = np.mean(np.linalg.norm(self.Z_corrected, axis=1))
                print(f"  Mean L2 norm: {norm:.4f}")

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
        """Generate R script for Symphony.

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
        header = generate_r_header(['symphony', 'harmony', 'Seurat', 'Matrix'])
        data_loading = generate_data_loading_code(expr_path, obs_path, var_path)

        symphony_code = f'''
# Build Symphony reference directly
cat("Building Symphony reference...\\n")

# Convert to sparse matrix for Symphony
expr_mat_sparse <- as(expr_mat_t, "dgCMatrix")

# Get batch information
batch_labels <- obs_df[["{batch_key}"]]
unique_batches <- unique(batch_labels)

# Set vars parameter based on batch count
vars_param <- if (length(unique_batches) > 1) "{batch_key}" else NULL

# Adjust parameters for small datasets
n_genes <- nrow(expr_mat_sparse)
n_cells <- ncol(expr_mat_sparse)
d_param <- min({self.n_pcs}, n_genes - 1, n_cells - 1)

cat("Building reference with", n_cells, "cells and", n_genes, "genes...\\n")
cat("Using d =", d_param, "PCs\\n")

reference <- symphony::buildReference(
  exp_ref = expr_mat_sparse,
  metadata_ref = obs_df,
  vars = vars_param,
  verbose = TRUE,
  do_umap = FALSE,
  do_normalize = FALSE,  # Data is already log-normalized
  vargenes_method = "vst",
  topn = min(2000, n_genes),
  d = d_param,
  K = max(1, min(10, n_cells %/% 10)),  # Adjust cluster number for small datasets
  theta = {self.theta}
)

cat("Extracting corrected embeddings...\\n")
# Use reference embeddings for all cells
embedding_mat <- t(reference$Z_corr)
rownames(embedding_mat) <- rownames(obs_df)

cat("Embedding extracted:", nrow(embedding_mat), "x", ncol(embedding_mat), "\\n")

# For expression, use original normalized data
# Symphony primarily provides corrected embeddings
corrected_mat <- expr_mat_t
'''

        data_saving = generate_data_saving_code(
            self.runner.temp_dir, prefix="corrected", save_embedding=True
        )

        return header + data_loading + symphony_code + data_saving

    def cleanup(self):
        """Clean up temporary files."""
        self.runner.cleanup()

    def __repr__(self) -> str:
        return f"SymphonyTeacher(n_pcs={self.n_pcs}, theta={self.theta})"

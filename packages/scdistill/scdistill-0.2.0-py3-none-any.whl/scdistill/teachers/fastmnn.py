"""fastMNN teacher for batch correction.

Uses the batchelor R package for mutual nearest neighbor batch correction.
"""

import numpy as np
import pandas as pd
from typing import Optional
from pathlib import Path

from .base import BaseTeacher, RScriptRunner


class FastMNNTeacher(BaseTeacher):
    """fastMNN batch correction teacher.

    Uses mutual nearest neighbors (MNN) for batch correction via the
    batchelor R package.

    Note: fastMNN produces small-scale embeddings, so needs_normalization=True.

    Parameters
    ----------
    k : int, default=20
        Number of nearest neighbors for MNN.
    d : int, default=50
        Number of PCA dimensions.
    rscript_path : str, default="Rscript"
        Path to Rscript executable.

    Examples
    --------
    >>> teacher = FastMNNTeacher()
    >>> Z_corrected = teacher.fit_transform(X_pca, batch_labels, adata=adata, batch_key="batch")
    """

    name = "fastMNN"
    needs_normalization = True  # fastMNN has small-scale embeddings

    def __init__(
        self,
        k: int = 20,
        d: int = 50,
        rscript_path: str = "Rscript",
    ):
        super().__init__()
        self.k = k
        self.d = d
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
        """Apply fastMNN batch correction.

        Parameters
        ----------
        X_pca : np.ndarray
            PCA embeddings (n_cells, n_pcs). Not used directly - fastMNN
            computes its own PCA internally.
        batch_labels : np.ndarray
            Batch labels (n_cells,).
        obs : pd.DataFrame, optional
            Cell metadata.
        verbose : bool
            Print progress.
        adata : AnnData
            Full AnnData object. Required for fastMNN.
        batch_key : str
            Key in adata.obs for batch labels.

        Returns
        -------
        Z_corrected : np.ndarray
            fastMNN-corrected embeddings.
        """
        if adata is None:
            raise ValueError(
                "fastMNN requires the full AnnData object. "
                "Pass adata=adata to fit_transform()."
            )

        if verbose:
            print(f"{self.name}: k={self.k}, d={self.d}")

        # Create temp directory
        self.runner.create_temp_dir("fastmnn_")

        try:
            # Save data for R
            expr_path = self.runner.temp_dir / "expression.csv"
            obs_path = self.runner.temp_dir / "obs.csv"

            X = adata.X
            if hasattr(X, "toarray"):
                X = X.toarray()
            expr_df = pd.DataFrame(X, index=adata.obs_names, columns=adata.var_names)
            expr_df.to_csv(expr_path)
            adata.obs.to_csv(obs_path)

            # Generate and run R script
            r_script = self._generate_r_script(
                expr_path=expr_path,
                obs_path=obs_path,
                batch_key=batch_key,
            )
            script_path = self.runner.temp_dir / "run_fastmnn.R"
            script_path.write_text(r_script)

            if verbose:
                print("  Running fastMNN via batchelor...")

            self.runner.run_r_script(script_path, verbose=verbose)

            # Load results
            embedding_df = pd.read_csv(
                self.runner.temp_dir / "embedding.csv", index_col=0
            )

            # Reorder to match original cell order
            if not all(idx in embedding_df.index for idx in adata.obs_names):
                embedding_df.index = adata.obs_names
            else:
                embedding_df = embedding_df.loc[adata.obs_names]

            self.Z_corrected = embedding_df.values
            self._is_fitted = True

            if verbose:
                print(f"  Corrected shape: {self.Z_corrected.shape}")
                norm = np.mean(np.linalg.norm(self.Z_corrected, axis=1))
                print(f"  Mean L2 norm: {norm:.4f} (small scale - normalization needed)")

            return self.Z_corrected

        finally:
            # Cleanup temp files
            self.runner.cleanup()

    def _generate_r_script(
        self,
        expr_path: Path,
        obs_path: Path,
        batch_key: str,
    ) -> str:
        """Generate R script for fastMNN.

        Parameters
        ----------
        expr_path : Path
            Path to expression matrix CSV.
        obs_path : Path
            Path to obs metadata CSV.
        batch_key : str
            Batch column name.

        Returns
        -------
        str
            R script content.
        """
        return f'''
suppressPackageStartupMessages({{
    library(batchelor)
    library(SingleCellExperiment)
}})

cat("Loading data...\\n")
expr <- read.csv("{expr_path}", row.names=1, check.names=FALSE)
obs <- read.csv("{obs_path}", row.names=1, stringsAsFactors=FALSE)

# Transpose: genes x cells
expr_t <- t(as.matrix(expr))

cat("Creating SingleCellExperiment...\\n")
sce <- SingleCellExperiment(assays=list(logcounts=expr_t))
colData(sce) <- DataFrame(obs)

# Get batch labels
batch_labels <- obs[["{batch_key}"]]
unique_batches <- unique(batch_labels)

cat("Running fastMNN on", length(unique_batches), "batches...\\n")

# Run fastMNN
mnn_result <- fastMNN(sce, batch=batch_labels, k={self.k}, d={self.d})

cat("Extracting results...\\n")
# Get MNN corrected embeddings
mnn_embedding <- reducedDim(mnn_result, "corrected")

# Ensure correct cell order (fastMNN preserves order)
rownames(mnn_embedding) <- rownames(obs)

cat("Saving results...\\n")
write.csv(mnn_embedding, "{self.runner.temp_dir}/embedding.csv", row.names=TRUE)

cat("fastMNN completed successfully\\n")
'''

    def cleanup(self):
        """Clean up temporary files."""
        self.runner.cleanup()

    def __repr__(self) -> str:
        return f"FastMNNTeacher(k={self.k}, d={self.d})"

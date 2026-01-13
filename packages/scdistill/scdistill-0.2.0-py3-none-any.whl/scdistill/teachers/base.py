"""Base class for teacher models with R script utilities.

This module provides:
- BaseTeacher: Abstract base class for batch correction teachers
- RScriptRunner: Helper class for executing R scripts
- Helper functions for R data I/O
"""

from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from typing import Optional, Dict
from pathlib import Path
import subprocess
import tempfile
import shutil
import anndata as ad


# =============================================================================
# R Script Utilities
# =============================================================================

class RScriptRunner:
    """Helper class for executing R scripts.

    Manages temporary directories, data I/O between Python and R,
    and R script execution.

    Parameters
    ----------
    rscript_path : str
        Path to Rscript executable. Default is "Rscript" (uses PATH).

    Examples
    --------
    >>> runner = RScriptRunner()
    >>> runner.create_temp_dir("my_method_")
    >>> data_paths = runner.save_anndata_for_r(adata, runner.temp_dir)
    >>> runner.run_r_script(script_path)
    >>> adata_result = runner.load_anndata_from_r(runner.temp_dir)
    >>> runner.cleanup()
    """

    def __init__(self, rscript_path: str = "Rscript"):
        """Initialize RScriptRunner.

        Parameters
        ----------
        rscript_path : str
            Path to Rscript executable. Use "Rscript" to find in PATH,
            or specify full path like "/usr/local/bin/Rscript".
        """
        self.rscript_path = rscript_path
        self.temp_dir: Optional[Path] = None

    def create_temp_dir(self, prefix: str = "r_wrapper_") -> Path:
        """Create a temporary directory.

        Parameters
        ----------
        prefix : str
            Prefix for the temp directory name.

        Returns
        -------
        Path
            Path to the created temp directory.
        """
        self.temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
        return self.temp_dir

    def cleanup(self):
        """Remove the temporary directory and all its contents."""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None

    def save_anndata_for_r(
        self,
        adata: ad.AnnData,
        output_dir: Path,
        prefix: str = "data"
    ) -> Dict[str, Path]:
        """Save AnnData for R processing.

        Saves expression matrix and metadata as CSV files.

        Parameters
        ----------
        adata : AnnData
            AnnData object to save.
        output_dir : Path
            Directory to save files.
        prefix : str
            Prefix for file names.

        Returns
        -------
        dict
            Dictionary with paths to saved files:
            {'expression': Path, 'obs': Path, 'var': Path}
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = {}

        # Save expression matrix as CSV
        expr_path = output_dir / f"{prefix}_expression.csv"
        X = adata.X
        if hasattr(X, "toarray"):
            X = X.toarray()
        expr_df = pd.DataFrame(
            X,
            index=adata.obs_names,
            columns=adata.var_names
        )
        expr_df.to_csv(expr_path)
        paths['expression'] = expr_path

        # Save metadata
        obs_path = output_dir / f"{prefix}_obs.csv"
        adata.obs.to_csv(obs_path)
        paths['obs'] = obs_path

        var_path = output_dir / f"{prefix}_var.csv"
        adata.var.to_csv(var_path)
        paths['var'] = var_path

        return paths

    def load_anndata_from_r(
        self,
        input_dir: Path,
        prefix: str = "corrected",
        original_adata: Optional[ad.AnnData] = None
    ) -> ad.AnnData:
        """Load AnnData from R output.

        Parameters
        ----------
        input_dir : Path
            Directory containing R output files.
        prefix : str
            Prefix for file names.
        original_adata : AnnData, optional
            Original AnnData for metadata reference.

        Returns
        -------
        AnnData
            Loaded AnnData object with corrected data.
        """
        input_dir = Path(input_dir)

        # Load expression matrix
        expr_path = input_dir / f"{prefix}_expression.csv"
        expr_df = pd.read_csv(expr_path, index_col=0)

        # Create AnnData object
        adata = ad.AnnData(X=expr_df.values)
        adata.obs_names = pd.Index(expr_df.index.astype(str))
        adata.var_names = pd.Index(expr_df.columns.astype(str))

        # Load metadata
        obs_path = input_dir / f"{prefix}_obs.csv"
        if obs_path.exists():
            adata.obs = pd.read_csv(obs_path, index_col=0)
        elif original_adata is not None:
            adata.obs = original_adata.obs.copy()

        var_path = input_dir / f"{prefix}_var.csv"
        if var_path.exists():
            adata.var = pd.read_csv(var_path, index_col=0)
        elif original_adata is not None:
            adata.var = original_adata.var.copy()

        # Load embedding if exists
        emb_path = input_dir / f"{prefix}_embedding.csv"
        if emb_path.exists():
            emb_df = pd.read_csv(emb_path, index_col=0)
            adata.obsm['X_emb'] = emb_df.values

        return adata

    def run_r_script(
        self,
        script_path: Path,
        timeout: int = 600,
        verbose: bool = True
    ) -> subprocess.CompletedProcess:
        """Execute an R script.

        Parameters
        ----------
        script_path : Path
            Path to the R script.
        timeout : int
            Timeout in seconds.
        verbose : bool
            Print stdout.

        Returns
        -------
        subprocess.CompletedProcess
            Result of script execution.

        Raises
        ------
        RuntimeError
            If script execution fails.
        """
        result = subprocess.run(
            [self.rscript_path, str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if verbose and result.stdout:
            print(result.stdout)

        if result.returncode != 0:
            error_msg = f"R script execution failed:\n{result.stderr}"
            if result.stdout:
                error_msg += f"\nStdout:\n{result.stdout}"
            raise RuntimeError(error_msg)

        return result


def generate_r_header(packages: list) -> str:
    """Generate R script header with package loading.

    Parameters
    ----------
    packages : list
        List of R packages to load.

    Returns
    -------
    str
        R code for loading packages.
    """
    lines = [
        "# Auto-generated R script",
        "suppressPackageStartupMessages({",
    ]
    for pkg in packages:
        lines.append(f"  library({pkg})")
    lines.append("})")
    lines.append("")
    return "\n".join(lines)


def generate_data_loading_code(
    expr_path: Path,
    obs_path: Path,
    var_path: Path
) -> str:
    """Generate R code for loading data from CSV files.

    Parameters
    ----------
    expr_path : Path
        Path to expression matrix CSV.
    obs_path : Path
        Path to obs metadata CSV.
    var_path : Path
        Path to var metadata CSV.

    Returns
    -------
    str
        R code for data loading.
    """
    return f'''
# Load data
cat("Loading data...\\n")
expr_mat <- as.matrix(read.csv("{expr_path}", row.names=1, check.names=FALSE))
obs_df <- read.csv("{obs_path}", row.names=1, stringsAsFactors=FALSE)
var_df <- read.csv("{var_path}", row.names=1, stringsAsFactors=FALSE)

# Transpose for R packages (genes × cells)
expr_mat_t <- t(expr_mat)

cat("Data loaded: ", nrow(expr_mat), " cells x ", ncol(expr_mat), " genes\\n")
'''


def generate_data_saving_code(
    output_dir: Path,
    prefix: str = "corrected",
    save_embedding: bool = True
) -> str:
    """Generate R code for saving corrected data.

    Parameters
    ----------
    output_dir : Path
        Output directory path.
    prefix : str
        Prefix for output file names.
    save_embedding : bool
        Whether to save embedding.

    Returns
    -------
    str
        R code for data saving.
    """
    code = f'''
# Save corrected data
cat("Saving corrected data...\\n")

# Save expression matrix (cells × genes)
corrected_expr <- t(as.matrix(corrected_mat))
write.csv(corrected_expr, "{output_dir}/{prefix}_expression.csv")

# Save metadata
write.csv(obs_df, "{output_dir}/{prefix}_obs.csv")
write.csv(var_df, "{output_dir}/{prefix}_var.csv")
'''

    if save_embedding:
        code += f'''
# Save embedding if available
if (exists("embedding_mat")) {{
  write.csv(embedding_mat, "{output_dir}/{prefix}_embedding.csv")
}}
'''

    code += '\ncat("Data saved successfully\\n")\n'
    return code


# =============================================================================
# Base Teacher Class
# =============================================================================

class BaseTeacher(ABC):
    """Abstract base class for batch correction teachers.

    Teachers are batch correction methods that operate in PCA/latent space.
    They produce batch-corrected embeddings that serve as teaching signals
    for the MLP student in the distillation framework.

    Subclasses must implement:
    - fit_transform(): Apply batch correction and return corrected embeddings

    Attributes
    ----------
    name : str
        Name of the teacher method.
    needs_normalization : bool
        Whether the teacher's embeddings need normalization before distillation.
        Methods with small-scale embeddings (fastMNN, LIGER) need normalization.
    Z_corrected : np.ndarray
        Corrected embeddings after fit_transform() is called.
    """

    name: str = "BaseTeacher"
    needs_normalization: bool = False  # Default: no normalization needed

    def __init__(self):
        self.Z_corrected = None
        self._is_fitted = False

    @abstractmethod
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
        """Apply batch correction to PCA embeddings.

        Parameters
        ----------
        X_pca : np.ndarray
            PCA embeddings of shape (n_cells, n_pcs).
        batch_labels : np.ndarray
            Batch labels of shape (n_cells,).
        obs : pd.DataFrame, optional
            Cell metadata (for methods that use covariates).
        verbose : bool, default=True
            Print progress.
        adata : AnnData, optional
            Full AnnData object (required for R-based teachers).
        batch_key : str, default="batch"
            Key in adata.obs for batch labels.
        **kwargs
            Additional keyword arguments for specific teachers.

        Returns
        -------
        Z_corrected : np.ndarray
            Batch-corrected embeddings of shape (n_cells, n_pcs).
        """
        pass

    def get_corrected_embeddings(self) -> np.ndarray:
        """Get the corrected embeddings from last fit_transform call."""
        if not self._is_fitted:
            raise ValueError(f"{self.name} has not been fitted. Call fit_transform() first.")
        return self.Z_corrected.copy()

    def __repr__(self) -> str:
        return f"{self.name}()"

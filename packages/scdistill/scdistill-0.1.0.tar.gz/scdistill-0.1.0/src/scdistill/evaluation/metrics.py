"""Wrapper functions for scib-metrics with DistillBenchmarker.

This module provides:
1. DistillBenchmarker: scIB-compatible benchmarker with covariate conservation
2. Convenient wrappers around scib-metrics functions

DistillBenchmarker Usage
------------------------
>>> from scdistill.evaluation import DistillBenchmarker
>>>
>>> bm = DistillBenchmarker(
...     adata,
...     batch_key="batch",
...     label_key="celltype",
...     embedding_obsm_keys=["X_pca", "X_emb"],
...     covariate_key="condition",  # scDistill extension
... )
>>> bm.benchmark()
>>> results = bm.get_results()
>>>
>>> # Access underlying scIB Benchmarker
>>> scib_bm = bm.scib
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, Union, List
from anndata import AnnData

# scib-metrics imports
try:
    import scib_metrics
    from scib_metrics import (
        silhouette_batch,
        silhouette_label,
        nmi_ari_cluster_labels_kmeans,
        ilisi_knn,
        clisi_knn,
        pcr_comparison,
        isolated_labels,
        graph_connectivity,
        kbet_per_label,
    )
    from scib_metrics.benchmark import Benchmarker, BioConservation, BatchCorrection
    SCIB_AVAILABLE = True
except ImportError:
    SCIB_AVAILABLE = False
    Benchmarker = None
    BioConservation = None
    BatchCorrection = None


def check_scib_available():
    """Check if scib-metrics is available."""
    if not SCIB_AVAILABLE:
        raise ImportError(
            "scib-metrics is required for this function. "
            "Install with: pip install scib-metrics"
        )


# =============================================================================
# DistillBenchmarker
# =============================================================================

class DistillBenchmarker:
    """Benchmarker for scDistill with scIB metrics + covariate conservation.

    Wraps scib-metrics Benchmarker and extends it with covariate conservation
    metrics for evaluating batch correction methods that preserve biological
    covariates.

    Parameters
    ----------
    adata : AnnData
        Annotated data matrix.
    batch_key : str
        Column in adata.obs with batch labels.
    label_key : str
        Column in adata.obs with cell type labels.
    embedding_obsm_keys : list of str
        Keys in adata.obsm for embeddings to evaluate.
    covariate_key : str, optional
        Column in adata.obs with covariate labels (e.g., condition, treatment).
        If provided, covariate conservation metrics are computed.
    bio_conservation_metrics : BioConservation, optional
        scIB BioConservation configuration. Uses default if None.
    batch_correction_metrics : BatchCorrection, optional
        scIB BatchCorrection configuration. Uses default if None.
    n_jobs : int, default=-1
        Number of parallel jobs.

    Attributes
    ----------
    scib : Benchmarker
        Underlying scib-metrics Benchmarker object.

    Examples
    --------
    >>> bm = DistillBenchmarker(
    ...     adata,
    ...     batch_key="batch",
    ...     label_key="celltype",
    ...     embedding_obsm_keys=["X_pca", "X_corrected"],
    ...     covariate_key="condition",
    ... )
    >>> bm.benchmark()
    >>> results = bm.get_results()
    >>>
    >>> # Access scIB Benchmarker directly
    >>> scib_results = bm.scib.get_results()
    """

    def __init__(
        self,
        adata: AnnData,
        batch_key: str,
        label_key: str,
        embedding_obsm_keys: List[str],
        covariate_key: Optional[str] = None,
        bio_conservation_metrics: Optional["BioConservation"] = None,
        batch_correction_metrics: Optional["BatchCorrection"] = None,
        n_jobs: int = -1,
    ):
        check_scib_available()

        self.adata = adata
        self.batch_key = batch_key
        self.label_key = label_key
        self.embedding_obsm_keys = embedding_obsm_keys
        self.covariate_key = covariate_key
        self.n_jobs = n_jobs

        # Create underlying scIB Benchmarker
        self._benchmarker = Benchmarker(
            adata,
            batch_key=batch_key,
            label_key=label_key,
            embedding_obsm_keys=embedding_obsm_keys,
            bio_conservation_metrics=bio_conservation_metrics or BioConservation(),
            batch_correction_metrics=batch_correction_metrics or BatchCorrection(),
            n_jobs=n_jobs,
        )

        self._covariate_results: Optional[pd.DataFrame] = None
        self._is_benchmarked = False

    @property
    def scib(self) -> "Benchmarker":
        """Access the underlying scib-metrics Benchmarker object."""
        return self._benchmarker

    def benchmark(self) -> None:
        """Run benchmarking on all embeddings.

        Computes:
        1. scIB batch correction metrics
        2. scIB bio conservation metrics
        3. Covariate conservation metrics (if covariate_key provided)
        """
        # Run scIB benchmark
        self._benchmarker.benchmark()

        # Compute covariate conservation metrics if requested
        if self.covariate_key is not None:
            self._compute_covariate_metrics()

        self._is_benchmarked = True

    def _compute_covariate_metrics(self) -> None:
        """Compute covariate conservation metrics for all embeddings."""
        from .covariate import compute_condition_asw

        results = {}
        covariate_labels = self.adata.obs[self.covariate_key].values

        for key in self.embedding_obsm_keys:
            if key not in self.adata.obsm:
                continue

            embedding = np.asarray(self.adata.obsm[key])

            # Compute condition ASW
            try:
                condition_asw = compute_condition_asw(
                    embedding, covariate_labels, rescale=True
                )
            except Exception:
                condition_asw = np.nan

            results[key] = {"Condition ASW": condition_asw}

        self._covariate_results = pd.DataFrame(results).T

    def get_results(
        self,
        min_max_scale: bool = False,
        include_covariate: bool = True,
    ) -> pd.DataFrame:
        """Get benchmark results as DataFrame.

        Parameters
        ----------
        min_max_scale : bool, default=False
            Scale metrics to [0, 1] range.
        include_covariate : bool, default=True
            Include covariate conservation metrics (if available).

        Returns
        -------
        results : pd.DataFrame
            Results with embeddings as rows and metrics as columns.
            Includes 'Total' column with overall score.
        """
        if not self._is_benchmarked:
            raise ValueError("Call benchmark() first")

        # Get scIB results
        scib_results = self._benchmarker.get_results(min_max_scale=min_max_scale)

        # Merge with covariate results if available
        if include_covariate and self._covariate_results is not None:
            # Add covariate metrics
            for col in self._covariate_results.columns:
                scib_results[col] = self._covariate_results[col]

            # Recalculate total score including covariate metrics
            # Using 0.4 batch + 0.4 bio + 0.2 covariate weighting
            numeric_cols = scib_results.select_dtypes(include=[np.number]).columns
            if "Total" in scib_results.columns:
                # Get batch and bio scores
                batch_score = scib_results.get("Batch correction", np.nan)
                bio_score = scib_results.get("Bio conservation", np.nan)
                cov_score = self._covariate_results.mean(axis=1)

                # Recalculate with covariate
                scib_results["Covariate conservation"] = cov_score
                scib_results["Total"] = (
                    0.4 * batch_score.fillna(0)
                    + 0.4 * bio_score.fillna(0)
                    + 0.2 * cov_score.fillna(0)
                )

        return scib_results

    def plot_results(self, **kwargs) -> None:
        """Plot benchmark results using scIB's plotting.

        Parameters
        ----------
        **kwargs
            Passed to scIB Benchmarker.plot_results().
        """
        if not self._is_benchmarked:
            raise ValueError("Call benchmark() first")
        self._benchmarker.plot_results(**kwargs)

    def __repr__(self) -> str:
        return (
            f"DistillBenchmarker("
            f"batch_key='{self.batch_key}', "
            f"label_key='{self.label_key}', "
            f"covariate_key={repr(self.covariate_key)}, "
            f"embeddings={self.embedding_obsm_keys})"
        )


def _to_numpy_labels(labels: np.ndarray) -> np.ndarray:
    """Convert labels to numpy array of integers for scib-metrics."""
    if isinstance(labels, pd.Series):
        labels = labels.values
    if isinstance(labels, pd.Categorical):
        labels = labels.codes
    if labels.dtype == object or labels.dtype.kind == 'U':
        from sklearn.preprocessing import LabelEncoder
        labels = LabelEncoder().fit_transform(labels)
    return labels


# =============================================================================
# Batch Correction Metrics
# =============================================================================

def compute_silhouette_batch(
    embedding: np.ndarray,
    batch_labels: np.ndarray,
    celltype_labels: Optional[np.ndarray] = None,
    rescale: bool = True,
) -> float:
    """Compute batch silhouette score (lower is better).

    Measures how well batches are mixed in embedding space.
    Lower values indicate better batch mixing.

    Parameters
    ----------
    embedding : np.ndarray
        Embedding matrix, shape (n_cells, n_dims).
    batch_labels : np.ndarray
        Batch labels for each cell.
    celltype_labels : np.ndarray, optional
        Cell type labels for per-label computation. If None, uses batch as labels.
    rescale : bool, default=True
        Rescale to [0, 1].

    Returns
    -------
    score : float
        Silhouette batch score (0-1, lower is better).
    """
    check_scib_available()
    batch = _to_numpy_labels(batch_labels)
    if celltype_labels is not None:
        labels = _to_numpy_labels(celltype_labels)
    else:
        labels = batch
    return silhouette_batch(embedding, labels, batch, rescale=rescale)


def compute_ilisi(
    embedding: np.ndarray,
    batch_labels: np.ndarray,
    perplexity: float = 30.0,
) -> float:
    """Compute integration LISI (higher is better).

    Measures local batch diversity around each cell.
    Higher values indicate better batch integration.

    Parameters
    ----------
    embedding : np.ndarray
        Embedding matrix, shape (n_cells, n_dims).
    batch_labels : np.ndarray
        Batch labels for each cell.
    perplexity : float, default=30.0
        Perplexity for kNN graph.

    Returns
    -------
    score : float
        iLISI score (0-1, higher is better).
    """
    check_scib_available()
    from scib_metrics.nearest_neighbors import NeighborsResults, pynndescent

    # Build kNN graph
    k = min(int(3 * perplexity), embedding.shape[0] - 1)
    neighbors = pynndescent(embedding, n_neighbors=k)

    batch = _to_numpy_labels(batch_labels)
    return ilisi_knn(neighbors, batch, perplexity=perplexity)


def compute_kbet(
    embedding: np.ndarray,
    batch_labels: np.ndarray,
    celltype_labels: np.ndarray,
) -> float:
    """Compute kBET acceptance rate (higher is better).

    Measures local batch label distribution.
    Higher values indicate better batch mixing.

    Parameters
    ----------
    embedding : np.ndarray
        Embedding matrix, shape (n_cells, n_dims).
    batch_labels : np.ndarray
        Batch labels for each cell.
    celltype_labels : np.ndarray
        Cell type labels for each cell.

    Returns
    -------
    score : float
        kBET acceptance rate (0-1, higher is better).
    """
    check_scib_available()
    from scib_metrics.nearest_neighbors import pynndescent

    # Build kNN graph
    k = min(50, embedding.shape[0] - 1)
    neighbors = pynndescent(embedding, n_neighbors=k)

    batch = _to_numpy_labels(batch_labels)
    celltype = _to_numpy_labels(celltype_labels)
    return kbet_per_label(neighbors, batch, celltype)


def compute_graph_connectivity(
    embedding: np.ndarray,
    celltype_labels: np.ndarray,
) -> float:
    """Compute graph connectivity (higher is better).

    Measures whether cells of the same type form connected components.
    Higher values indicate better preservation of cell type structure.

    Parameters
    ----------
    embedding : np.ndarray
        Embedding matrix, shape (n_cells, n_dims).
    celltype_labels : np.ndarray
        Cell type labels for each cell.

    Returns
    -------
    score : float
        Graph connectivity score (0-1, higher is better).
    """
    check_scib_available()
    from scib_metrics.nearest_neighbors import pynndescent

    # Build kNN graph
    k = min(15, embedding.shape[0] - 1)
    neighbors = pynndescent(embedding, n_neighbors=k)

    labels = _to_numpy_labels(celltype_labels)
    return graph_connectivity(neighbors, labels)


def compute_pcr(
    embedding: np.ndarray,
    X_original: np.ndarray,
    batch_labels: np.ndarray,
) -> float:
    """Compute principal component regression (lower is better).

    Measures batch effect captured by principal components.
    Lower values indicate less batch effect in the embedding.

    Parameters
    ----------
    embedding : np.ndarray
        Corrected embedding matrix, shape (n_cells, n_dims).
    X_original : np.ndarray
        Original expression or PCA matrix, shape (n_cells, n_features).
    batch_labels : np.ndarray
        Batch labels for each cell.

    Returns
    -------
    score : float
        PCR score (0-1, lower is better).
    """
    check_scib_available()
    covariate = _to_numpy_labels(batch_labels)
    return pcr_comparison(X_original, embedding, covariate)


# =============================================================================
# Biological Conservation Metrics
# =============================================================================

def compute_nmi_ari(
    embedding: np.ndarray,
    celltype_labels: np.ndarray,
) -> Dict[str, float]:
    """Compute NMI and ARI using k-means clustering (higher is better).

    Measures how well the embedding preserves cell type structure.

    Parameters
    ----------
    embedding : np.ndarray
        Embedding matrix, shape (n_cells, n_dims).
    celltype_labels : np.ndarray
        Cell type labels for each cell.

    Returns
    -------
    scores : dict
        Dictionary with 'nmi' and 'ari' keys.
    """
    check_scib_available()
    labels = _to_numpy_labels(celltype_labels)

    # scib-metrics returns a dict with 'nmi' and 'ari' keys
    result = nmi_ari_cluster_labels_kmeans(embedding, labels)
    return {'nmi': result['nmi'], 'ari': result['ari']}


def compute_silhouette_label(
    embedding: np.ndarray,
    celltype_labels: np.ndarray,
    rescale: bool = True,
) -> float:
    """Compute cell type silhouette score (higher is better).

    Measures how well cell types are separated in embedding space.
    Higher values indicate better cell type separation.

    Parameters
    ----------
    embedding : np.ndarray
        Embedding matrix, shape (n_cells, n_dims).
    celltype_labels : np.ndarray
        Cell type labels for each cell.
    rescale : bool, default=True
        Rescale to [0, 1].

    Returns
    -------
    score : float
        Silhouette label score (0-1, higher is better).
    """
    check_scib_available()
    labels = _to_numpy_labels(celltype_labels)
    return silhouette_label(embedding, labels, rescale=rescale)


def compute_clisi(
    embedding: np.ndarray,
    celltype_labels: np.ndarray,
    perplexity: float = 30.0,
) -> float:
    """Compute cell type LISI (lower is better for cell type purity).

    Measures local cell type homogeneity around each cell.
    Lower values indicate better preservation of cell type neighborhoods.

    Parameters
    ----------
    embedding : np.ndarray
        Embedding matrix, shape (n_cells, n_dims).
    celltype_labels : np.ndarray
        Cell type labels for each cell.
    perplexity : float, default=30.0
        Perplexity for kNN graph.

    Returns
    -------
    score : float
        cLISI score (0-1, lower is better).
    """
    check_scib_available()
    from scib_metrics.nearest_neighbors import pynndescent

    # Build kNN graph
    k = min(int(3 * perplexity), embedding.shape[0] - 1)
    neighbors = pynndescent(embedding, n_neighbors=k)

    labels = _to_numpy_labels(celltype_labels)
    return clisi_knn(neighbors, labels, perplexity=perplexity)


def compute_isolated_labels(
    embedding: np.ndarray,
    celltype_labels: np.ndarray,
    batch_labels: np.ndarray,
    rescale: bool = True,
) -> float:
    """Compute isolated labels score (higher is better).

    Measures ability to identify cell types present in only one batch.

    Parameters
    ----------
    embedding : np.ndarray
        Embedding matrix, shape (n_cells, n_dims).
    celltype_labels : np.ndarray
        Cell type labels for each cell.
    batch_labels : np.ndarray
        Batch labels for each cell.
    rescale : bool, default=True
        Rescale to [0, 1].

    Returns
    -------
    score : float
        Isolated labels score (0-1, higher is better).
    """
    check_scib_available()
    labels = _to_numpy_labels(celltype_labels)
    batch = _to_numpy_labels(batch_labels)
    return isolated_labels(embedding, labels, batch, rescale=rescale)


# =============================================================================
# Combined Metrics
# =============================================================================

def compute_all_metrics(
    embedding: np.ndarray,
    batch_labels: np.ndarray,
    celltype_labels: np.ndarray,
    X_original: Optional[np.ndarray] = None,
    metrics: Optional[list] = None,
) -> Dict[str, float]:
    """Compute all batch correction and bio conservation metrics.

    Parameters
    ----------
    embedding : np.ndarray
        Embedding matrix, shape (n_cells, n_dims).
    batch_labels : np.ndarray
        Batch labels for each cell.
    celltype_labels : np.ndarray
        Cell type labels for each cell.
    X_original : np.ndarray, optional
        Original expression for PCR computation.
    metrics : list, optional
        List of metrics to compute. If None, compute all.

    Returns
    -------
    results : dict
        Dictionary with metric names and values.
    """
    check_scib_available()

    all_metrics = {
        # Batch correction
        'silhouette_batch': lambda: compute_silhouette_batch(embedding, batch_labels),
        'ilisi': lambda: compute_ilisi(embedding, batch_labels),
        'kbet': lambda: compute_kbet(embedding, batch_labels, celltype_labels),
        'graph_connectivity': lambda: compute_graph_connectivity(embedding, celltype_labels),
        # Bio conservation
        'silhouette_label': lambda: compute_silhouette_label(embedding, celltype_labels),
        'clisi': lambda: compute_clisi(embedding, celltype_labels),
        'isolated_labels': lambda: compute_isolated_labels(embedding, celltype_labels, batch_labels),
    }

    # Add PCR if original expression is provided
    if X_original is not None:
        all_metrics['pcr'] = lambda: compute_pcr(embedding, X_original, batch_labels)

    if metrics is None:
        metrics = list(all_metrics.keys()) + ['nmi', 'ari']

    results = {}

    for name in metrics:
        if name in ['nmi', 'ari']:
            if 'nmi' not in results and 'ari' not in results:
                nmi_ari = compute_nmi_ari(embedding, celltype_labels)
                results['nmi'] = nmi_ari['nmi']
                results['ari'] = nmi_ari['ari']
        elif name in all_metrics:
            try:
                results[name] = all_metrics[name]()
            except Exception as e:
                print(f"Warning: Failed to compute {name}: {e}")
                results[name] = np.nan

    return results

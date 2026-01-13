"""Representative cell subsampling for efficient training.

Implements stratified geometric sketching on Harmony latent space
to select K representative cells for MLP training.

Usage:
    from scdistill.subsampling import select_representative_cells

    indices = select_representative_cells(
        Z_harmony=Z_harmony,
        obs=adata.obs,
        ratio=0.1,  # 10% of cells
        batch_key="batch",
        celltype_key="cell_type",
        condition_key="age",
    )
"""

import numpy as np
import pandas as pd
from typing import Optional
from scipy.spatial.distance import cdist


def select_representative_cells(
    Z_harmony: np.ndarray,
    obs: pd.DataFrame,
    n_cells: Optional[int] = None,
    ratio: float = 0.1,
    batch_key: str = "batch",
    celltype_key: str = "cell_type",
    condition_key: Optional[str] = None,
    condition_bins: int = 6,
    method: str = "geosketch",
    random_state: int = 42,
    min_cells_per_stratum: int = 2,
) -> np.ndarray:
    """Stratified representative cell selection on Harmony latent space.

    Parameters
    ----------
    Z_harmony : np.ndarray
        Harmony-corrected latent representation (N, latent_dim).
    obs : pd.DataFrame
        Cell metadata with batch, celltype, and optionally condition columns.
    n_cells : int, optional
        Number of cells to select (K). If None, uses ratio.
    ratio : float, default=0.1
        Fraction of cells to select if n_cells is None.
    batch_key : str, default="batch"
        Column name in obs for batch labels.
    celltype_key : str, default="cell_type"
        Column name in obs for cell type labels.
    condition_key : str, optional
        Column name in obs for continuous covariate (e.g., "age").
        If None, stratification is by (batch, celltype) only.
    condition_bins : int, default=6
        Number of bins for discretizing continuous condition.
    method : str, default="geosketch"
        Sampling method: "geosketch" or "kmeans_medoid".
    random_state : int, default=42
        Random seed for reproducibility.
    min_cells_per_stratum : int, default=2
        Minimum cells required per stratum.

    Returns
    -------
    indices : np.ndarray
        Indices of selected representative cells (shape: K,).

    Raises
    ------
    ValueError
        If required columns are missing or strata have insufficient cells.
    ImportError
        If geosketch is not installed.

    Notes
    -----
    Algorithm:
    1. Compute strata from (batch, celltype, condition_bin)
    2. Allocate quota proportionally to stratum size
    3. Apply geosketch (farthest-point sampling) within each stratum
    4. Combine indices from all strata

    NO FALLBACK: If geosketch fails, an error is raised.
    """
    N = Z_harmony.shape[0]

    # Validate inputs
    if batch_key not in obs.columns:
        raise ValueError(f"batch_key '{batch_key}' not in obs columns: {list(obs.columns)}")
    if celltype_key not in obs.columns:
        raise ValueError(f"celltype_key '{celltype_key}' not in obs columns: {list(obs.columns)}")
    if condition_key is not None and condition_key not in obs.columns:
        raise ValueError(f"condition_key '{condition_key}' not in obs columns: {list(obs.columns)}")

    # Compute target K
    if n_cells is None:
        K = max(int(N * ratio), min_cells_per_stratum * 10)
    else:
        K = n_cells
    K = min(K, N)  # Cannot exceed total cells

    # Compute strata
    strata, stratum_names = _compute_strata(
        obs=obs,
        batch_key=batch_key,
        celltype_key=celltype_key,
        condition_key=condition_key,
        condition_bins=condition_bins,
    )

    unique_strata = np.unique(strata)
    n_strata = len(unique_strata)

    # Allocate quota per stratum (proportional to size)
    stratum_sizes = np.array([np.sum(strata == s) for s in unique_strata])
    quotas = np.round(K * stratum_sizes / N).astype(int)

    # Ensure minimum quota and adjust total
    quotas = np.maximum(quotas, 1)

    # Check strata have enough cells
    for s, size, quota in zip(unique_strata, stratum_sizes, quotas):
        if size < min_cells_per_stratum:
            raise ValueError(
                f"Stratum '{stratum_names[s]}' has only {size} cells, "
                f"less than minimum {min_cells_per_stratum}. "
                "Consider reducing stratification or increasing data."
            )
        # Adjust quota if stratum is too small
        quotas[unique_strata == s] = min(quota, size)

    # Adjust quotas to sum to K
    current_total = quotas.sum()
    if current_total < K:
        # Add to largest strata
        diff = K - current_total
        order = np.argsort(-stratum_sizes)
        for i in range(diff):
            idx = order[i % n_strata]
            if quotas[idx] < stratum_sizes[idx]:
                quotas[idx] += 1
    elif current_total > K:
        # Remove from largest strata
        diff = current_total - K
        order = np.argsort(-stratum_sizes)
        for i in range(diff):
            idx = order[i % n_strata]
            if quotas[idx] > 1:
                quotas[idx] -= 1

    # Select representatives per stratum
    all_indices = []
    np.random.seed(random_state)

    for s, quota in zip(unique_strata, quotas):
        stratum_mask = strata == s
        stratum_indices = np.where(stratum_mask)[0]
        Z_stratum = Z_harmony[stratum_mask]

        if quota >= len(stratum_indices):
            # Take all cells from this stratum
            selected_local = np.arange(len(stratum_indices))
        elif method == "geosketch":
            selected_local = _geosketch_stratum(
                Z_stratum, quota, random_state + s
            )
        elif method == "kmeans_medoid":
            selected_local = _kmeans_medoid_stratum(
                Z_stratum, quota, random_state + s
            )
        else:
            raise ValueError(f"Unknown method: {method}. Use 'geosketch' or 'kmeans_medoid'.")

        # Convert local indices to global
        selected_global = stratum_indices[selected_local]
        all_indices.extend(selected_global)

    return np.array(all_indices, dtype=int)


def _compute_strata(
    obs: pd.DataFrame,
    batch_key: str,
    celltype_key: str,
    condition_key: Optional[str],
    condition_bins: int,
) -> tuple:
    """Compute stratum IDs for (batch, celltype, condition_bin).

    Returns
    -------
    strata : np.ndarray
        Integer stratum ID for each cell.
    stratum_names : dict
        Mapping from stratum ID to human-readable name.
    """
    # Get batch and celltype as categorical codes
    batch_cat = pd.Categorical(obs[batch_key])
    celltype_cat = pd.Categorical(obs[celltype_key])

    batch_codes = batch_cat.codes
    celltype_codes = celltype_cat.codes

    n_batches = len(batch_cat.categories)
    n_celltypes = len(celltype_cat.categories)

    if condition_key is not None:
        # Bin continuous condition
        condition_series = obs[condition_key]

        # Check if numeric (handle pandas Categorical dtype properly)
        is_numeric = pd.api.types.is_numeric_dtype(condition_series)

        if is_numeric:
            # Numeric: use quantile-based binning
            condition_values = condition_series.values
            non_nan_values = condition_values[~np.isnan(condition_values)]
            condition_bins_edges = np.quantile(
                non_nan_values,
                np.linspace(0, 1, condition_bins + 1)
            )
            condition_bin_codes = np.digitize(condition_values, condition_bins_edges[1:-1])
        else:
            # Categorical: treat as is
            condition_cat = pd.Categorical(condition_series)
            condition_bin_codes = condition_cat.codes
            condition_bins = len(condition_cat.categories)

        # Compute combined stratum ID
        strata = (
            batch_codes * (n_celltypes * condition_bins) +
            celltype_codes * condition_bins +
            condition_bin_codes
        )
    else:
        # No condition: just batch x celltype
        strata = batch_codes * n_celltypes + celltype_codes
        condition_bins = 1

    # Create stratum names for debugging
    stratum_names = {}
    for s in np.unique(strata):
        if condition_key is not None:
            b = s // (n_celltypes * condition_bins)
            ct = (s % (n_celltypes * condition_bins)) // condition_bins
            cond = s % condition_bins
            name = f"{batch_cat.categories[b]}_{celltype_cat.categories[ct]}_bin{cond}"
        else:
            b = s // n_celltypes
            ct = s % n_celltypes
            name = f"{batch_cat.categories[b]}_{celltype_cat.categories[ct]}"
        stratum_names[s] = name

    return strata, stratum_names


def _geosketch_stratum(
    Z: np.ndarray,
    n_select: int,
    random_state: int,
) -> np.ndarray:
    """Apply geosketch (farthest-point sampling) within a stratum.

    Parameters
    ----------
    Z : np.ndarray
        Points to sample from (n_points, n_dims).
    n_select : int
        Number of points to select.
    random_state : int
        Random seed.

    Returns
    -------
    indices : np.ndarray
        Local indices of selected points.
    """
    try:
        from geosketch import gs
    except ImportError:
        raise ImportError(
            "geosketch is required for geometric sketching. "
            "Install with: pip install geosketch"
        )

    if n_select >= len(Z):
        return np.arange(len(Z))

    # geosketch returns indices
    indices = gs(Z, n_select, seed=random_state)
    return np.array(indices, dtype=int)


def _kmeans_medoid_stratum(
    Z: np.ndarray,
    n_select: int,
    random_state: int,
) -> np.ndarray:
    """Apply k-means clustering and select medoids.

    Parameters
    ----------
    Z : np.ndarray
        Points to sample from (n_points, n_dims).
    n_select : int
        Number of points to select (= number of clusters).
    random_state : int
        Random seed.

    Returns
    -------
    indices : np.ndarray
        Local indices of medoid points.
    """
    from sklearn.cluster import KMeans

    if n_select >= len(Z):
        return np.arange(len(Z))

    # K-means clustering
    kmeans = KMeans(n_clusters=n_select, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(Z)
    centers = kmeans.cluster_centers_

    # Find medoid (closest real point) for each cluster
    medoid_indices = []
    for k in range(n_select):
        cluster_mask = labels == k
        cluster_indices = np.where(cluster_mask)[0]

        if len(cluster_indices) == 0:
            continue

        cluster_points = Z[cluster_mask]
        distances = cdist(cluster_points, centers[k:k+1], metric='euclidean').ravel()
        medoid_local = np.argmin(distances)
        medoid_indices.append(cluster_indices[medoid_local])

    return np.array(medoid_indices, dtype=int)

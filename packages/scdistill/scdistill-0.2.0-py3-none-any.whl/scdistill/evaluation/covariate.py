"""Covariate Conservation metrics for scDistill.

This module provides metrics to evaluate how well biological covariates
(e.g., treatment conditions, age, disease state) are preserved after
batch correction.

Metrics:
- Embedding-level: Condition ASW
- Expression-level: Variance Preservation, DEG Overlap, Effect Correlation
"""

import numpy as np
import pandas as pd
from typing import Optional, Dict, List, Union, Tuple
from dataclasses import dataclass, field
from scipy import stats
from sklearn.metrics import silhouette_score


@dataclass
class CovariateConservation:
    """Configuration for covariate conservation metrics.

    Parameters
    ----------
    condition_asw : bool, default=True
        Compute condition ASW in embedding space.
    variance_preservation : bool, default=True
        Compute variance preservation ratio in expression space.
    deg_overlap : bool, default=True
        Compute DEG overlap (F1 score) in expression space.
    effect_correlation : bool, default=True
        Compute effect size correlation in expression space.
    """
    condition_asw: bool = True
    variance_preservation: bool = True
    deg_overlap: bool = True
    effect_correlation: bool = True


# =============================================================================
# Embedding-level Metrics
# =============================================================================

def compute_condition_asw(
    embedding: np.ndarray,
    condition_labels: np.ndarray,
    rescale: bool = True,
) -> float:
    """Compute condition ASW (Average Silhouette Width) in embedding space.

    Measures how well conditions are separated in the embedding space.
    Higher values indicate better condition separation (good for preserving
    biological signal from covariates).

    Parameters
    ----------
    embedding : np.ndarray
        Embedding matrix, shape (n_cells, n_dims).
    condition_labels : np.ndarray
        Condition labels for each cell.
    rescale : bool, default=True
        Rescale score from [-1, 1] to [0, 1].

    Returns
    -------
    score : float
        Condition ASW score. If rescale=True, range is [0, 1] (higher is better).
        If rescale=False, range is [-1, 1].

    Notes
    -----
    Unlike batch ASW (where lower is better because we want batch mixing),
    condition ASW should be HIGH because we want conditions to remain
    distinguishable after batch correction.
    """
    # Filter out NaN/None labels
    valid_mask = pd.notna(condition_labels)
    if not valid_mask.all():
        embedding = embedding[valid_mask]
        condition_labels = condition_labels[valid_mask]

    # Need at least 2 conditions
    unique_conditions = np.unique(condition_labels)
    if len(unique_conditions) < 2:
        return np.nan

    # Compute silhouette score
    score = silhouette_score(embedding, condition_labels)

    if rescale:
        # Rescale from [-1, 1] to [0, 1]
        score = (score + 1) / 2

    return score


# =============================================================================
# Expression-level Metrics
# =============================================================================

def compute_variance_preservation(
    X_original: np.ndarray,
    X_corrected: np.ndarray,
    condition_labels: np.ndarray,
    top_n_genes: int = 100,
) -> float:
    """Compute variance preservation ratio between conditions.

    Measures how much of the original condition-related variance is
    preserved after batch correction.

    Parameters
    ----------
    X_original : np.ndarray
        Original expression matrix, shape (n_cells, n_genes).
    X_corrected : np.ndarray
        Corrected expression matrix, shape (n_cells, n_genes).
    condition_labels : np.ndarray
        Condition labels for each cell.
    top_n_genes : int, default=100
        Number of top variable genes to consider.

    Returns
    -------
    ratio : float
        Variance preservation ratio (0-1+). Values close to 1 indicate
        good preservation. Values > 1 indicate amplification.
        Perfect preservation = 1.0 (100%).

    Notes
    -----
    Computed as ratio of between-condition variance:
    ratio = var_corrected / var_original

    We focus on genes that show high between-condition variance in the
    original data, as these are most informative for condition effects.
    """
    unique_conditions = np.unique(condition_labels)
    if len(unique_conditions) < 2:
        return np.nan

    # Compute condition means for original data
    means_original = np.array([
        X_original[condition_labels == c].mean(axis=0)
        for c in unique_conditions
    ])

    # Between-condition variance for each gene (original)
    var_between_original = np.var(means_original, axis=0)

    # Select top variable genes
    top_genes = np.argsort(var_between_original)[-top_n_genes:]

    # Compute condition means for corrected data
    means_corrected = np.array([
        X_corrected[condition_labels == c].mean(axis=0)
        for c in unique_conditions
    ])

    # Between-condition variance for selected genes
    var_original_sum = var_between_original[top_genes].sum()
    var_corrected_sum = np.var(means_corrected, axis=0)[top_genes].sum()

    # Avoid division by zero
    if var_original_sum < 1e-10:
        return np.nan

    ratio = var_corrected_sum / var_original_sum

    return ratio


def compute_variance_preservation_per_celltype(
    X_original: np.ndarray,
    X_corrected: np.ndarray,
    condition_labels: np.ndarray,
    celltype_labels: np.ndarray,
    top_n_genes: int = 100,
    min_cells_per_condition: int = 10,
) -> Dict[str, Dict[str, float]]:
    """Compute variance preservation ratio for each cell type.

    Parameters
    ----------
    X_original : np.ndarray
        Original expression matrix, shape (n_cells, n_genes).
    X_corrected : np.ndarray
        Corrected expression matrix, shape (n_cells, n_genes).
    condition_labels : np.ndarray
        Condition labels for each cell.
    celltype_labels : np.ndarray
        Cell type labels for each cell.
    top_n_genes : int, default=100
        Number of top variable genes to consider per cell type.
    min_cells_per_condition : int, default=10
        Minimum cells per condition required for computation.

    Returns
    -------
    results : dict
        Dictionary with keys:
        - 'per_celltype': {celltype: variance_preservation_ratio}
        - 'mean': Mean across cell types
        - 'weighted_mean': Weighted mean by cell count
        - 'celltypes_computed': List of cell types included
    """
    unique_conditions = np.unique(condition_labels)
    if len(unique_conditions) < 2:
        return {'per_celltype': {}, 'mean': np.nan, 'weighted_mean': np.nan, 'celltypes_computed': []}

    unique_celltypes = np.unique(celltype_labels)
    per_celltype = {}
    cell_counts = {}

    for ct in unique_celltypes:
        ct_mask = celltype_labels == ct

        # Check minimum cells per condition
        has_enough = True
        for cond in unique_conditions:
            cond_ct_mask = ct_mask & (condition_labels == cond)
            if cond_ct_mask.sum() < min_cells_per_condition:
                has_enough = False
                break

        if not has_enough:
            continue

        # Compute variance preservation for this cell type
        X_orig_ct = X_original[ct_mask]
        X_corr_ct = X_corrected[ct_mask]
        cond_ct = condition_labels[ct_mask]

        try:
            vp = compute_variance_preservation(X_orig_ct, X_corr_ct, cond_ct, top_n_genes)
            if not np.isnan(vp):
                per_celltype[str(ct)] = vp
                cell_counts[str(ct)] = int(ct_mask.sum())
        except Exception:
            continue

    # Compute aggregates
    if per_celltype:
        values = list(per_celltype.values())
        counts = [cell_counts[ct] for ct in per_celltype.keys()]
        mean_vp = np.mean(values)
        weighted_mean_vp = np.average(values, weights=counts)
    else:
        mean_vp = np.nan
        weighted_mean_vp = np.nan

    return {
        'per_celltype': per_celltype,
        'mean': mean_vp,
        'weighted_mean': weighted_mean_vp,
        'celltypes_computed': list(per_celltype.keys()),
    }


def compute_effect_correlation_per_celltype(
    X_original: np.ndarray,
    X_corrected: np.ndarray,
    condition_labels: np.ndarray,
    celltype_labels: np.ndarray,
    top_n_genes: Optional[int] = None,
    min_cells_per_condition: int = 10,
) -> Dict[str, Dict[str, float]]:
    """Compute effect correlation for each cell type.

    Parameters
    ----------
    X_original : np.ndarray
        Original expression matrix, shape (n_cells, n_genes).
    X_corrected : np.ndarray
        Corrected expression matrix, shape (n_cells, n_genes).
    condition_labels : np.ndarray
        Condition labels for each cell.
    celltype_labels : np.ndarray
        Cell type labels for each cell.
    top_n_genes : int, optional
        If specified, use only top variable genes.
    min_cells_per_condition : int, default=10
        Minimum cells per condition required for computation.

    Returns
    -------
    results : dict
        Dictionary with keys:
        - 'per_celltype': {celltype: {'pearson_r': ..., 'spearman_r': ...}}
        - 'mean_pearson': Mean Pearson correlation across cell types
        - 'weighted_mean_pearson': Weighted mean by cell count
        - 'celltypes_computed': List of cell types included
    """
    unique_conditions = np.unique(condition_labels)
    if len(unique_conditions) < 2:
        return {'per_celltype': {}, 'mean_pearson': np.nan, 'weighted_mean_pearson': np.nan, 'celltypes_computed': []}

    unique_celltypes = np.unique(celltype_labels)
    per_celltype = {}
    cell_counts = {}

    for ct in unique_celltypes:
        ct_mask = celltype_labels == ct

        # Check minimum cells per condition
        has_enough = True
        for cond in unique_conditions:
            cond_ct_mask = ct_mask & (condition_labels == cond)
            if cond_ct_mask.sum() < min_cells_per_condition:
                has_enough = False
                break

        if not has_enough:
            continue

        # Compute effect correlation for this cell type
        X_orig_ct = X_original[ct_mask]
        X_corr_ct = X_corrected[ct_mask]
        cond_ct = condition_labels[ct_mask]

        try:
            result = compute_effect_correlation(X_orig_ct, X_corr_ct, cond_ct, top_n_genes)
            if not np.isnan(result['pearson_r']):
                per_celltype[str(ct)] = result
                cell_counts[str(ct)] = int(ct_mask.sum())
        except Exception:
            continue

    # Compute aggregates
    if per_celltype:
        pearson_values = [r['pearson_r'] for r in per_celltype.values()]
        counts = [cell_counts[ct] for ct in per_celltype.keys()]
        mean_pearson = np.mean(pearson_values)
        weighted_mean_pearson = np.average(pearson_values, weights=counts)
    else:
        mean_pearson = np.nan
        weighted_mean_pearson = np.nan

    return {
        'per_celltype': per_celltype,
        'mean_pearson': mean_pearson,
        'weighted_mean_pearson': weighted_mean_pearson,
        'celltypes_computed': list(per_celltype.keys()),
    }


def compute_deg_overlap(
    X_original: np.ndarray,
    X_corrected: np.ndarray,
    condition_labels: np.ndarray,
    gene_names: Optional[np.ndarray] = None,
    n_top: int = 100,
    method: str = 'wilcoxon',
) -> Dict[str, float]:
    """Compute DEG overlap between original and corrected data.

    Identifies differentially expressed genes in both datasets and
    computes overlap metrics (precision, recall, F1).

    Parameters
    ----------
    X_original : np.ndarray
        Original expression matrix, shape (n_cells, n_genes).
    X_corrected : np.ndarray
        Corrected expression matrix, shape (n_cells, n_genes).
    condition_labels : np.ndarray
        Condition labels for each cell (assumes 2 conditions).
    gene_names : np.ndarray, optional
        Gene names for reporting.
    n_top : int, default=100
        Number of top DEGs to consider from each dataset.
    method : str, default='wilcoxon'
        Statistical test method ('wilcoxon' or 'ttest').

    Returns
    -------
    results : dict
        Dictionary with keys: 'precision', 'recall', 'f1', 'overlap_count'.

    Notes
    -----
    DEGs are identified by ranking genes by p-value from the specified
    test. The top n_top genes from each dataset are compared.

    F1 = 2 * (precision * recall) / (precision + recall)
    """
    unique_conditions = np.unique(condition_labels)
    if len(unique_conditions) != 2:
        return {'precision': np.nan, 'recall': np.nan, 'f1': np.nan, 'overlap_count': 0}

    cond1, cond2 = unique_conditions
    mask1 = condition_labels == cond1
    mask2 = condition_labels == cond2

    def get_top_degs(X):
        """Get top DEGs by p-value ranking."""
        pvals = []
        for gene_idx in range(X.shape[1]):
            expr1 = X[mask1, gene_idx]
            expr2 = X[mask2, gene_idx]

            # Skip genes with no variance
            if np.std(expr1) < 1e-10 and np.std(expr2) < 1e-10:
                pvals.append(1.0)
                continue

            try:
                if method == 'wilcoxon':
                    _, pval = stats.mannwhitneyu(expr1, expr2, alternative='two-sided')
                else:  # ttest
                    _, pval = stats.ttest_ind(expr1, expr2)
                pvals.append(pval)
            except Exception:
                pvals.append(1.0)

        pvals = np.array(pvals)
        top_indices = np.argsort(pvals)[:n_top]
        return set(top_indices)

    # Get DEGs from original and corrected
    degs_original = get_top_degs(X_original)
    degs_corrected = get_top_degs(X_corrected)

    # Compute overlap metrics
    overlap = degs_original & degs_corrected
    overlap_count = len(overlap)

    precision = overlap_count / len(degs_corrected) if len(degs_corrected) > 0 else 0
    recall = overlap_count / len(degs_original) if len(degs_original) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'overlap_count': overlap_count,
    }


def _compute_pairwise_effect_correlation(
    X_original: np.ndarray,
    X_corrected: np.ndarray,
    mask1: np.ndarray,
    mask2: np.ndarray,
    top_n_genes: Optional[int] = None,
) -> Dict[str, float]:
    """Compute effect correlation for a single pair of conditions."""
    # Compute effects (log fold change for log-normalized data)
    effect_original = X_original[mask1].mean(axis=0) - X_original[mask2].mean(axis=0)
    effect_corrected = X_corrected[mask1].mean(axis=0) - X_corrected[mask2].mean(axis=0)

    # Filter to top variable genes if specified
    if top_n_genes is not None:
        var_original = np.abs(effect_original)
        top_genes = np.argsort(var_original)[-top_n_genes:]
        effect_original = effect_original[top_genes]
        effect_corrected = effect_corrected[top_genes]

    # Filter out genes with zero variance
    valid_mask = (np.abs(effect_original) > 1e-10) | (np.abs(effect_corrected) > 1e-10)
    if valid_mask.sum() < 10:
        return {'pearson_r': np.nan, 'pearson_p': np.nan, 'spearman_r': np.nan}

    effect_original = effect_original[valid_mask]
    effect_corrected = effect_corrected[valid_mask]

    # Compute correlations
    pearson_r, pearson_p = stats.pearsonr(effect_original, effect_corrected)
    spearman_r, _ = stats.spearmanr(effect_original, effect_corrected)

    return {
        'pearson_r': pearson_r,
        'pearson_p': pearson_p,
        'spearman_r': spearman_r,
    }


def compute_effect_correlation(
    X_original: np.ndarray,
    X_corrected: np.ndarray,
    condition_labels: np.ndarray,
    top_n_genes: Optional[int] = None,
) -> Dict[str, float]:
    """Compute correlation of condition effects between original and corrected.

    Measures how well the log fold changes between conditions are preserved
    after batch correction.

    Parameters
    ----------
    X_original : np.ndarray
        Original expression matrix, shape (n_cells, n_genes).
    X_corrected : np.ndarray
        Corrected expression matrix, shape (n_cells, n_genes).
    condition_labels : np.ndarray
        Condition labels for each cell. Supports 2 or more conditions.
        For 3+ conditions, computes pairwise correlations and averages.
    top_n_genes : int, optional
        If specified, use only top variable genes.

    Returns
    -------
    results : dict
        Dictionary with keys:
        - 'pearson_r': Pearson correlation coefficient (average for 3+ conditions)
        - 'pearson_p': p-value for Pearson correlation (NaN for 3+ conditions)
        - 'spearman_r': Spearman correlation coefficient (average for 3+ conditions)

    Notes
    -----
    Effect size is computed as log2 fold change:
    effect = mean(cond1) - mean(cond2)  (for log-normalized data)

    High correlation indicates that the relative expression differences
    between conditions are preserved after batch correction.

    For 3+ conditions, pairwise effect correlations are computed for all
    pairs and averaged.
    """
    unique_conditions = np.unique(condition_labels)
    if len(unique_conditions) < 2:
        return {'pearson_r': np.nan, 'pearson_p': np.nan, 'spearman_r': np.nan}

    # For exactly 2 conditions, use simple pairwise
    if len(unique_conditions) == 2:
        cond1, cond2 = unique_conditions
        mask1 = condition_labels == cond1
        mask2 = condition_labels == cond2
        return _compute_pairwise_effect_correlation(
            X_original, X_corrected, mask1, mask2, top_n_genes
        )

    # For 3+ conditions, compute all pairwise correlations and average
    from itertools import combinations

    pearson_rs = []
    spearman_rs = []

    for cond1, cond2 in combinations(unique_conditions, 2):
        mask1 = condition_labels == cond1
        mask2 = condition_labels == cond2

        result = _compute_pairwise_effect_correlation(
            X_original, X_corrected, mask1, mask2, top_n_genes
        )

        if not np.isnan(result['pearson_r']):
            pearson_rs.append(result['pearson_r'])
        if not np.isnan(result['spearman_r']):
            spearman_rs.append(result['spearman_r'])

    # Average pairwise correlations
    mean_pearson = np.mean(pearson_rs) if pearson_rs else np.nan
    mean_spearman = np.mean(spearman_rs) if spearman_rs else np.nan

    return {
        'pearson_r': mean_pearson,
        'pearson_p': np.nan,  # p-value not meaningful for averaged correlation
        'spearman_r': mean_spearman,
    }


# =============================================================================
# Ground Truth DEG Metrics
# =============================================================================

def compute_deg_f1_vs_ground_truth(
    X_corrected: np.ndarray,
    condition_labels: np.ndarray,
    ground_truth_de_genes: np.ndarray,
    n_top: int = 100,
    method: str = 'wilcoxon',
) -> Dict[str, float]:
    """Compute DEG detection F1 against ground truth DE genes.

    Compares detected DEGs in corrected data against the known ground truth
    DE genes from simulation. This is the proper way to evaluate DEG
    preservation - comparing to the true biological signal.

    Parameters
    ----------
    X_corrected : np.ndarray
        Corrected expression matrix, shape (n_cells, n_genes).
    condition_labels : np.ndarray
        Condition labels for each cell (assumes 2 conditions).
    ground_truth_de_genes : np.ndarray
        Boolean array indicating true DE genes, shape (n_genes,).
        Typically from adata.var['is_de_gene'].
    n_top : int, default=100
        Number of top DEGs to detect from corrected data.
    method : str, default='wilcoxon'
        Statistical test method ('wilcoxon' or 'ttest').

    Returns
    -------
    results : dict
        Dictionary with keys:
        - 'precision': Fraction of detected DEGs that are true DEGs
        - 'recall': Fraction of true DEGs that are detected
        - 'f1': F1 score (harmonic mean of precision and recall)
        - 'n_true_de': Number of ground truth DE genes
        - 'n_detected': Number of detected DEGs

    Notes
    -----
    This metric answers: "Of the genes we detect as DE after correction,
    how many are actually true DE genes?"

    Unlike compute_deg_overlap which compares original vs corrected,
    this function compares against the simulation ground truth.
    """
    unique_conditions = np.unique(condition_labels)
    if len(unique_conditions) != 2:
        return {
            'precision': np.nan, 'recall': np.nan, 'f1': np.nan,
            'n_true_de': 0, 'n_detected': 0
        }

    cond1, cond2 = unique_conditions
    mask1 = condition_labels == cond1
    mask2 = condition_labels == cond2

    # Detect DEGs from corrected data
    pvals = []
    for gene_idx in range(X_corrected.shape[1]):
        expr1 = X_corrected[mask1, gene_idx]
        expr2 = X_corrected[mask2, gene_idx]

        if np.std(expr1) < 1e-10 and np.std(expr2) < 1e-10:
            pvals.append(1.0)
            continue

        try:
            if method == 'wilcoxon':
                _, pval = stats.mannwhitneyu(expr1, expr2, alternative='two-sided')
            else:
                _, pval = stats.ttest_ind(expr1, expr2)
            pvals.append(pval)
        except Exception:
            pvals.append(1.0)

    pvals = np.array(pvals)
    detected_indices = set(np.argsort(pvals)[:n_top])

    # Ground truth set
    gt_indices = set(np.where(ground_truth_de_genes)[0])
    n_true_de = len(gt_indices)

    if n_true_de == 0:
        return {
            'precision': np.nan, 'recall': np.nan, 'f1': np.nan,
            'n_true_de': 0, 'n_detected': len(detected_indices)
        }

    # Compute metrics
    overlap = detected_indices & gt_indices
    precision = len(overlap) / len(detected_indices) if len(detected_indices) > 0 else 0
    recall = len(overlap) / n_true_de
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'n_true_de': n_true_de,
        'n_detected': len(detected_indices),
    }


def compute_expression_correlation(
    X_ground_truth: np.ndarray,
    X_corrected: np.ndarray,
) -> float:
    """Compute Pearson correlation between ground truth and corrected expression.

    Measures how well the corrected expression matches the true biological
    expression (without batch effects). This is the proper way to evaluate
    expression preservation - comparing to ground truth, not batch-affected data.

    Parameters
    ----------
    X_ground_truth : np.ndarray
        Ground truth expression matrix WITHOUT batch effects, shape (n_cells, n_genes).
        This should be from adata.layers['X_no_batch'] (log-normalized).
    X_corrected : np.ndarray
        Corrected expression matrix, shape (n_cells, n_genes).

    Returns
    -------
    correlation : float
        Pearson correlation coefficient between flattened matrices.
        Range: [-1, 1], higher is better.

    Notes
    -----
    IMPORTANT: X_ground_truth should be expression BEFORE batch effect application.
    Using expression AFTER batch effect (X_original) is meaningless because
    successful batch correction would REDUCE correlation with batch-affected data.
    """
    # Flatten and compute correlation
    gt_flat = X_ground_truth.flatten()
    corr_flat = X_corrected.flatten()

    # Handle edge cases
    if len(gt_flat) == 0 or np.std(gt_flat) < 1e-10 or np.std(corr_flat) < 1e-10:
        return np.nan

    correlation, _ = stats.pearsonr(gt_flat, corr_flat)
    return correlation


def compute_batch_removal_score(
    X_with_batch: np.ndarray,
    X_corrected: np.ndarray,
    X_no_batch: np.ndarray,
) -> Dict[str, float]:
    """Compute batch effect removal score.

    Compares:
    1. Correlation of corrected with ground truth (should be HIGH)
    2. Correlation of corrected with batch-affected data (expected to decrease)

    The difference shows how much batch effect was removed while
    preserving true biological signal.

    Parameters
    ----------
    X_with_batch : np.ndarray
        Expression WITH batch effects (original input), shape (n_cells, n_genes).
    X_corrected : np.ndarray
        Corrected expression matrix, shape (n_cells, n_genes).
    X_no_batch : np.ndarray
        Ground truth expression WITHOUT batch effects, shape (n_cells, n_genes).

    Returns
    -------
    results : dict
        Dictionary with keys:
        - 'corr_vs_ground_truth': Correlation with true expression (higher = better)
        - 'corr_vs_batch_affected': Correlation with batch-affected data
        - 'batch_removal_gain': Ground truth corr minus batch-affected corr
          Positive values indicate successful batch removal with signal preservation.
    """
    # Correlation with ground truth (should be HIGH for good correction)
    corr_gt = compute_expression_correlation(X_no_batch, X_corrected)

    # Correlation with batch-affected data (expected to decrease after correction)
    gt_flat = X_with_batch.flatten()
    corr_flat = X_corrected.flatten()
    if len(gt_flat) == 0 or np.std(gt_flat) < 1e-10 or np.std(corr_flat) < 1e-10:
        corr_batch = np.nan
    else:
        corr_batch, _ = stats.pearsonr(gt_flat, corr_flat)

    # Batch removal gain: how much we improved correlation with ground truth
    # vs correlation with batch-affected data
    if np.isnan(corr_gt) or np.isnan(corr_batch):
        gain = np.nan
    else:
        gain = corr_gt - corr_batch

    return {
        'corr_vs_ground_truth': corr_gt,
        'corr_vs_batch_affected': corr_batch,
        'batch_removal_gain': gain,
    }


# =============================================================================
# Effect Size Preservation Metrics (NEW - for scDistill vs scVI differentiation)
# =============================================================================

def compute_effect_size_preservation(
    X_original: np.ndarray,
    X_corrected: np.ndarray,
    condition_labels: np.ndarray,
    ground_truth_de_genes: Optional[np.ndarray] = None,
) -> Dict[str, float]:
    """Compute effect size preservation ratio (corrected effect / original effect).

    This metric measures how well the magnitude of condition effects is preserved.
    A ratio of 1.0 indicates perfect preservation, <1.0 indicates attenuation,
    >1.0 indicates amplification.

    Parameters
    ----------
    X_original : np.ndarray
        Original expression matrix, shape (n_cells, n_genes).
    X_corrected : np.ndarray
        Corrected expression matrix, shape (n_cells, n_genes).
    condition_labels : np.ndarray
        Condition labels for each cell.
    ground_truth_de_genes : np.ndarray, optional
        Boolean array indicating true DE genes.

    Returns
    -------
    results : dict
        Dictionary with keys:
        - 'effect_ratio_median': Median effect size ratio (ideal=1.0)
        - 'effect_ratio_mean': Mean effect size ratio
        - 'effect_ratio_low_expr': Ratio for low-expression genes
        - 'effect_ratio_mid_expr': Ratio for medium-expression genes
        - 'effect_ratio_high_expr': Ratio for high-expression genes
        - 'de_effect_correlation': Effect correlation for DE genes (if ground truth available)
        - 'non_de_effect_correlation': Effect correlation for non-DE genes
    """
    unique_conditions = np.unique(condition_labels)
    if len(unique_conditions) < 2:
        return {
            'effect_ratio_median': np.nan,
            'effect_ratio_mean': np.nan,
            'effect_ratio_low_expr': np.nan,
            'effect_ratio_mid_expr': np.nan,
            'effect_ratio_high_expr': np.nan,
            'de_effect_correlation': np.nan,
            'non_de_effect_correlation': np.nan,
        }

    cond1, cond2 = unique_conditions[:2]
    mask1 = condition_labels == cond1
    mask2 = condition_labels == cond2

    # Compute effects (mean difference between conditions)
    effect_original = X_original[mask1].mean(axis=0) - X_original[mask2].mean(axis=0)
    effect_corrected = X_corrected[mask1].mean(axis=0) - X_corrected[mask2].mean(axis=0)

    # Effect size ratio per gene (avoid division by zero)
    valid_mask = np.abs(effect_original) > 1e-10
    ratios = np.abs(effect_corrected[valid_mask]) / np.abs(effect_original[valid_mask])

    # Overall statistics
    effect_ratio_median = np.median(ratios) if len(ratios) > 0 else np.nan
    effect_ratio_mean = np.mean(ratios) if len(ratios) > 0 else np.nan

    # Stratify by expression level (using original mean expression)
    gene_means = X_original.mean(axis=0)
    low_th = np.percentile(gene_means, 25)
    high_th = np.percentile(gene_means, 75)

    low_mask = (gene_means < low_th) & valid_mask
    mid_mask = (gene_means >= low_th) & (gene_means < high_th) & valid_mask
    high_mask = (gene_means >= high_th) & valid_mask

    def safe_ratio(mask):
        if mask.sum() < 5:
            return np.nan
        return np.median(np.abs(effect_corrected[mask]) / (np.abs(effect_original[mask]) + 1e-10))

    effect_ratio_low = safe_ratio(low_mask)
    effect_ratio_mid = safe_ratio(mid_mask)
    effect_ratio_high = safe_ratio(high_mask)

    # DE/Non-DE effect correlation
    de_effect_corr = np.nan
    non_de_effect_corr = np.nan

    if ground_truth_de_genes is not None:
        de_mask = ground_truth_de_genes
        non_de_mask = ~ground_truth_de_genes

        if de_mask.sum() >= 10:
            de_effect_corr = np.corrcoef(effect_original[de_mask], effect_corrected[de_mask])[0, 1]
        if non_de_mask.sum() >= 10:
            non_de_effect_corr = np.corrcoef(effect_original[non_de_mask], effect_corrected[non_de_mask])[0, 1]

    # === INTUITIVE METRICS (all: 1.0 = ideal, higher = better) ===

    # Effect Accuracy: 1.0 - |ratio - 1.0|, capped at [0, 1]
    # Measures how well effect sizes are preserved (1.0 = perfect)
    effect_accuracy = np.nan
    if not np.isnan(effect_ratio_median):
        distortion = abs(effect_ratio_median - 1.0)
        effect_accuracy = max(0.0, 1.0 - distortion)

    # Signal Fidelity: 1 / (1 + noise_ratio)
    # Measures how little spurious signal is introduced to non-DE genes (1.0 = perfect)
    signal_fidelity = np.nan
    if ground_truth_de_genes is not None:
        non_de_mask = ~ground_truth_de_genes
        if non_de_mask.sum() >= 10:
            # Spurious effect = corrected - original effect in non-DE genes
            spurious_effects = effect_corrected[non_de_mask] - effect_original[non_de_mask]
            orig_effect_std = np.std(effect_original[non_de_mask])
            if orig_effect_std > 1e-10:
                noise_ratio = np.std(spurious_effects) / orig_effect_std
            else:
                noise_ratio = np.std(spurious_effects)
            # Transform to 0-1 scale: 1/(1+noise) gives 1 when noise=0, approaches 0 as noise→∞
            signal_fidelity = 1.0 / (1.0 + noise_ratio)

    return {
        'effect_ratio_median': effect_ratio_median,
        'effect_ratio_mean': effect_ratio_mean,
        'effect_ratio_low_expr': effect_ratio_low,
        'effect_ratio_mid_expr': effect_ratio_mid,
        'effect_ratio_high_expr': effect_ratio_high,
        'de_effect_correlation': de_effect_corr,
        'non_de_effect_correlation': non_de_effect_corr,
        # Intuitive metrics (all: 1.0 = ideal, higher = better)
        'effect_accuracy': effect_accuracy,
        'signal_fidelity': signal_fidelity,
    }


def compute_marker_preservation(
    X_original: np.ndarray,
    X_corrected: np.ndarray,
    celltype_labels: np.ndarray,
    marker_genes: Optional[Dict[str, np.ndarray]] = None,
) -> Dict[str, float]:
    """Compute cell type marker gene preservation.

    Measures how well the expression difference between cell types
    is preserved for marker genes after batch correction.

    Parameters
    ----------
    X_original : np.ndarray
        Original expression matrix, shape (n_cells, n_genes).
    X_corrected : np.ndarray
        Corrected expression matrix, shape (n_cells, n_genes).
    celltype_labels : np.ndarray
        Cell type labels for each cell.
    marker_genes : dict, optional
        Dictionary mapping cell type names to boolean arrays indicating marker genes.
        If None, uses variance-based automatic detection.

    Returns
    -------
    results : dict
        Dictionary with keys:
        - 'marker_preservation_mean': Mean marker preservation across cell types
        - 'marker_preservation_min': Minimum marker preservation
        - 'per_celltype': Per-celltype preservation scores
    """
    unique_celltypes = np.unique(celltype_labels)
    if len(unique_celltypes) < 2:
        return {
            'marker_preservation_mean': np.nan,
            'marker_preservation_min': np.nan,
            'per_celltype': {},
        }

    per_celltype = {}

    for ct in unique_celltypes:
        ct_mask = celltype_labels == ct
        other_mask = celltype_labels != ct

        if ct_mask.sum() < 5 or other_mask.sum() < 5:
            continue

        # Compute marker expression difference: this celltype vs others
        orig_diff = X_original[ct_mask].mean(axis=0) - X_original[other_mask].mean(axis=0)
        corr_diff = X_corrected[ct_mask].mean(axis=0) - X_corrected[other_mask].mean(axis=0)

        # Use marker genes if provided, else use top variable genes
        if marker_genes is not None and str(ct) in marker_genes:
            gene_mask = marker_genes[str(ct)]
        else:
            # Use top 10% of genes by original difference magnitude
            top_n = max(10, int(len(orig_diff) * 0.1))
            gene_mask = np.zeros(len(orig_diff), dtype=bool)
            gene_mask[np.argsort(np.abs(orig_diff))[-top_n:]] = True

        if gene_mask.sum() < 5:
            continue

        # Correlation of marker expression differences
        corr = np.corrcoef(orig_diff[gene_mask], corr_diff[gene_mask])[0, 1]
        if not np.isnan(corr):
            per_celltype[str(ct)] = corr

    if not per_celltype:
        return {
            'marker_preservation_mean': np.nan,
            'marker_preservation_min': np.nan,
            'per_celltype': {},
        }

    values = list(per_celltype.values())
    return {
        'marker_preservation_mean': np.mean(values),
        'marker_preservation_min': np.min(values),
        'per_celltype': per_celltype,
    }


def compute_effect_variance_by_magnitude(
    X_original: np.ndarray,
    X_corrected: np.ndarray,
    condition_labels: np.ndarray,
    true_log2fc: Optional[np.ndarray] = None,
    ground_truth_de_genes: Optional[np.ndarray] = None,
) -> Dict[str, float]:
    """Compute variance preservation stratified by effect magnitude.

    Measures how well variance is preserved for genes with different
    effect sizes (small, medium, large).

    Parameters
    ----------
    X_original : np.ndarray
        Original expression matrix, shape (n_cells, n_genes).
    X_corrected : np.ndarray
        Corrected expression matrix, shape (n_cells, n_genes).
    condition_labels : np.ndarray
        Condition labels for each cell.
    true_log2fc : np.ndarray, optional
        True log2 fold change values for each gene (from simulation).
    ground_truth_de_genes : np.ndarray, optional
        Boolean array indicating true DE genes.

    Returns
    -------
    results : dict
        Dictionary with keys:
        - 'var_pres_small_effect': Variance preservation for small effects (|lfc|<0.5)
        - 'var_pres_medium_effect': Variance preservation for medium effects (0.5<=|lfc|<1)
        - 'var_pres_large_effect': Variance preservation for large effects (|lfc|>=1)
    """
    unique_conditions = np.unique(condition_labels)
    if len(unique_conditions) < 2:
        return {
            'var_pres_small_effect': np.nan,
            'var_pres_medium_effect': np.nan,
            'var_pres_large_effect': np.nan,
        }

    cond1, cond2 = unique_conditions[:2]
    mask1 = condition_labels == cond1
    mask2 = condition_labels == cond2

    # Compute effects
    effect_original = X_original[mask1].mean(axis=0) - X_original[mask2].mean(axis=0)
    effect_corrected = X_corrected[mask1].mean(axis=0) - X_corrected[mask2].mean(axis=0)

    # Use true log2fc if available, else use observed effect
    if true_log2fc is not None and ground_truth_de_genes is not None:
        # Only for DE genes
        de_idx = np.where(ground_truth_de_genes)[0]
        lfc = np.abs(true_log2fc[de_idx])
        orig_eff = effect_original[de_idx]
        corr_eff = effect_corrected[de_idx]
    else:
        # Use observed effect magnitude
        lfc = np.abs(effect_original)
        orig_eff = effect_original
        corr_eff = effect_corrected

    def safe_var_ratio(mask):
        if mask.sum() < 5:
            return np.nan
        orig_var = orig_eff[mask].var()
        corr_var = corr_eff[mask].var()
        if orig_var < 1e-10:
            return np.nan
        return corr_var / orig_var

    # Stratify by effect magnitude
    small_mask = lfc < 0.5
    medium_mask = (lfc >= 0.5) & (lfc < 1.0)
    large_mask = lfc >= 1.0

    return {
        'var_pres_small_effect': safe_var_ratio(small_mask),
        'var_pres_medium_effect': safe_var_ratio(medium_mask),
        'var_pres_large_effect': safe_var_ratio(large_mask),
    }


# =============================================================================
# Combined Computation
# =============================================================================

def compute_all_covariate_metrics(
    embedding: Optional[np.ndarray] = None,
    X_original: Optional[np.ndarray] = None,
    X_corrected: Optional[np.ndarray] = None,
    condition_labels: Optional[np.ndarray] = None,
    config: Optional[CovariateConservation] = None,
) -> Dict[str, float]:
    """Compute all covariate conservation metrics.

    Parameters
    ----------
    embedding : np.ndarray, optional
        Embedding matrix for condition_asw.
    X_original : np.ndarray, optional
        Original expression for expression-level metrics.
    X_corrected : np.ndarray, optional
        Corrected expression for expression-level metrics.
    condition_labels : np.ndarray, optional
        Condition labels.
    config : CovariateConservation, optional
        Configuration for which metrics to compute.

    Returns
    -------
    results : dict
        Dictionary with all computed metrics.
    """
    if config is None:
        config = CovariateConservation()

    results = {}

    # Embedding-level metrics
    if config.condition_asw and embedding is not None and condition_labels is not None:
        results['condition_asw'] = compute_condition_asw(embedding, condition_labels)

    # Expression-level metrics
    if X_original is not None and X_corrected is not None and condition_labels is not None:
        if config.variance_preservation:
            results['variance_preservation'] = compute_variance_preservation(
                X_original, X_corrected, condition_labels
            )

        if config.deg_overlap:
            deg_results = compute_deg_overlap(X_original, X_corrected, condition_labels)
            results['deg_f1'] = deg_results['f1']
            results['deg_precision'] = deg_results['precision']
            results['deg_recall'] = deg_results['recall']

        if config.effect_correlation:
            effect_results = compute_effect_correlation(X_original, X_corrected, condition_labels)
            results['effect_pearson_r'] = effect_results['pearson_r']
            results['effect_spearman_r'] = effect_results['spearman_r']

    return results

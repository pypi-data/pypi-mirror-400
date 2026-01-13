"""Differential Expression Analysis.

This module provides two DE analysis methods:

1. **pseudobulk** (default): Sample-level pseudobulk DE analysis with proper
   statistical testing. Groups cells by sample (biological replicate) and
   performs t-test at sample level. Recommended for most use cases.

2. **bayesian**: Bayesian DE detection using MC Dropout inspired by scVI.
   More computationally intensive but provides uncertainty estimates.
   Not recommended due to inflated significance with large cell numbers.

References
----------
- DESeq2: Anders & Huber (2010)
- scVI differential expression guide
"""

import torch
import numpy as np
import pandas as pd
from typing import Optional, Literal, Tuple, Dict, Union
from scipy import stats
from scipy.stats import ttest_ind, false_discovery_control
from sklearn.metrics import roc_auc_score, average_precision_score


def differential_expression_pseudobulk(
    X_corrected: np.ndarray,
    idx1: np.ndarray,
    idx2: np.ndarray,
    sample_labels: np.ndarray,
    gene_names: Optional[np.ndarray] = None,
    min_cells_per_sample: int = 5,
    lfc_threshold: Union[float, Literal['auto']] = 0.25,
    fdr_threshold: float = 0.05,
    method: Literal['wilcox', 'ttest', 'deseq2'] = 'wilcox',
    center_lfc: bool = False,
) -> pd.DataFrame:
    """Perform sample-level pseudobulk differential expression analysis.

    Groups cells by sample (biological replicate) and performs statistical
    testing at the sample level. This is the statistically correct approach
    for single-cell DE analysis.

    Parameters
    ----------
    X_corrected : np.ndarray
        Batch-corrected expression matrix in log1p space (n_cells, n_genes)
    idx1 : np.ndarray
        Boolean mask for group 1 cells (e.g., Healthy)
    idx2 : np.ndarray
        Boolean mask for group 2 cells (e.g., COVID)
    sample_labels : np.ndarray
        Sample ID for each cell (n_cells,). Used to group cells into
        biological replicates for pseudobulk aggregation.
    gene_names : np.ndarray, optional
        Gene names for results table
    min_cells_per_sample : int
        Minimum cells required per sample to include in analysis (default: 5)
    lfc_threshold : float or 'auto'
        Minimum |LFC| to consider as DE.
        - 'auto' (default): Dynamically determine threshold based on the 95th
          percentile of |LFC| for non-significant genes (FDR >= 0.5).
        - float: Fixed threshold value.
    fdr_threshold : float
        FDR threshold for significance (default: 0.05)
    method : str
        Statistical test method:
        - 'wilcox' (default): Wilcoxon rank-sum test (robust, non-parametric)
        - 'ttest': Student's t-test (parametric)
        - 'deseq2': DESeq2-style negative binomial test (requires pydeseq2)
    center_lfc : bool
        If True (default), center LFC values by subtracting the median LFC
        of non-significant genes. This corrects for systematic bias caused
        by library size or composition differences between conditions.

    Returns
    -------
    results_df : pd.DataFrame
        Results table with columns:
        - gene: Gene name
        - lfc: Log2 fold-change (group1 / group2), positive = up in group1
        - lfc_std: Standard deviation across samples
        - pval: P-value from statistical test
        - fdr: FDR-corrected p-value (Benjamini-Hochberg)
        - is_de: Boolean indicator of DE (|LFC| > threshold AND FDR < threshold)
        - direction: 'up_in_group1' or 'down_in_group1' (based on LFC sign)

    Notes
    -----
    LFC is computed as log2 fold-change (group1 vs group2):
        LFC = log2((mean_group1 + 1) / (mean_group2 + 1))

    Positive LFC means higher expression in group1.
    Negative LFC means higher expression in group2.

    Means are computed on pseudo-counts (expm1 of log1p data).
    """
    from scipy.stats import mannwhitneyu, ranksums
    n_genes = X_corrected.shape[1]

    # Convert boolean masks to indices if needed
    idx1_mask = idx1 if idx1.dtype == bool else np.isin(np.arange(len(sample_labels)), idx1)
    idx2_mask = idx2 if idx2.dtype == bool else np.isin(np.arange(len(sample_labels)), idx2)

    # Find samples with enough cells in each group
    unique_samples = np.unique(sample_labels)
    samples_group1 = []
    samples_group2 = []

    for sample in unique_samples:
        sample_mask = sample_labels == sample
        n_cells_g1 = np.sum(sample_mask & idx1_mask)
        n_cells_g2 = np.sum(sample_mask & idx2_mask)

        if n_cells_g1 >= min_cells_per_sample:
            samples_group1.append(sample)
        if n_cells_g2 >= min_cells_per_sample:
            samples_group2.append(sample)

    n_samples_g1 = len(samples_group1)
    n_samples_g2 = len(samples_group2)

    print("=" * 70)
    print("DIFFERENTIAL EXPRESSION ANALYSIS (Sample-level Pseudobulk)")
    print("=" * 70)
    print(f"\n  Group 1: {n_samples_g1} samples (min {min_cells_per_sample} cells each)")
    print(f"  Group 2: {n_samples_g2} samples (min {min_cells_per_sample} cells each)")

    if n_samples_g1 < 3 or n_samples_g2 < 3:
        raise ValueError(
            f"Insufficient samples for DE analysis. "
            f"Group 1: {n_samples_g1}, Group 2: {n_samples_g2}. "
            f"Need at least 3 samples per group."
        )

    # Compute pseudobulk for each sample
    # Convert to pseudo-counts and compute mean per sample
    def compute_sample_pseudobulk(samples, group_mask):
        """Compute pseudobulk expression for each sample."""
        pseudobulk = []
        for sample in samples:
            mask = (sample_labels == sample) & group_mask
            if mask.sum() > 0:
                # Convert from log1p to pseudo-counts
                counts = np.expm1(X_corrected[mask])
                # Mean expression per sample
                pb = counts.mean(axis=0)
                pseudobulk.append(pb)
        return np.array(pseudobulk)  # (n_samples, n_genes)

    print(f"\n  Computing pseudobulk per sample...")
    pb_group1 = compute_sample_pseudobulk(samples_group1, idx1_mask)
    pb_group2 = compute_sample_pseudobulk(samples_group2, idx2_mask)

    print(f"  Pseudobulk shape: Group1={pb_group1.shape}, Group2={pb_group2.shape}")

    # Compute LFC: log2((mean_group1 + 1) / (mean_group2 + 1))
    # Positive LFC = higher in group1, Negative LFC = higher in group2
    mean_g1 = pb_group1.mean(axis=0)
    mean_g2 = pb_group2.mean(axis=0)
    eps = 1.0  # Pseudocount
    lfc = np.log2((mean_g1 + eps) / (mean_g2 + eps))

    # Compute LFC std across samples (for uncertainty estimate)
    # Individual sample LFCs
    sample_lfcs_g1 = np.log2(pb_group1 + eps)
    sample_lfcs_g2 = np.log2(pb_group2 + eps)
    lfc_std = np.sqrt(
        np.var(sample_lfcs_g2.mean(axis=0) - sample_lfcs_g1, axis=0) / n_samples_g1 +
        np.var(sample_lfcs_g2 - sample_lfcs_g1.mean(axis=0), axis=0) / n_samples_g2
    )

    # P-values using selected method
    print(f"\n  Computing p-values (method={method})...")
    pvals = np.zeros(n_genes)

    if method == 'wilcox':
        # Wilcoxon rank-sum test (Mann-Whitney U) - robust, non-parametric
        for g in range(n_genes):
            try:
                _, pvals[g] = ranksums(pb_group2[:, g], pb_group1[:, g])
            except Exception:
                pvals[g] = 1.0

    elif method == 'ttest':
        # Student's t-test - parametric
        for g in range(n_genes):
            try:
                _, pvals[g] = ttest_ind(pb_group2[:, g], pb_group1[:, g])
            except Exception:
                pvals[g] = 1.0

    elif method == 'deseq2':
        # DESeq2-style using pydeseq2
        try:
            from pydeseq2.dds import DeseqDataSet
            from pydeseq2.ds import DeseqStats

            # Prepare count matrix (samples x genes)
            counts = np.vstack([pb_group1, pb_group2]).astype(int)
            counts = np.maximum(counts, 0)  # Ensure non-negative

            # Sample metadata
            conditions = ['group1'] * n_samples_g1 + ['group2'] * n_samples_g2
            metadata = pd.DataFrame({'condition': conditions})
            metadata.index = [f'sample_{i}' for i in range(len(conditions))]

            # Gene names for count matrix
            if gene_names is not None:
                count_df = pd.DataFrame(counts, columns=gene_names)
            else:
                count_df = pd.DataFrame(counts)
            count_df.index = metadata.index

            # Run DESeq2
            dds = DeseqDataSet(counts=count_df, metadata=metadata, design_factors='condition')
            dds.deseq2()

            stat_res = DeseqStats(dds, contrast=['condition', 'group2', 'group1'])
            stat_res.summary()

            results_deseq = stat_res.results_df
            pvals = results_deseq['pvalue'].values
            # Use DESeq2's LFC instead
            lfc = results_deseq['log2FoldChange'].values

        except ImportError:
            raise ImportError(
                "pydeseq2 is required for method='deseq2'. "
                "Install with: pip install pydeseq2"
            )
        except Exception as e:
            print(f"  Warning: DESeq2 failed ({e}), falling back to wilcox")
            method = 'wilcox'
            for g in range(n_genes):
                try:
                    _, pvals[g] = ranksums(pb_group2[:, g], pb_group1[:, g])
                except Exception:
                    pvals[g] = 1.0
    else:
        raise ValueError(f"Unknown method: {method}. Use 'wilcox', 'ttest', or 'deseq2'")

    # Handle NaN p-values
    pvals = np.nan_to_num(pvals, nan=1.0)

    # FDR correction (Benjamini-Hochberg)
    try:
        fdr = false_discovery_control(pvals, method='bh')
    except Exception:
        # Fallback for older scipy versions
        sorted_idx = np.argsort(pvals)
        fdr = np.zeros(n_genes)
        for i, idx in enumerate(sorted_idx):
            fdr[idx] = pvals[idx] * n_genes / (i + 1)
        fdr = np.minimum.accumulate(fdr[np.argsort(sorted_idx)[::-1]])[::-1]
        fdr = np.clip(fdr, 0, 1)

    # Apply LFC centering to correct composition bias
    # Non-significant genes (high FDR) should have ~0 LFC on average
    if center_lfc:
        # Use genes with FDR >= 0.5 as "null" genes (clearly non-significant)
        null_mask = fdr >= 0.5
        if null_mask.sum() > 10:
            lfc_offset = np.median(lfc[null_mask])
            lfc = lfc - lfc_offset
            print(f"\n  ✓ LFC centering applied: offset = {lfc_offset:.4f}")
        else:
            print(f"\n  ⚠ LFC centering skipped: too few null genes ({null_mask.sum()})")

    # Determine LFC threshold
    if lfc_threshold == 'auto':
        # Use 95th percentile of |LFC| for non-significant genes as threshold
        null_mask = fdr >= 0.5
        if null_mask.sum() > 10:
            auto_threshold = np.percentile(np.abs(lfc[null_mask]), 95)
            # Ensure minimum threshold of 0.1
            lfc_threshold_used = max(auto_threshold, 0.1)
            print(f"  ✓ Auto LFC threshold: {lfc_threshold_used:.4f} (95th percentile of null genes)")
        else:
            lfc_threshold_used = 0.25  # Default fallback
            print(f"  ⚠ Auto threshold fallback: {lfc_threshold_used} (too few null genes)")
    else:
        lfc_threshold_used = lfc_threshold

    # Determine DE genes
    is_de = (np.abs(lfc) > lfc_threshold_used) & (fdr < fdr_threshold)

    # Gene names
    if gene_names is None:
        gene_names = np.array([f'gene_{i}' for i in range(n_genes)])

    # Create results DataFrame
    results_df = pd.DataFrame({
        'gene': gene_names,
        'lfc': lfc,
        'lfc_std': lfc_std,
        'pval': pvals,
        'fdr': fdr,
        'is_de': is_de,
        'direction': np.where(lfc > 0, 'up_in_group1', 'down_in_group1')
    })

    # Sort by |LFC| descending
    results_df['abs_lfc'] = np.abs(results_df['lfc'])
    results_df = results_df.sort_values('abs_lfc', ascending=False).reset_index(drop=True)
    results_df = results_df.drop(columns=['abs_lfc'])

    # Summary statistics
    n_de = is_de.sum()
    n_up = ((lfc > lfc_threshold_used) & (fdr < fdr_threshold)).sum()
    n_down = ((lfc < -lfc_threshold_used) & (fdr < fdr_threshold)).sum()
    n_sig_fdr = (fdr < fdr_threshold).sum()

    print(f"\n  ✓ Mean |LFC|: {np.mean(np.abs(lfc)):.4f}")
    print(f"  ✓ FDR < {fdr_threshold}: {n_sig_fdr} genes")
    print(f"  ✓ DE genes (|LFC| > {lfc_threshold_used:.4f}, FDR < {fdr_threshold}): {n_de}")
    print(f"    - UP (Group2 > Group1): {n_up}")
    print(f"    - DOWN (Group2 < Group1): {n_down}")

    print("\n" + "=" * 70)
    print(f"SUMMARY: {n_de} DE genes detected ({n_up} up, {n_down} down)")
    print("=" * 70)

    return results_df


# =============================================================================
# Bayesian DE (legacy, not recommended)
# =============================================================================

def sample_expression_posterior(
    model,
    X: np.ndarray,
    idx: np.ndarray,
    n_samples: int = 100,
    device: str = 'cpu'
) -> np.ndarray:
    """Sample expression levels from posterior using MC Dropout.

    WARNING: This method is not recommended due to inflated significance
    with large cell numbers. Use pseudobulk method instead.
    """
    model = model.to(device)
    model.train()  # Enable dropout

    X_subset = X[idx]
    x = torch.from_numpy(X_subset).float().to(device)

    samples = []
    for _ in range(n_samples):
        with torch.no_grad():
            U = model(x)
            X_recon = model.decode(U)
            samples.append(X_recon.cpu().numpy())

    return np.stack(samples, axis=0)


def differential_expression_bayesian(
    model,
    X: np.ndarray,
    idx1: np.ndarray,
    idx2: np.ndarray,
    mode: Literal['vanilla', 'change'] = 'change',
    delta: Optional[float] = None,
    fdr_target: float = 0.05,
    n_samples: int = 100,
    device: str = 'cpu',
    gene_names: Optional[np.ndarray] = None
) -> pd.DataFrame:
    """Perform Bayesian differential expression analysis.

    WARNING: This method is not recommended for single-cell data due to
    inflated significance with large cell numbers. Statistical significance
    does not equal biological significance when N is large.

    Use `differential_expression_pseudobulk` instead for proper statistical
    testing at the sample level.
    """
    import warnings
    warnings.warn(
        "Bayesian DE is not recommended for single-cell data due to inflated "
        "significance with large N. Use pseudobulk method instead.",
        UserWarning
    )

    print("=" * 70)
    print("DIFFERENTIAL EXPRESSION ANALYSIS (Bayesian)")
    print("WARNING: Not recommended - use pseudobulk method instead")
    print("=" * 70)

    # Sample expression
    print(f"\n[1/4] Sampling expression posterior (n_samples={n_samples})...")
    samples_A = sample_expression_posterior(model, X, idx1, n_samples, device)
    samples_B = sample_expression_posterior(model, X, idx2, n_samples, device)

    # Aggregate across cells
    print(f"\n[2/4] Aggregating across cells...")
    pop_A = np.mean(samples_A, axis=1)  # (n_samples, n_genes)
    pop_B = np.mean(samples_B, axis=1)

    # Compute LFC
    print(f"\n[3/4] Computing log fold-change...")
    eps = 1e-8
    lfc_samples = np.log2(np.maximum(pop_B, eps) + eps) - np.log2(np.maximum(pop_A, eps) + eps)
    lfc_mean = np.mean(lfc_samples, axis=0)
    lfc_std = np.std(lfc_samples, axis=0)

    # Compute p(DE)
    print(f"\n[4/4] Computing posterior probability...")
    if delta is None:
        delta = 0.1
    p_de = np.mean(np.abs(lfc_samples) > delta, axis=0)

    # FDR control
    sorted_idx = np.argsort(-p_de)
    n_genes = len(p_de)
    fdr = np.zeros(n_genes)
    for k in range(1, n_genes + 1):
        fdr[k - 1] = np.sum(1 - p_de[sorted_idx[:k]]) / k

    fdr_reordered = fdr[np.argsort(sorted_idx)]
    is_de = np.zeros(n_genes, dtype=bool)
    valid_k = np.where(fdr <= fdr_target)[0]
    if len(valid_k) > 0:
        k_star = valid_k[-1] + 1
        is_de[sorted_idx[:k_star]] = True

    if gene_names is None:
        gene_names = np.array([f'gene_{i}' for i in range(n_genes)])

    results_df = pd.DataFrame({
        'gene': gene_names,
        'lfc': lfc_mean,
        'lfc_std': lfc_std,
        'p_de': p_de,
        'fdr': fdr_reordered,
        'is_de': is_de,
        'direction': np.where(lfc_mean > 0, 'up', 'down')
    })

    results_df = results_df.sort_values('p_de', ascending=False).reset_index(drop=True)

    print(f"\n  Detected DE genes: {is_de.sum()}")
    return results_df


# =============================================================================
# Main dispatcher function
# =============================================================================

def differential_expression(
    X_corrected: Optional[np.ndarray] = None,
    idx1: Optional[np.ndarray] = None,
    idx2: Optional[np.ndarray] = None,
    sample_labels: Optional[np.ndarray] = None,
    gene_names: Optional[np.ndarray] = None,
    how: Literal['pseudobulk', 'bayesian'] = 'pseudobulk',
    # Pseudobulk-specific params
    min_cells_per_sample: int = 5,
    lfc_threshold: float = 0.1,
    fdr_threshold: float = 0.05,
    method: Literal['wilcox', 'ttest', 'deseq2'] = 'wilcox',
    # Bayesian-specific params (legacy)
    model=None,
    X: Optional[np.ndarray] = None,
    mode: Literal['vanilla', 'change'] = 'change',
    delta: Optional[float] = None,
    fdr_target: float = 0.05,
    n_samples: int = 100,
    device: str = 'cpu',
) -> pd.DataFrame:
    """Perform differential expression analysis.

    Parameters
    ----------
    X_corrected : np.ndarray
        Batch-corrected expression matrix in log1p space (n_cells, n_genes)
    idx1 : np.ndarray
        Boolean mask for group 1 cells (reference group, e.g., Healthy)
    idx2 : np.ndarray
        Boolean mask for group 2 cells (comparison group, e.g., COVID)
    sample_labels : np.ndarray
        Sample ID for each cell. Required for pseudobulk method.
    gene_names : np.ndarray, optional
        Gene names for results table
    how : str
        DE method to use:
        - 'pseudobulk' (default): Sample-level pseudobulk
        - 'bayesian': MC Dropout-based (legacy, not recommended)

    Pseudobulk-specific parameters
    ------------------------------
    min_cells_per_sample : int
        Minimum cells per sample (default: 5)
    lfc_threshold : float
        Minimum |LFC| for DE (default: 0.1)
    fdr_threshold : float
        FDR threshold (default: 0.05)
    method : str
        Statistical test: 'wilcox' (default), 'ttest', or 'deseq2'

    Bayesian-specific parameters (legacy)
    -------------------------------------
    model : HarmonyMLP
        Trained model (required for bayesian)
    X : np.ndarray
        Input expression matrix (required for bayesian)
    mode, delta, fdr_target, n_samples, device : various
        Bayesian-specific settings

    Returns
    -------
    results_df : pd.DataFrame
        DE results table with columns: gene, lfc, pval/p_de, fdr, is_de, direction
    """
    if idx1 is None or idx2 is None:
        raise ValueError("idx1 and idx2 must be provided")

    if how == 'pseudobulk':
        if X_corrected is None:
            raise ValueError("X_corrected is required for pseudobulk method")
        if sample_labels is None:
            raise ValueError(
                "sample_labels is required for pseudobulk method. "
                "Provide the sample/donor ID for each cell to enable "
                "proper sample-level statistical testing."
            )
        return differential_expression_pseudobulk(
            X_corrected=X_corrected,
            idx1=idx1,
            idx2=idx2,
            sample_labels=sample_labels,
            gene_names=gene_names,
            min_cells_per_sample=min_cells_per_sample,
            lfc_threshold=lfc_threshold,
            fdr_threshold=fdr_threshold,
            method=method,
        )

    elif how == 'bayesian':
        if model is None or X is None:
            raise ValueError("model and X are required for bayesian method")
        return differential_expression_bayesian(
            model=model,
            X=X,
            idx1=idx1,
            idx2=idx2,
            mode=mode,
            delta=delta,
            fdr_target=fdr_target,
            n_samples=n_samples,
            device=device,
            gene_names=gene_names,
        )

    else:
        raise ValueError(f"Unknown method: {how}. Use 'pseudobulk' or 'bayesian'")

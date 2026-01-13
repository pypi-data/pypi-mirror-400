"""Evaluation module for scDistill.

This module provides evaluation metrics for batch correction,
extending scib-metrics with Covariate Conservation metrics.

Main Classes
------------
- DistillBenchmarker: scIB-compatible benchmarker with covariate conservation

Three metric categories:
1. Batch Correction: iLISI, KBET, Graph connectivity, PCR, Silhouette batch
2. Bio Conservation: NMI, ARI, Silhouette label, cLISI, Isolated labels
3. Covariate Conservation: Condition ASW, Variance Preservation, DEG overlap, Effect Correlation

Example
-------
>>> from scdistill.evaluation import DistillBenchmarker
>>>
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
>>> # Access underlying scIB Benchmarker
>>> scib_bm = bm.scib
"""

from .covariate import (
    CovariateConservation,
    compute_condition_asw,
    compute_variance_preservation,
    compute_variance_preservation_per_celltype,
    compute_effect_correlation_per_celltype,
    compute_deg_overlap,
    compute_effect_correlation,
    compute_all_covariate_metrics,
    # Ground truth metrics
    compute_deg_f1_vs_ground_truth,
    compute_expression_correlation,
    compute_batch_removal_score,
    # Effect size preservation metrics
    compute_effect_size_preservation,
    compute_marker_preservation,
    compute_effect_variance_by_magnitude,
)
from .metrics import (
    # DistillBenchmarker
    DistillBenchmarker,
    # Individual metric functions
    compute_all_metrics,
    compute_silhouette_batch,
    compute_ilisi,
    compute_nmi_ari,
    compute_silhouette_label,
    # Additional scib-metrics
    compute_kbet,
    compute_graph_connectivity,
    compute_pcr,
    compute_clisi,
    compute_isolated_labels,
    SCIB_AVAILABLE,
)

__all__ = [
    # Main class
    "DistillBenchmarker",
    # Covariate Conservation
    "CovariateConservation",
    "compute_condition_asw",
    "compute_variance_preservation",
    "compute_variance_preservation_per_celltype",
    "compute_effect_correlation_per_celltype",
    "compute_deg_overlap",
    "compute_effect_correlation",
    "compute_all_covariate_metrics",
    "compute_deg_f1_vs_ground_truth",
    "compute_expression_correlation",
    "compute_batch_removal_score",
    # Effect size preservation metrics
    "compute_effect_size_preservation",
    "compute_marker_preservation",
    "compute_effect_variance_by_magnitude",
    # scib-metrics wrappers
    "compute_all_metrics",
    "compute_silhouette_batch",
    "compute_ilisi",
    "compute_kbet",
    "compute_graph_connectivity",
    "compute_pcr",
    "compute_nmi_ari",
    "compute_silhouette_label",
    "compute_clisi",
    "compute_isolated_labels",
    "SCIB_AVAILABLE",
]

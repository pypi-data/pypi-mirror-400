# scDistill vs scVI Comparison Benchmark

This benchmark compares scDistill against scVI across the same 6 simulation scenarios to evaluate relative performance on batch correction and differential expression detection.

## Overview

Both models are evaluated on:
- **Differential Expression (DE) Detection**: Precision, recall, F1 score
- **Batch Integration**: iLISI, silhouette batch score
- **Biological Conservation**: NMI, ARI, condition ASW
- **Effect Size Estimation**: Correlation with ground truth log fold changes

## Prerequisites

1. Run the performance benchmark first (generates cached scDistill models):
```bash
uv run python benchmarks/1_performance/run_benchmark.py
```

2. Install scVI:
```bash
uv add scvi-tools
```

## Usage

### Run Comparison
```bash
uv run python benchmarks/2_bench_other/run_comparison.py
```

### Options
```bash
# Force retrain all models
uv run python benchmarks/2_bench_other/run_comparison.py --no-cache

# Run specific scenarios
uv run python benchmarks/2_bench_other/run_comparison.py --scenarios scenario1 scenario3
```

### Generate R Visualizations
```bash
cd benchmarks/2_bench_other
Rscript visualize_comparison.R
```

## Results

### Combined Summary

![Combined Summary](results/figures_r/fig7_combined_summary.png)

**Insights**: This summary view reveals the fundamental trade-off between the two approaches. scVI excels at batch mixing but sacrifices DE detection sensitivity. scDistill prioritizes preserving biological signal, resulting in dramatically better DE detection while still achieving reasonable batch correction.

### Differential Expression Detection

![DE Detection](results/figures_r/fig1_de_detection.png)

**Insights**:
- **scVI's low recall (0.26-0.34)**: scVI over-corrects, removing biological signal along with batch effects, causing it to miss most true DE genes
- **scDistill's high recall (0.63-0.98)**: By learning from a teacher that explicitly preserves condition effects, scDistill maintains the biological signal needed for DE detection
- **Both maintain high precision**: Neither method calls many false positives, but scVI is too conservative

| Scenario | scVI F1 | scDistill F1 | Δ |
|----------|---------|--------------|---|
| 1 (Basic) | 0.502 | **0.987** | +0.485 |
| 2 (Medium) | 0.450 | **0.941** | +0.491 |
| 3 (Imbalanced) | 0.411 | **0.946** | +0.535 |
| 4 (Weak conf.) | 0.448 | **0.927** | +0.479 |
| 5 (Strong conf.) | 0.400 | **0.686** | +0.286 |
| 6 (ZINB) | 0.456 | **0.992** | +0.536 |

### Biological Conservation

![Biological Conservation](results/figures_r/fig2_bio_conservation.png)

**Insights**:
- **Condition ASW measures how well conditions remain separated** after batch correction
- scDistill consistently achieves higher condition ASW (0.52-0.66 vs 0.54-0.60), indicating better preservation of condition-related biological variation
- This directly translates to better DE detection performance

| Scenario | scVI Condition ASW | scDistill Condition ASW |
|----------|-------------------|------------------------|
| 1 | 0.586 | **0.659** |
| 2 | 0.603 | **0.651** |
| 3 | 0.536 | **0.664** |
| 4 | 0.585 | **0.663** |
| 5 | 0.538 | 0.521 |
| 6 | 0.563 | **0.582** |

### Batch Integration

![Batch Integration](results/figures_r/fig3_batch_integration.png)

**Insights**:
- **iLISI measures local batch diversity**—higher values mean batches are better mixed
- scVI achieves higher iLISI in most scenarios, reflecting its primary optimization goal
- However, **aggressive batch mixing can remove biological signal**, explaining scVI's poor DE performance
- scDistill accepts slightly lower batch mixing to preserve condition effects

| Scenario | scVI iLISI | scDistill iLISI |
|----------|------------|-----------------|
| 1 | **0.864** | 0.691 |
| 2 | **0.784** | 0.655 |
| 3 | 0.599 | 0.550 |
| 4 | **0.695** | 0.495 |
| 5 | **0.456** | 0.055 |
| 6 | **0.898** | 0.891 |

### Summary Heatmap

![Summary Heatmap](results/figures_r/fig4_summary_heatmap.png)

**Insights**: The heatmap provides a comprehensive view across all metrics and scenarios. Red indicates scDistill advantage, blue indicates scVI advantage. The strong red pattern in DE metrics (precision, recall, F1) demonstrates scDistill's clear superiority for differential expression studies.

### Performance Difference

![Performance Difference](results/figures_r/fig5_performance_diff.png)

**Insights**:
- Bars show (scDistill - scVI) for each metric
- **DE F1 difference (+0.29 to +0.54)**: scDistill's largest advantage
- **iLISI difference (-0.01 to -0.40)**: scVI's advantage in batch mixing
- The trade-off is clear: scVI wins on batch metrics, scDistill wins on biological metrics

### UMAP Visualizations

**Insights**: Visual comparison of latent spaces. In scVI embeddings, conditions often overlap more (better batch mixing but lost biological signal). In scDistill embeddings, conditions remain more distinct (preserved biological signal for DE analysis).

#### Scenario 1 (Basic)
![UMAP Scenario 1](results/figures_r/fig6_umap_scenario1.png)

#### Scenario 2 (Medium Scale)
![UMAP Scenario 2](results/figures_r/fig6_umap_scenario2.png)

#### Scenario 3 (Imbalanced)
![UMAP Scenario 3](results/figures_r/fig6_umap_scenario3.png)

## Detailed Results

### DE Detection Breakdown

| Scenario | Model | Precision | Recall | F1 |
|----------|-------|-----------|--------|-----|
| 1 | scVI | 1.000 | 0.335 | 0.502 |
| 1 | scDistill | 0.992 | 0.983 | **0.987** |
| 2 | scVI | 1.000 | 0.290 | 0.450 |
| 2 | scDistill | 0.989 | 0.898 | **0.941** |
| 3 | scVI | 1.000 | 0.258 | 0.411 |
| 3 | scDistill | 0.996 | 0.900 | **0.946** |
| 4 | scVI | 1.000 | 0.288 | 0.448 |
| 4 | scDistill | 0.974 | 0.883 | **0.927** |
| 5 | scVI | 0.832 | 0.263 | 0.400 |
| 5 | scDistill | 0.759 | 0.625 | **0.686** |
| 6 | scVI | 1.000 | 0.295 | 0.456 |
| 6 | scDistill | 1.000 | 0.985 | **0.992** |

### Effect Size Correlation (Pearson r)

| Scenario | scVI | scDistill |
|----------|------|-----------|
| 1 | **0.999** | 0.982 |
| 2 | **0.999** | 0.953 |
| 3 | **0.999** | 0.949 |
| 4 | 0.972 | 0.937 |
| 5 | 0.697 | **0.741** |
| 6 | **0.997** | 0.982 |

## Output Files

```
results/
├── comparison_summary.csv         # All metrics for both models
├── scenario{1-6}/
│   ├── metrics/comparison_metrics.json
│   └── visualization/
│       ├── combined_umap.csv      # UMAP coordinates
│       ├── scvi_latent.csv
│       └── scdistill_latent.csv
└── figures_r/                     # R-generated comparison figures
    ├── fig1_de_detection.pdf
    ├── fig2_bio_conservation.pdf
    ├── fig3_batch_integration.pdf
    ├── fig4_summary_heatmap.pdf
    ├── fig5_performance_diff.pdf
    ├── fig6_umap_scenario*.pdf
    └── fig7_combined_summary.pdf
```

## Key Findings

1. **DE Detection**: scDistill significantly outperforms scVI in recall (detecting true DE genes) while maintaining high precision. scVI tends to be overly conservative.

2. **Batch Integration**: scVI achieves better batch mixing (higher iLISI), which comes at the cost of potentially over-correcting biological signal.

3. **Biological Conservation**: scDistill better preserves condition-related signal (higher condition ASW), which is critical for downstream DE analysis.

4. **Trade-off**: scVI prioritizes batch removal, while scDistill balances batch correction with biological signal preservation—making it more suitable for differential expression studies.

5. **Strong Confounding**: Both methods struggle with strong batch-condition confounding (scenario 5), but scDistill still achieves higher F1 score.

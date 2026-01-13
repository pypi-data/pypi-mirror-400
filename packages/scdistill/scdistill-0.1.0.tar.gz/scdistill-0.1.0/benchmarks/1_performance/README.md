# scDistill Performance Benchmark

This benchmark evaluates scDistill's internal performance across 6 simulation scenarios with varying batch-condition confounding levels.

## Scenarios

| Scenario | Description | Cells | Genes | Batches | Confounding |
|----------|-------------|-------|-------|---------|-------------|
| 1 | Basic validation | 5,000 | 2,000 | 2 | None |
| 2 | Medium scale, 2 covariates | 8,000 | 3,000 | 3 | None |
| 3 | Imbalanced batch sizes | 10,000 | 3,000 | 4 | None |
| 4 | Weak confounding | 8,000 | 3,000 | 3 | Weak (70/50/30%) |
| 5 | Strong confounding | 8,000 | 3,000 | 3 | Strong (100/50/0%) |
| 6 | ZINB distribution | 5,000 | 2,000 | 2 | None |

## Prerequisites

1. Generate simulation data first:
```bash
cd simulation
Rscript generate_data.R
```

2. Install dependencies:
```bash
uv sync
```

## Usage

### Run Full Benchmark
```bash
uv run python benchmarks/1_performance/run_benchmark.py
```

### Options
```bash
# Force retrain models (ignore cache)
uv run python benchmarks/1_performance/run_benchmark.py --no-cache

# Run specific scenario
uv run python benchmarks/1_performance/run_benchmark.py --scenarios scenario1 scenario2
```

### Generate R Visualizations
```bash
# Export data for R
uv run python benchmarks/1_performance/export_for_r.py

# Render all figures
cd benchmarks/1_performance/visualizations/r_plots
Rscript render_all.R
```

## Results

### Metrics Overview

![Metrics Overview](results/figures_r/fig1_metrics_overview.png)

**Insights**: scDistill maintains consistent performance across scenarios 1-4 and 6, with only scenario 5 (strong confounding) showing degradation. This demonstrates robustness to varying batch sizes, multiple covariates, and realistic zero-inflation.

### Differential Expression Performance

![DE Performance](results/figures_r/fig2_de_performance.png)

**Insights**:
- **High precision (>0.97)** across non-confounded scenarios indicates scDistill rarely calls false positives
- **High recall (>0.88)** shows it successfully detects most true DE genes
- Scenario 5's lower performance (F1=0.686) reflects the fundamental limitation when batch and condition are nearly perfectly correlated—this is expected and unavoidable

| Scenario | Precision | Recall | F1 Score | Accuracy |
|----------|-----------|--------|----------|----------|
| 1 (Basic) | 0.992 | 0.983 | 0.987 | 0.995 |
| 2 (Medium) | 0.989 | 0.898 | 0.941 | 0.978 |
| 3 (Imbalanced) | 0.996 | 0.900 | 0.946 | 0.979 |
| 4 (Weak conf.) | 0.974 | 0.883 | 0.927 | 0.972 |
| 5 (Strong conf.) | 0.759 | 0.625 | 0.686 | 0.885 |
| 6 (ZINB) | 1.000 | 0.985 | 0.992 | 0.997 |

### Effect Size Correlation

![Effect Size Scatter](results/figures_r/fig3_effect_scatter.png)

**Insights**:
- Estimated log fold changes (LFC) are highly correlated with ground truth (r > 0.93 for non-confounded scenarios)
- The scatter plots show tight clustering around the diagonal, indicating accurate effect size estimation
- Scenario 5 shows increased scatter due to the difficulty in separating batch from biological effects

| Scenario | Pearson r | Spearman ρ | MAE | RMSE |
|----------|-----------|------------|-----|------|
| 1 | 0.982 | 0.698 | 0.197 | 0.231 |
| 2 | 0.953 | 0.677 | 0.169 | 0.292 |
| 3 | 0.949 | 0.681 | 0.165 | 0.287 |
| 4 | 0.937 | 0.676 | 0.182 | 0.305 |
| 5 | 0.741 | 0.576 | 0.298 | 0.458 |
| 6 | 0.982 | 0.698 | 0.214 | 0.309 |

### UMAP Comparison (Before vs After Batch Correction)

![UMAP Comparison](results/figures_r/fig4_umap_comparison.png)

**Insights**:
- **Before correction**: Cells cluster primarily by batch (colors), obscuring biological structure
- **After correction**: Batch effects are removed while condition-related clustering is preserved
- The teacher (Harmony) provides initial batch correction; the student (scDistill) learns to generalize this

### Before/After Visualization

![Before After](results/figures_r/fig5_before_after.png)

**Insights**:
- Clear visual demonstration of batch effect removal
- Condition labels remain well-separated after correction, indicating preserved biological signal
- This balance between batch removal and signal preservation is key to accurate downstream DE analysis

### Latent Space Quality

| Scenario | iLISI (batch) | Condition ASW | NMI | ARI |
|----------|---------------|---------------|-----|-----|
| 1 | 0.691 | 0.659 | 1.000 | 1.000 |
| 2 | 0.655 | 0.651 | 1.000 | 1.000 |
| 3 | 0.550 | 0.664 | 1.000 | 1.000 |
| 4 | 0.495 | 0.663 | 1.000 | 1.000 |
| 5 | 0.055 | 0.521 | 1.000 | 1.000 |
| 6 | 0.891 | 0.582 | 1.000 | 1.000 |

## Output Files

```
results/
├── benchmark_summary.csv          # All metrics across scenarios
├── scenario{1-6}/
│   ├── metrics/all_metrics.json   # Detailed metrics
│   ├── lfc_data.csv               # Log fold change data
│   └── figures/                   # Generated plots
├── for_r_viz/                     # Data exported for R visualization
│   ├── metrics_long.csv
│   └── scenario*_umap.csv
└── figures_r/                     # R-generated publication figures
    ├── fig1_metrics_overview.pdf
    ├── fig2_de_performance.pdf
    ├── fig3_effect_scatter.pdf
    ├── fig4_umap_comparison.pdf
    └── fig5_before_after.pdf
```

## Key Findings

1. **Non-confounded scenarios (1-4, 6)**: scDistill achieves excellent DE detection (F1 > 0.92) and effect size correlation (r > 0.93)

2. **Strong confounding (scenario 5)**: Performance degrades as expected when batch and condition are nearly perfectly correlated

3. **ZINB distribution (scenario 6)**: Maintains high performance despite zero-inflation, demonstrating robustness to dropout

4. **Cell type preservation**: Perfect NMI/ARI across all scenarios indicates biological signal is well preserved

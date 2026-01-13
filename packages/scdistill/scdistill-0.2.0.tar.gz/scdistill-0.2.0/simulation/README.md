# scDistill Simulation Data

This module generates synthetic scRNA-seq data using scDesign3 for validating scDistill's batch correction and differential expression detection capabilities.

## Overview

The simulation framework creates controlled datasets with:
- Known ground truth batch effects
- Known ground truth biological signals (DE genes)
- Varying levels of batch-condition confounding

## Scenarios

Six scenarios with increasing complexity:

| Scenario | Cells | Genes | Batches | Covariates | Confounding | Description |
|----------|-------|-------|---------|------------|-------------|-------------|
| **scenario1** | 5,000 | 2,000 | 2 | condition | None | Basic validation with balanced design |
| **scenario2** | 8,000 | 3,000 | 3 | condition, age_group | None | Multiple covariates, balanced |
| **scenario3** | 10,000 | 3,000 | 4 | condition, age_group | None | Imbalanced batch sizes |
| **scenario4** | 8,000 | 3,000 | 3 | condition | Weak | Partial batch-condition correlation (70/50/30%) |
| **scenario5** | 8,000 | 3,000 | 3 | condition | Strong | Strong batch-condition confounding (100/50/0%) |
| **scenario6** | 5,000 | 2,000 | 2 | condition | None | ZINB distribution with zero-inflation |

## Quick Start

### 1. Install R Dependencies

```bash
Rscript simulation/install_packages.R
```

### 2. Generate Simulation Data

```bash
# Generate all scenarios
Rscript simulation/generate_data.R

# Or generate a specific scenario
Rscript simulation/generate_data.R scenario1
```

**Output**: `simulation/results/{scenario}/data.h5ad`

### 3. Run Benchmarks

After generating data, run the benchmark suites:

```bash
# scDistill performance evaluation
uv run python benchmarks/1_performance/run_benchmark.py

# scDistill vs scVI comparison
uv run python benchmarks/2_bench_other/run_comparison.py
```

## Data Format

Each scenario generates an AnnData file (`data.h5ad`) with:

```python
import scanpy as sc
adata = sc.read_h5ad("simulation/results/scenario1/data.h5ad")

# Observations (cells)
adata.obs["batch"]      # Batch labels (batch_0, batch_1, ...)
adata.obs["condition"]  # Condition labels (control, treated)
adata.obs["celltype"]   # Cell type labels

# Variables (genes)
adata.var["is_de"]      # Ground truth DE genes (True/False)
adata.var["true_lfc"]   # Ground truth log fold change

# Expression matrix
adata.X                 # Raw counts
adata.layers["log1p"]   # Log-normalized expression
```

## Scenario Configuration

Scenarios are defined in `scenarios.yaml`:

```yaml
scenario1:
  name: "Basic validation (non-confounded)"
  n_cells: 5000
  n_genes: 2000
  n_batches: 2
  covariates:
    - name: "condition"
      type: "categorical"
      levels: ["control", "treated"]
  design:
    type: "balanced"
  batch_effect_strength: "medium"
  biological_effect_strength: "strong"
```

### Custom Scenarios

Add a new scenario to `scenarios.yaml`:

```yaml
scenario_custom:
  name: "My custom scenario"
  n_cells: 6000
  n_genes: 2500
  n_batches: 2
  covariates:
    - name: "treatment"
      type: "categorical"
      levels: ["control", "drug_a", "drug_b"]
  design:
    type: "balanced"
  batch_effect_strength: "strong"
  biological_effect_strength: "medium"
```

Then generate:
```bash
Rscript simulation/generate_data.R scenario_custom
```

## Directory Structure

```
simulation/
├── scenarios.yaml         # Scenario definitions
├── generate_data.R        # scDesign3 data generation (R)
├── install_packages.R     # R package installation
├── run_validation.py      # Validation script (Python)
├── visualize.py           # Visualization (Python)
├── metrics.py             # Evaluation metrics
├── baselines/             # Baseline model wrappers
│   └── scvi_baseline.py
├── README.md              # This file
└── results/
    ├── scenario1/
    │   ├── data.h5ad           # Generated data
    │   └── scenario_info.json  # Scenario metadata
    ├── scenario2/
    ├── scenario3/
    ├── scenario4/
    ├── scenario5/
    └── scenario6/
```

## Dependencies

### R (for data generation)

```r
# Install via pak
pak::pak(c(
  "SONGDONGYUAN1994/scDesign3",
  "SingleCellExperiment",
  "anndata",
  "yaml"
))
```

### Python (for benchmarks)

Dependencies are managed via `uv` (see `pyproject.toml`):

```bash
uv sync
```

## Troubleshooting

### R package installation fails

```bash
# Retry with verbose output
Rscript simulation/install_packages.R
```

### Memory issues

Reduce `n_cells` or `n_genes` in `scenarios.yaml`:

```yaml
scenario1:
  n_cells: 2000  # Reduced from 5000
  n_genes: 1000  # Reduced from 2000
```

### scDesign3 fitting fails

- Check R version (>= 4.0)
- Ensure reference data has sufficient cells/genes
- Reduce `n_cores` if memory limited

## References

- **scDesign3**: Song et al., "scDesign3 generates realistic in silico data for multimodal single-cell and spatial omics", Nature Biotechnology (2024)
- **scVI**: Lopez et al., "Deep generative modeling for single-cell transcriptomics", Nature Methods (2018)
- **Harmony**: Korsunsky et al., "Fast, sensitive and accurate integration of single-cell data with Harmony", Nature Methods (2019)

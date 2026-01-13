"""MLP encoder-decoder for batch correction via knowledge distillation.

This module provides the neural network architecture for distillation learning.
The student MLP learns to reproduce any teacher's batch corrections
(Harmony, ComBat, fastMNN, LIGER, etc.) from gene expression.

Architecture:
- Encoder: Maps gene expression to batch-corrected embeddings
- Decoder: Reconstructs gene expression for differential expression analysis

The DistillationMLP model can work with any teacher that provides
batch-corrected embeddings, making it a general-purpose framework
for single-cell batch correction.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Optional, Dict
from tqdm import tqdm


def compute_loading_weights(
    loadings: np.ndarray,
    variance_ratio: np.ndarray,
    n_top_pcs: int = 50,
    floor: float = 0.1
) -> np.ndarray:
    """Compute gene importance weights from PCA loadings.

    This function computes gene importance based on how much each gene
    contributed to the teacher's latent space construction. Genes that
    the teacher used to build Z* receive higher weights.

    This is superior to HVG (Highly Variable Genes) because:
    - HVG identifies "noisy" genes (high variance), not important ones
    - Teacher-derived weights identify genes that define the structure
    - Preserves weak but consistent biological signals (LFC < 0.5)

    Parameters
    ----------
    loadings : np.ndarray
        PCA loadings (n_genes, n_pcs) from adata.varm['PCs']
    variance_ratio : np.ndarray
        Explained variance ratio (n_pcs,) from adata.uns['pca']['variance_ratio']
    n_top_pcs : int, default=50
        Number of top PCs to use for weighting
    floor : float, default=0.1
        Minimum weight to prevent complete ignoring of any gene

    Returns
    -------
    gene_weights : np.ndarray
        Normalized gene importance weights (n_genes,)
        Range: [floor, 1.0]
    """
    # Use top PCs only
    n_pcs = min(n_top_pcs, loadings.shape[1], len(variance_ratio))
    loadings_top = loadings[:, :n_pcs]
    var_ratio_top = variance_ratio[:n_pcs]

    # Weight = |Loading| × Eigenvalue contribution
    # S_g = Σ_k |Loading_g,k| × λ_k
    gene_scores = np.abs(loadings_top) @ var_ratio_top  # (n_genes,)

    # Normalize to [floor, 1.0]
    gene_scores = gene_scores / gene_scores.max()
    gene_weights = gene_scores + floor  # Apply floor
    gene_weights = gene_weights / gene_weights.max()  # Re-normalize

    return gene_weights


def gene_wise_correlation_loss(x_pred: torch.Tensor, x_true: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    """Compute gene-wise Pearson correlation loss.

    This loss focuses on preserving the variation PATTERN of each gene,
    ignoring shift (mean) and scale (variance). This makes it ideal for
    batch correction because:
    - Shift Invariant: Ignores batch-specific baseline differences
    - Scale Invariant: Ignores batch-specific amplitude scaling
    - Pattern Focus: Only matches the relative variation pattern

    Parameters
    ----------
    x_pred : torch.Tensor
        Predicted/reconstructed expression (N_samples, N_genes)
    x_true : torch.Tensor
        Target expression (N_samples, N_genes)
    eps : float
        Small constant for numerical stability

    Returns
    -------
    loss : torch.Tensor
        1 - mean(Pearson correlation across genes)
        Range: [0, 2], where 0 = perfect correlation, 2 = perfect anti-correlation
    """
    # 1. Center the data (gene-wise, across samples)
    x_pred_mean = x_pred.mean(dim=0, keepdim=True)
    x_true_mean = x_true.mean(dim=0, keepdim=True)

    x_pred_centered = x_pred - x_pred_mean
    x_true_centered = x_true - x_true_mean

    # 2. Compute covariance (gene-wise)
    covariance = (x_pred_centered * x_true_centered).mean(dim=0)

    # 3. Compute standard deviations (gene-wise)
    x_pred_std = x_pred.std(dim=0, unbiased=False) + eps
    x_true_std = x_true.std(dim=0, unbiased=False) + eps

    # 4. Pearson correlation per gene
    corr = covariance / (x_pred_std * x_true_std)

    # 5. Loss = 1 - mean correlation
    return 1.0 - corr.mean()


def weighted_gene_wise_correlation_loss(
    x_pred: torch.Tensor,
    x_true: torch.Tensor,
    gene_weights: torch.Tensor,
    eps: float = 1e-8
) -> torch.Tensor:
    """Compute weighted gene-wise Pearson correlation loss.

    This is an enhanced version of gene_wise_correlation_loss that applies
    teacher-derived importance weights to each gene. Genes that contributed
    more to the teacher's latent space construction receive higher weights.

    This protects weak but structurally important biological signals
    (e.g., LFC < 0.5) from being drowned out by noise.

    Parameters
    ----------
    x_pred : torch.Tensor
        Predicted/reconstructed expression (N_samples, N_genes)
    x_true : torch.Tensor
        Target expression (N_samples, N_genes)
    gene_weights : torch.Tensor
        Importance weights per gene (N_genes,)
        Should be normalized or sum to n_genes
    eps : float
        Small constant for numerical stability

    Returns
    -------
    loss : torch.Tensor
        1 - weighted_mean(Pearson correlation across genes)
        Range: [0, 2], where 0 = perfect correlation, 2 = perfect anti-correlation
    """
    # 1. Center the data (gene-wise, across samples)
    x_pred_mean = x_pred.mean(dim=0, keepdim=True)
    x_true_mean = x_true.mean(dim=0, keepdim=True)

    x_pred_centered = x_pred - x_pred_mean
    x_true_centered = x_true - x_true_mean

    # 2. Compute covariance (gene-wise)
    covariance = (x_pred_centered * x_true_centered).mean(dim=0)

    # 3. Compute standard deviations (gene-wise)
    x_pred_std = x_pred.std(dim=0, unbiased=False) + eps
    x_true_std = x_true.std(dim=0, unbiased=False) + eps

    # 4. Pearson correlation per gene
    corr = covariance / (x_pred_std * x_true_std)  # (n_genes,)

    # 5. Weighted loss = 1 - weighted_mean(correlation)
    weighted_corr = (corr * gene_weights).sum() / gene_weights.sum()

    return 1.0 - weighted_corr


class DistillationMLP(nn.Module):
    """Neural network for batch correction via knowledge distillation.

    DistillationMLP learns to map gene expression to batch-corrected
    embeddings by reproducing any teacher's corrections. It also maintains
    the ability to reconstruct expression for downstream analysis.

    Architecture:
    - Encoder: Gene expression → MLP layers → Batch-corrected embeddings
    - Decoder: Batch-corrected embeddings → Reconstructed expression

    Training:
    - Distillation loss: Match teacher's batch-corrected embeddings
    - Reconstruction loss: Accurately reconstruct original expression

    Parameters
    ----------
    input_dim : int
        Number of input genes
    latent_dim : int, default=20
        Dimension of batch-corrected embeddings
    hidden_dim : int, default=128
        Size of hidden layers in MLP
    n_layers_encoder : int, default=2
        Number of layers in encoder (input → hidden → ... → latent)
    n_layers_decoder : int, default=2
        Number of layers in decoder (latent → hidden → ... → output)
    dropout : float, default=0.1
        Dropout probability for regularization
    reconstruction_loss : str, default='mse'
        Type of reconstruction loss:
        - 'mse': Gaussian decoder with MSE loss (for log-normalized input) [DEFAULT]
          Works well for most cases. May produce negative values for very sparse data.
        - 'nb': Negative Binomial decoder with Adapter Layer
          Hybrid architecture: Encoder targets PCA/Harmony space,
          Adapter + NB decoder outputs count distribution.
          More stable than ZINB and guarantees non-negative output.
        - 'zinb': ZINB decoder with NLL loss (for raw count input)
          Requires 2-stage training. Use 'nb' instead for simpler workflow.

    Examples
    --------
    >>> # ZINB decoder (raw count input) - DEFAULT
    >>> model = DistillationMLP(input_dim=2000, latent_dim=50)
    >>> Z_student = model(X_raw_counts)  # Encode (internally log1p transformed)
    >>> X_recon = model.decode(Z_student)  # Returns μ*(1-π) for ZINB
    >>>
    >>> # MSE decoder (log-normalized input) - Legacy
    >>> model = DistillationMLP(input_dim=2000, latent_dim=50, reconstruction_loss='mse')
    >>> Z_student = model(X_expression)  # Encode
    >>> X_recon = model.decode(Z_student)  # Decode
    """

    def __init__(
        self,
        input_dim: int,
        latent_dim: int = 20,
        hidden_dim: int = 128,
        n_layers_encoder: int = 2,
        n_layers_decoder: int = 2,
        dropout: float = 0.1,
        reconstruction_loss: str = 'zinb',
        use_layernorm: bool = True,  # LayerNorm at encoder output for batch distance preservation
        # Legacy parameter (for backward compatibility)
        num_layers: int = None,
    ):
        super().__init__()

        # Handle legacy parameter
        if num_layers is not None:
            n_layers_encoder = num_layers

        # Validate reconstruction_loss
        if reconstruction_loss not in ('mse', 'zinb', 'nb'):
            raise ValueError(f"reconstruction_loss must be 'mse', 'nb', or 'zinb', got '{reconstruction_loss}'")

        self.input_dim = input_dim
        self.latent_dim = latent_dim
        self.hidden_dim = hidden_dim
        self.n_layers_encoder = n_layers_encoder
        self.n_layers_decoder = n_layers_decoder
        self.dropout = dropout
        self.reconstruction_loss = reconstruction_loss
        self.use_layernorm = use_layernorm

        # Build Encoder (with dropout between layers for batch distance preservation)
        self.encoder = self._build_mlp(
            input_dim=input_dim,
            output_dim=latent_dim,
            hidden_dim=hidden_dim,
            n_layers=n_layers_encoder,
            use_output_activation=False,
            use_dropout=True,  # Dropout between layers, not at input
        )

        # LayerNorm at encoder output (normalizes batch-specific scaling)
        # This is critical for preserving batch mixing (iLISI) from the teacher
        if use_layernorm:
            self.layer_norm = nn.LayerNorm(latent_dim)
        else:
            self.layer_norm = None

        # Build Decoder based on reconstruction_loss type
        if reconstruction_loss == 'zinb':
            from .zinb import ZINBDecoder
            self.decoder = ZINBDecoder(
                latent_dim=latent_dim,
                output_dim=input_dim,
                hidden_dim=hidden_dim,
                n_layers=n_layers_decoder,
            )
            self.zinb_decoder = self.decoder  # Alias for clarity
            self.nb_decoder = None
        elif reconstruction_loss == 'nb':
            from .zinb import NBDecoder
            self.decoder = NBDecoder(
                latent_dim=latent_dim,
                output_dim=input_dim,
                hidden_dim=hidden_dim,
                n_layers=n_layers_decoder,
            )
            self.nb_decoder = self.decoder  # Alias for clarity
            self.zinb_decoder = None
        else:
            # MSE decoder (Gaussian)
            self.decoder = self._build_mlp(
                input_dim=latent_dim,
                output_dim=input_dim,
                hidden_dim=hidden_dim,
                n_layers=n_layers_decoder,
                use_output_activation=False
            )
            self.zinb_decoder = None
            self.nb_decoder = None

        # Note: Dropout is applied between encoder layers (inside self.encoder)
        # for better batch distance preservation. See _build_mlp() with use_dropout=True.

    def _build_mlp(
        self,
        input_dim: int,
        output_dim: int,
        hidden_dim: int,
        n_layers: int,
        use_output_activation: bool = False,
        use_dropout: bool = False,
    ) -> nn.Sequential:
        """Build MLP with specified number of layers.

        n_layers=1: input → output (linear)
        n_layers=2: input → hidden → output
        n_layers=3: input → hidden → hidden → output

        Parameters
        ----------
        use_dropout : bool, default=False
            If True, add dropout between hidden layers (after ReLU).
            This placement preserves batch distance better than input dropout.
        """
        if n_layers < 1:
            raise ValueError("n_layers must be >= 1")

        layers = []

        if n_layers == 1:
            # Single linear layer
            layers.append(nn.Linear(input_dim, output_dim))
        else:
            # Input layer
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            if use_dropout:
                layers.append(nn.Dropout(self.dropout))

            # Hidden layers
            for _ in range(n_layers - 2):
                layers.append(nn.Linear(hidden_dim, hidden_dim))
                layers.append(nn.ReLU())
                if use_dropout:
                    layers.append(nn.Dropout(self.dropout))

            # Output layer
            layers.append(nn.Linear(hidden_dim, output_dim))

        if use_output_activation:
            layers.append(nn.ReLU())

        return nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass (encode).

        Parameters
        ----------
        x : torch.Tensor
            Input features (N, input_dim)
            - For ZINB: raw counts (will be log1p transformed internally)
            - For MSE: log-normalized expression

        Returns
        -------
        U : torch.Tensor
            Latent embeddings (N, latent_dim)
        """
        # For ZINB, apply log1p transformation for encoder stability
        if self.reconstruction_loss == 'zinb':
            x_enc = torch.log1p(x)
        else:
            x_enc = x

        # Dropout is now applied between encoder layers (inside self.encoder)
        # This placement preserves batch distance better than input dropout
        U = self.encoder(x_enc)

        # Apply LayerNorm if enabled (normalizes batch-specific scaling)
        if self.layer_norm is not None:
            U = self.layer_norm(U)

        return U

    def decode(
        self,
        U: torch.Tensor,
        library_size: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Decode latent embeddings to reconstructed expression.

        Parameters
        ----------
        U : torch.Tensor
            Latent embeddings (N, latent_dim)
        library_size : torch.Tensor, optional
            Total counts per cell (N,) or (N, 1).
            Required for NB decoder to compute μ = scale * library_size.

        Returns
        -------
        X_recon : torch.Tensor
            Reconstructed expression (N, input_dim)
            - For ZINB: expected value μ*(1-π), always non-negative
            - For NB: expected value μ in raw count space (if library_size given),
                     or scale (proportion) if library_size is None
            - For MSE: continuous values (may be negative)
        """
        if self.reconstruction_loss == 'zinb':
            # ZINB decoder returns expected value
            x_recon = self.decoder.get_mean(U)
        elif self.reconstruction_loss == 'nb':
            # NB decoder returns μ = scale * library_size
            x_recon = self.decoder.get_mean(U, library_size)
        else:
            # MSE decoder
            x_recon = self.decoder(U)

        return x_recon

    def decode_zinb_params(self, U: torch.Tensor) -> tuple:
        """Decode latent to ZINB parameters (μ, θ, π).

        Only available when reconstruction_loss='zinb'.

        Parameters
        ----------
        U : torch.Tensor
            Latent embeddings (N, latent_dim)

        Returns
        -------
        mu : torch.Tensor
            Mean expression (N, input_dim)
        theta : torch.Tensor
            Dispersion (N, input_dim)
        pi : torch.Tensor
            Dropout probability (N, input_dim)
        """
        if self.reconstruction_loss != 'zinb':
            raise ValueError("decode_zinb_params() only available with reconstruction_loss='zinb'")
        return self.decoder(U)

    def decode_nb_params(
        self,
        U: torch.Tensor,
        library_size: Optional[torch.Tensor] = None,
    ) -> tuple:
        """Decode latent to NB parameters (μ, θ).

        Only available when reconstruction_loss='nb'.

        Parameters
        ----------
        U : torch.Tensor
            Latent embeddings (N, latent_dim)
        library_size : torch.Tensor, optional
            Total counts per cell (N,) or (N, 1).
            If provided, returns μ = scale * library_size.
            If None, returns scale (proportion).

        Returns
        -------
        mu : torch.Tensor
            Mean expression (N, input_dim) in raw count space,
            or scale (proportion) if library_size is None
        theta : torch.Tensor
            Dispersion (n_genes,) - per-gene parameter
        """
        if self.reconstruction_loss != 'nb':
            raise ValueError("decode_nb_params() only available with reconstruction_loss='nb'")
        return self.decoder(U, library_size)

    def decode_nb_scale(self, U: torch.Tensor) -> torch.Tensor:
        """Get expression proportion (scale) from NB decoder.

        This returns the normalized expression proportion without
        library size scaling, useful for relative comparisons.

        Only available when reconstruction_loss='nb'.

        Parameters
        ----------
        U : torch.Tensor
            Latent embeddings (N, latent_dim)

        Returns
        -------
        scale : torch.Tensor
            Expression proportions (N, input_dim), sum to 1 per cell
        """
        if self.reconstruction_loss != 'nb':
            raise ValueError("decode_nb_scale() only available with reconstruction_loss='nb'")
        return self.decoder.get_scale(U)

def train_distillation(
    model: DistillationMLP,
    X: np.ndarray,
    Z_teacher: np.ndarray,
    n_epochs: int = 200,
    learning_rate: float = 1e-3,
    lambda_recon: float = 1.0,
    lambda_cosine: float = 2.0,
    lambda_norm: float = 0.0,
    lambda_corr: float = 1.0,  # Phase 3: Gene-wise correlation loss weight (DEFAULT)
    lambda_nonneg: float = 0.0,  # Non-negative penalty weight for MSE decoder
    gene_weights: Optional[np.ndarray] = None,  # Phase 4: Gene importance weights
    X_raw: Optional[np.ndarray] = None,  # Raw counts for NB loss
    library_size: Optional[np.ndarray] = None,  # Library size per cell for NB
    normalize_teacher: bool = False,
    device: str = 'cpu',
    verbose: bool = True,
    early_stopping: bool = True,
    patience: int = 10,
    min_delta: float = 1e-4,
) -> Dict[str, list]:
    """Train MLP to reproduce teacher's batch-corrected embeddings (distillation).

    This function trains the student MLP to:
    1. Reproduce the teacher's embeddings (distillation loss)
    2. Reconstruct the original expression (reconstruction loss)
    3. Preserve gene-wise correlation patterns (optional, recommended)

    Parameters
    ----------
    model : DistillationMLP
        MLP model to train
    X : np.ndarray
        Input features (N, input_dim).
        - For ZINB models (reconstruction_loss='zinb'): raw counts
        - For MSE models (reconstruction_loss='mse'): log-normalized expression
    Z_teacher : np.ndarray
        Teacher's batch-corrected embeddings (N, latent_dim)
    n_epochs : int, default=200
        Number of training epochs
    learning_rate : float, default=1e-3
        Learning rate
    lambda_recon : float, default=1.0
        Reconstruction loss weight
    lambda_cosine : float, default=2.0
        Cosine similarity loss weight for pattern matching.
        Higher values enforce direction/pattern alignment over magnitude.
        Useful for preserving small biological signals (LFC < 0.5).
        Set to 0.0 to disable.
    lambda_corr : float, default=1.0
        Gene-wise correlation loss weight (shift/scale invariant).

        **This is enabled by default for optimal variance preservation.**

        This loss uses Pearson correlation per gene, which provides:
        - Shift invariance: Ignores batch-specific baseline differences
        - Scale invariance: Ignores batch-specific amplitude scaling
        - Pattern focus: Preserves relative variation across cells
        - Democratic treatment: All genes weighted equally (no bias)

        Phase 3 breakthrough results:
        - Variance preservation: 27.8% → 41.2% (+48%)
        - DEG F1 score: 0.077 → 0.179 (+131%)
        - Batch correction maintained: Silhouette > 0.99
    lambda_nonneg : float, default=0.0
        Non-negative penalty weight for MSE decoder outputs.
        Penalizes negative values in reconstruction: mean(ReLU(-X_recon)^2)
        Only applies to MSE reconstruction (ignored for ZINB).
        Recommended range: 1.0-10.0 for reducing negative outputs.
    gene_weights : np.ndarray, optional
        **EXPERIMENTAL**: Per-gene importance weights (N_genes,).
        If provided, uses weighted correlation loss.
        Default None uses uniform weights (recommended).
    X_raw : np.ndarray, optional
        Raw integer counts (N, input_dim). Required for NB reconstruction loss.
        Must be provided when reconstruction_loss='nb'.
    library_size : np.ndarray, optional
        Total counts per cell (N,). Required for NB reconstruction loss.
        Used to compute μ = scale × library_size.
        Must be provided when reconstruction_loss='nb'.
    normalize_teacher : bool, default=False
        Normalize teacher embeddings to zero mean and unit variance per dimension.
        Required for teachers with small-scale embeddings (fastMNN, LIGER).
        Teachers like Harmony and Symphony have normal scale and don't need this.
    device : str, default='cpu'
        Device
    verbose : bool, default=True
        Print progress
    early_stopping : bool, default=True
        Enable early stopping based on loss improvement
    patience : int, default=10
        Number of epochs to wait for improvement before stopping
    min_delta : float, default=1e-4
        Minimum improvement to count as progress

    Returns
    -------
    history : Dict[str, list]
        Training history with keys: 'epoch', 'loss_total', 'loss_distillation',
        'loss_cosine', 'loss_corr', 'loss_reconstruction'

    Notes
    -----
    **Input Data Requirements:**
    - For ZINB models: pass raw counts (integers). Internally log1p transformed.
    - For MSE models: pass log-normalized expression.

    **Recommended Configuration:**

    >>> # ZINB model (default) - use raw counts
    >>> model = DistillationMLP(input_dim=n_genes, latent_dim=50)
    >>> history = train_distillation(
    ...     model=model,
    ...     X=X_raw_counts,
    ...     Z_teacher=Z_harmony,
    ...     lambda_cosine=2.0,
    ...     lambda_corr=1.0,
    ...     n_epochs=200
    ... )
    >>>
    >>> # MSE model (legacy) - use log-normalized
    >>> model = DistillationMLP(input_dim=n_genes, reconstruction_loss='mse')
    >>> history = train_distillation(
    ...     model=model,
    ...     X=X_normalized,
    ...     Z_teacher=Z_harmony,
    ...     ...
    ... )

    The `normalize_teacher` option is needed for teachers that produce
    small-scale embeddings:
    - fastMNN: mean_norm ≈ 0.45 (needs normalization)
    - LIGER: mean_norm ≈ 0.05 (needs normalization)
    - Harmony: mean_norm ≈ 25-35 (no normalization needed)
    - Symphony: mean_norm ≈ 24 (no normalization needed)
    """
    model = model.to(device)

    # Normalize teacher embeddings if requested
    if normalize_teacher:
        Z_mean = np.mean(Z_teacher, axis=0, keepdims=True)
        Z_std = np.std(Z_teacher, axis=0, keepdims=True)
        Z_std = np.where(Z_std < 1e-6, 1.0, Z_std)
        Z_teacher_normalized = (Z_teacher - Z_mean) / Z_std

        if verbose:
            orig_norm = np.mean(np.linalg.norm(Z_teacher, axis=1))
            norm_norm = np.mean(np.linalg.norm(Z_teacher_normalized, axis=1))
            print(f"  Teacher normalization: {orig_norm:.2f} → {norm_norm:.2f} (mean L2 norm)")

        Z_teacher = Z_teacher_normalized

    # Convert to tensors
    x = torch.from_numpy(X).float().to(device)
    z_teacher = torch.from_numpy(Z_teacher).float().to(device)

    # Convert NB-specific tensors if provided
    x_raw_tensor = None
    lib_tensor = None
    if X_raw is not None:
        x_raw_tensor = torch.from_numpy(X_raw).float().to(device)
    if library_size is not None:
        lib_tensor = torch.from_numpy(library_size).float().to(device)

    # Validate NB requirements
    if model.reconstruction_loss == 'nb':
        if x_raw_tensor is None or lib_tensor is None:
            raise ValueError(
                "reconstruction_loss='nb' requires X_raw and library_size parameters. "
                "X_raw should be raw integer counts, library_size should be total counts per cell."
            )

    # Convert gene weights to tensor if provided
    gene_weights_tensor = None
    if gene_weights is not None:
        gene_weights_tensor = torch.from_numpy(gene_weights).float().to(device)

    # Optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # Training history
    history = {
        'epoch': [],
        'loss_total': [],
        'loss_distillation': [],
        'loss_cosine': [],
        'loss_norm': [],
        'loss_corr': [],  # Phase 3: Gene-wise correlation loss
        'loss_nonneg': [],  # Non-negative penalty
        'loss_reconstruction': []
    }

    # Early stopping state
    best_loss = float('inf')
    patience_counter = 0
    best_state = None

    if verbose:
        print(f"Training Distillation MLP:")
        print(f"  Epochs: {n_epochs}, LR: {learning_rate}")
        print(f"  λ_recon: {lambda_recon}, λ_cosine: {lambda_cosine}, λ_corr: {lambda_corr}")
        if lambda_nonneg > 0:
            print(f"  λ_nonneg: {lambda_nonneg} (non-negative penalty enabled)")
        if early_stopping:
            print(f"  Early stopping: patience={patience}, min_delta={min_delta}")

    # Use tqdm for progress tracking
    epoch_iter = tqdm(range(n_epochs), desc="Training", disable=not verbose)

    for epoch in epoch_iter:
        model.train()
        optimizer.zero_grad()

        # Forward pass (encode)
        U = model(x)

        # Distillation loss: MSE (magnitude matching)
        loss_distillation = F.mse_loss(U, z_teacher)

        # Cosine similarity loss: Pattern matching (direction alignment)
        if lambda_cosine > 0:
            cosine_sim = F.cosine_similarity(U, z_teacher, dim=1).mean()
            loss_cosine = 1.0 - cosine_sim
        else:
            loss_cosine = torch.tensor(0.0, device=U.device)

        # Norm consistency loss: Magnitude matching (force same L2 norm)
        if lambda_norm > 0:
            u_norm = torch.norm(U, p=2, dim=1)
            z_norm = torch.norm(z_teacher, p=2, dim=1)
            loss_norm = F.mse_loss(u_norm, z_norm)
        else:
            loss_norm = torch.tensor(0.0, device=U.device)

        # Reconstruction loss: Decode and reconstruct expression
        if model.reconstruction_loss == 'zinb':
            # ZINB NLL loss for count data
            from .zinb import zinb_nll
            mu, theta, pi = model.decode_zinb_params(U)
            loss_recon = zinb_nll(x, mu, theta, pi, reduction='mean')
            x_recon = mu * (1 - pi)  # Expected value for correlation loss
        elif model.reconstruction_loss == 'nb':
            # NB NLL loss for count data (with library size injection)
            # μ = scale × library_size
            from .zinb import nb_nll
            mu, theta = model.decode_nb_params(U, lib_tensor)
            # NB loss is computed against raw counts
            loss_recon = nb_nll(x_raw_tensor, mu, theta, reduction='mean')
            # For correlation loss, transform μ to log-normalized space
            # This matches the input X (log-normalized) for fair comparison
            mu_normalized = mu / (mu.sum(dim=1, keepdim=True) + 1e-8) * 10000
            x_recon = torch.log1p(mu_normalized)
        else:
            # MSE loss for log-normalized data
            x_recon = model.decode(U)
            loss_recon = F.mse_loss(x_recon, x)

        # Gene-wise Correlation Loss - Phase 3/4
        if lambda_corr > 0:
            if gene_weights_tensor is not None:
                # Phase 4: Weighted correlation loss
                loss_corr = weighted_gene_wise_correlation_loss(x_recon, x, gene_weights_tensor)
            else:
                # Phase 3: Uniform correlation loss
                loss_corr = gene_wise_correlation_loss(x_recon, x)
        else:
            loss_corr = torch.tensor(0.0, device=U.device)

        # Non-negative penalty (MSE decoder only)
        if lambda_nonneg > 0 and model.reconstruction_loss == 'mse':
            # Penalize negative values: mean(ReLU(-x_recon)^2)
            loss_nonneg = torch.mean(F.relu(-x_recon) ** 2)
        else:
            loss_nonneg = torch.tensor(0.0, device=U.device)

        # Total loss
        loss = (loss_distillation +
                lambda_cosine * loss_cosine +
                lambda_norm * loss_norm +
                lambda_recon * loss_recon +
                lambda_corr * loss_corr +
                lambda_nonneg * loss_nonneg)

        # Backward pass
        loss.backward()
        optimizer.step()

        # Record history
        history['epoch'].append(epoch)
        history['loss_total'].append(loss.item())
        history['loss_distillation'].append(loss_distillation.item())
        history['loss_cosine'].append(loss_cosine.item())
        history['loss_norm'].append(loss_norm.item())
        history['loss_corr'].append(loss_corr.item())
        history['loss_nonneg'].append(loss_nonneg.item())
        history['loss_reconstruction'].append(loss_recon.item())

        # Update tqdm description with current loss
        if lambda_cosine > 0 or lambda_norm > 0 or lambda_corr > 0 or lambda_nonneg > 0:
            postfix_dict = {
                'loss': f"{loss.item():.4f}",
                'distill': f"{loss_distillation.item():.4f}",
                'recon': f"{loss_recon.item():.4f}"
            }
            if lambda_cosine > 0:
                postfix_dict['cosine'] = f"{loss_cosine.item():.4f}"
            if lambda_norm > 0:
                postfix_dict['norm'] = f"{loss_norm.item():.4f}"
            if lambda_corr > 0:
                postfix_dict['corr'] = f"{loss_corr.item():.4f}"
            if lambda_nonneg > 0:
                postfix_dict['nonneg'] = f"{loss_nonneg.item():.6f}"
            epoch_iter.set_postfix(**postfix_dict)
        else:
            epoch_iter.set_postfix(
                loss=f"{loss.item():.4f}",
                distill=f"{loss_distillation.item():.4f}",
                recon=f"{loss_recon.item():.4f}"
            )

        # Early stopping check
        if early_stopping:
            if loss.item() < best_loss - min_delta:
                best_loss = loss.item()
                patience_counter = 0
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    epoch_iter.close()
                    if verbose:
                        print(f"Early stopping at epoch {epoch + 1} (no improvement for {patience} epochs)")
                    # Restore best state
                    if best_state is not None:
                        model.load_state_dict(best_state)
                    break

    return history


def get_embedding(
    model: DistillationMLP,
    X: np.ndarray,
    device: str = 'cpu',
) -> np.ndarray:
    """Get embeddings from trained model.

    Parameters
    ----------
    model : DistillationMLP
        Trained model
    X : np.ndarray
        Input features (N, input_dim)
    device : str
        Device

    Returns
    -------
    U : np.ndarray
        Latent embeddings (N, latent_dim)
    """
    model = model.to(device)
    model.eval()

    x = torch.from_numpy(X).float().to(device)

    with torch.no_grad():
        U = model(x)

    return U.cpu().numpy()


def get_reconstructed_expression(
    model: DistillationMLP,
    X: np.ndarray,
    device: str = 'cpu',
    gene_indices: Optional[np.ndarray] = None,
    target_sum: float = 1e4,
) -> np.ndarray:
    """Get reconstructed expression from trained model.

    Parameters
    ----------
    model : DistillationMLP
        Trained model
    X : np.ndarray
        Input features (N, input_dim)
    device : str
        Device
    gene_indices : np.ndarray, optional
        Indices of genes to decode. If None, decode all genes.
        When specified, only computes output for selected genes
        (more efficient than decoding all then subsetting).
    target_sum : float, default=1e4
        Target sum for log-normalization (used for NB mode).

    Returns
    -------
    X_recon : np.ndarray
        Reconstructed expression (N, n_genes or len(gene_indices))
        - For MSE: log-normalized expression
        - For NB: log-normalized expression (transformed from scale)
        - For ZINB: expected counts μ*(1-π)
    """
    model = model.to(device)
    model.eval()

    x = torch.from_numpy(X).float().to(device)

    with torch.no_grad():
        # Encode
        U = model(x)

        # Handle NB mode specially: get scale and transform to log-normalized
        if model.reconstruction_loss == 'nb':
            # Get scale (proportion) - no library_size needed
            scale = model.decode_nb_scale(U)
            # Transform to log-normalized space: log1p(scale * target_sum)
            # This makes output comparable to log-normalized input
            X_recon = torch.log1p(scale * target_sum)

            if gene_indices is not None:
                gene_idx = torch.tensor(gene_indices, dtype=torch.long, device=device)
                X_recon = X_recon[:, gene_idx]

        elif gene_indices is not None:
            # Efficient gene-specific decoding (for non-NB modes):
            # Run all hidden layers, then selectively compute final layer
            gene_idx = torch.tensor(gene_indices, dtype=torch.long, device=device)

            # Process through all layers except the last
            decoder_layers = list(model.decoder.children())
            h = U
            for layer in decoder_layers[:-1]:
                h = layer(h)

            # For final linear layer, compute only selected genes
            final_layer = decoder_layers[-1]
            W_subset = final_layer.weight[gene_idx, :]  # (n_selected, hidden)
            b_subset = final_layer.bias[gene_idx]  # (n_selected,)
            X_recon = torch.mm(h, W_subset.T) + b_subset
        else:
            X_recon = model.decode(U)

    return X_recon.cpu().numpy()


def pretrain_zinb_autoencoder(
    model: DistillationMLP,
    X: np.ndarray,
    n_epochs: int = 100,
    learning_rate: float = 1e-3,
    device: str = 'cpu',
    verbose: bool = True,
    early_stopping: bool = True,
    patience: int = 10,
    min_delta: float = 1e-4,
) -> Dict[str, list]:
    """Pre-train ZINB autoencoder with reconstruction loss only.

    This is Stage 1 of the 2-stage ZINB approach:
    1. Pre-train: Learn encoder/decoder with ZINB NLL (no distillation)
    2. Harmony: Apply Harmony to encoder output Z
    3. Fine-tune: Distill Harmony-corrected Z* into the model

    Parameters
    ----------
    model : DistillationMLP
        ZINB model to pre-train (reconstruction_loss='zinb' required)
    X : np.ndarray
        Raw count input (N, n_genes)
    n_epochs : int, default=100
        Number of pre-training epochs
    learning_rate : float, default=1e-3
        Learning rate
    device : str, default='cpu'
        Device
    verbose : bool, default=True
        Print progress
    early_stopping : bool, default=True
        Enable early stopping
    patience : int, default=10
        Epochs to wait for improvement
    min_delta : float, default=1e-4
        Minimum improvement threshold

    Returns
    -------
    history : Dict[str, list]
        Training history with 'epoch', 'loss_reconstruction'
    """
    if model.reconstruction_loss != 'zinb':
        raise ValueError("pretrain_zinb_autoencoder requires reconstruction_loss='zinb'")

    model = model.to(device)
    x = torch.from_numpy(X).float().to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    history = {
        'epoch': [],
        'loss_reconstruction': [],
    }

    best_loss = float('inf')
    patience_counter = 0
    best_state = None

    if verbose:
        print(f"Pre-training ZINB Autoencoder:")
        print(f"  Epochs: {n_epochs}, LR: {learning_rate}")
        print(f"  Input shape: {X.shape}")

    epoch_iter = tqdm(range(n_epochs), desc="Pre-training", disable=not verbose)

    for epoch in epoch_iter:
        model.train()
        optimizer.zero_grad()

        # Forward pass
        U = model(x)

        # ZINB reconstruction loss only
        from .zinb import zinb_nll
        mu, theta, pi = model.decode_zinb_params(U)
        loss = zinb_nll(x, mu, theta, pi, reduction='mean')

        # Backward
        loss.backward()
        optimizer.step()

        # Record
        history['epoch'].append(epoch)
        history['loss_reconstruction'].append(loss.item())

        epoch_iter.set_postfix(loss=f"{loss.item():.4f}")

        # Early stopping
        if early_stopping:
            if loss.item() < best_loss - min_delta:
                best_loss = loss.item()
                patience_counter = 0
                best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    epoch_iter.close()
                    if verbose:
                        print(f"Early stopping at epoch {epoch + 1}")
                    if best_state is not None:
                        model.load_state_dict(best_state)
                    break

    if verbose:
        print(f"  Final reconstruction loss: {history['loss_reconstruction'][-1]:.4f}")

    return history


# Backward compatibility aliases
HarmonyMLP = DistillationMLP
train_harmony_distillation = train_distillation

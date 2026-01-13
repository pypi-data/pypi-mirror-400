"""Zero-Inflated Negative Binomial (ZINB) distribution for scRNA-seq data.

This module provides ZINB distribution utilities for modeling single-cell
RNA-seq count data, which exhibits:
- Overdispersion: Variance exceeds mean
- Zero-inflation: Excess zeros from dropout events

The ZINB distribution combines a Bernoulli component (for technical zeros)
with a Negative Binomial component (for biological counts), making it well-suited
for scRNA-seq data modeling.

Note: The current HarmonyDistillationModel uses MSE loss instead of ZINB.
This module is provided for potential future extensions or custom models.

Based on scVI implementation (Lopez et al., Nature Methods 2018).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Normal, Gamma
from typing import Optional


class ZINB:
    """Zero-Inflated Negative Binomial distribution for scRNA-seq counts.

    ZINB models gene expression counts by separating technical dropout
    from biological variation:

    Parameters of the distribution:
    - μ (mu): Mean expression level of the gene
    - θ (theta): Inverse dispersion parameter (higher = less variable)
    - π (pi): Probability of technical dropout (zero-inflation)

    The model works as follows:
    1. With probability π, the count is zero (technical dropout)
    2. With probability (1-π), the count follows NB(μ, θ) distribution

    This two-component mixture captures both:
    - Technical zeros: From RNA capture inefficiency
    - Biological variation: Actual gene expression variability

    Example
    -------
    >>> from scdistill import zinb_nll
    >>> import torch
    >>>
    >>> # Observed counts (2 cells, 3 genes)
    >>> x = torch.tensor([[0, 5, 10], [0, 0, 3]])
    >>>
    >>> # Model parameters
    >>> mu = torch.tensor([[0.1, 5.2, 9.8], [0.2, 0.1, 3.1]])
    >>> theta = torch.tensor([10.0, 10.0, 10.0])
    >>> pi = torch.tensor([[0.9, 0.1, 0.05], [0.8, 0.9, 0.1]])
    >>>
    >>> # Compute loss
    >>> loss = zinb_nll(x, mu, theta, pi)

    Note
    ----
    The current HarmonyDistillationModel uses MSE loss. This ZINB
    implementation is provided for custom models or future extensions.
    """

    @staticmethod
    def log_nb_positive(
        x: torch.Tensor,
        mu: torch.Tensor,
        theta: torch.Tensor,
        eps: float = 1e-8
    ) -> torch.Tensor:
        """Log probability of Negative Binomial for positive counts.

        Args:
            x: Observed counts (N, G)
            mu: Mean parameter (N, G)
            theta: Inverse dispersion (G,) or (N, G)
            eps: Numerical stability constant

        Returns:
            Log probability (N, G)
        """
        # Ensure numerical stability
        mu = mu.clamp(min=eps)
        theta = theta.clamp(min=eps)

        # NB parameterization: p = μ / (μ + θ)
        log_theta_mu_eps = torch.log(theta + mu + eps)

        # Log probability
        log_prob = (
            theta * (torch.log(theta + eps) - log_theta_mu_eps)
            + x * (torch.log(mu + eps) - log_theta_mu_eps)
            + torch.lgamma(x + theta)
            - torch.lgamma(theta)
            - torch.lgamma(x + 1)
        )

        return log_prob

    @staticmethod
    def log_zinb_positive(
        x: torch.Tensor,
        mu: torch.Tensor,
        theta: torch.Tensor,
        pi: torch.Tensor,
        eps: float = 1e-8
    ) -> torch.Tensor:
        """Log probability of ZINB for positive counts.

        For x > 0: log((1-π) * NB(x|μ,θ))

        Args:
            x: Observed counts (N, G)
            mu: Mean parameter (N, G)
            theta: Inverse dispersion (G,) or (N, G)
            pi: Zero-inflation probability (N, G)
            eps: Numerical stability constant

        Returns:
            Log probability (N, G)
        """
        # Case 1: x > 0
        # log P(x > 0) = log(1 - π) + log NB(x|μ,θ)
        log_nb = ZINB.log_nb_positive(x, mu, theta, eps)
        log_prob = torch.log(1 - pi + eps) + log_nb

        return log_prob

    @staticmethod
    def log_zinb_zero(
        mu: torch.Tensor,
        theta: torch.Tensor,
        pi: torch.Tensor,
        eps: float = 1e-8
    ) -> torch.Tensor:
        """Log probability of ZINB for zero counts.

        For x = 0: log(π + (1-π) * NB(0|μ,θ))

        Args:
            mu: Mean parameter (N, G)
            theta: Inverse dispersion (G,) or (N, G)
            pi: Zero-inflation probability (N, G)
            eps: Numerical stability constant

        Returns:
            Log probability (N, G)
        """
        # Case 2: x = 0
        # log P(x = 0) = log(π + (1-π) * NB(0|μ,θ))
        # NB(0|μ,θ) = (θ/(θ+μ))^θ

        mu = mu.clamp(min=eps)
        theta = theta.clamp(min=eps)

        # Compute log NB(0|μ,θ) in numerically stable way
        log_nb_zero = theta * (torch.log(theta + eps) - torch.log(theta + mu + eps))

        # log(π + (1-π) * exp(log_nb_zero))
        # = log(π + (1-π) * nb_zero)
        # Use log-sum-exp trick for stability
        log_prob = torch.log(pi + (1 - pi) * torch.exp(log_nb_zero) + eps)

        return log_prob


def zinb_nll(
    x: torch.Tensor,
    mu: torch.Tensor,
    theta: torch.Tensor,
    pi: torch.Tensor,
    eps: float = 1e-8,
    reduction: str = "mean"
) -> torch.Tensor:
    """Compute negative log-likelihood loss for ZINB distribution.

    This loss function measures how well the ZINB parameters (mu, theta, pi)
    explain the observed count data. Lower values indicate better fit.

    Use this as a reconstruction loss when training models on count data
    instead of MSE loss, which assumes Gaussian errors.

    Parameters
    ----------
    x : torch.Tensor
        Observed gene counts, shape (n_cells, n_genes)
    mu : torch.Tensor
        Predicted mean expression, shape (n_cells, n_genes)
    theta : torch.Tensor
        Inverse dispersion parameter, shape (n_genes,) or (n_cells, n_genes)
        Higher values mean less dispersed (more Poisson-like)
    pi : torch.Tensor
        Zero-inflation probability, shape (n_cells, n_genes)
        Probability of technical dropout for each gene
    eps : float, default=1e-8
        Small constant for numerical stability
    reduction : str, default='mean'
        How to reduce the loss: 'mean', 'sum', or 'none'

    Returns
    -------
    loss : torch.Tensor
        Negative log-likelihood loss (scalar if reduction != 'none')

    Example
    -------
    >>> import torch
    >>> from scdistill import zinb_nll
    >>>
    >>> # Observed counts (2 cells, 3 genes)
    >>> x = torch.tensor([[0, 5, 10], [0, 0, 3]])
    >>>
    >>> # Model predictions
    >>> mu = torch.tensor([[0.1, 5.2, 9.8], [0.2, 0.1, 3.1]])
    >>> theta = torch.tensor([10.0, 10.0, 10.0])  # One value per gene
    >>> pi = torch.tensor([[0.9, 0.1, 0.05], [0.8, 0.9, 0.1]])
    >>>
    >>> # Compute loss
    >>> loss = zinb_nll(x, mu, theta, pi)
    >>> print(f"Loss: {loss.item():.4f}")

    Note
    ----
    The current HarmonyDistillationModel uses MSE loss. This function is
    provided for users building custom models that require count-based losses.
    """
    # Separate zero and non-zero cases
    zero_mask = (x < eps).float()

    # Log probability for zeros
    log_prob_zero = ZINB.log_zinb_zero(mu, theta, pi, eps)

    # Log probability for positive counts
    log_prob_pos = ZINB.log_zinb_positive(x, mu, theta, pi, eps)

    # Combine using mask
    log_prob = zero_mask * log_prob_zero + (1 - zero_mask) * log_prob_pos

    # Negative log-likelihood
    nll = -log_prob

    # Apply reduction
    if reduction == "mean":
        return nll.mean()
    elif reduction == "sum":
        return nll.sum()
    elif reduction == "none":
        return nll
    else:
        raise ValueError(f"Unknown reduction: {reduction}")


class ZINBDecoder(nn.Module):
    """Decoder that outputs ZINB parameters (μ, θ, π).

    Maps latent Z to ZINB parameters for each gene. Used with raw count input
    instead of Gaussian decoder (MSE loss).

    Parameters
    ----------
    latent_dim : int
        Dimension of latent space
    output_dim : int
        Number of genes
    hidden_dim : int, default=128
        Hidden layer size
    n_layers : int, default=2
        Number of layers
    """

    def __init__(
        self,
        latent_dim: int,
        output_dim: int,
        hidden_dim: int = 128,
        n_layers: int = 2,
    ):
        super().__init__()

        self.latent_dim = latent_dim
        self.output_dim = output_dim

        # Shared hidden layers
        layers = []
        in_dim = latent_dim
        for _ in range(n_layers - 1):
            layers.append(nn.Linear(in_dim, hidden_dim))
            layers.append(nn.ReLU())
            in_dim = hidden_dim

        self.hidden = nn.Sequential(*layers) if layers else nn.Identity()

        # Output heads
        final_in = hidden_dim if n_layers > 1 else latent_dim

        # μ (mean): must be positive → use softplus
        self.mu_head = nn.Linear(final_in, output_dim)

        # θ (dispersion): must be positive → use softplus
        self.theta_head = nn.Linear(final_in, output_dim)

        # π (dropout): must be in [0,1] → use sigmoid
        self.pi_head = nn.Linear(final_in, output_dim)

    def forward(self, z: torch.Tensor) -> tuple:
        """Decode latent to ZINB parameters.

        Parameters
        ----------
        z : torch.Tensor
            Latent representation (N, latent_dim)

        Returns
        -------
        mu : torch.Tensor
            Mean expression (N, output_dim)
        theta : torch.Tensor
            Dispersion (N, output_dim)
        pi : torch.Tensor
            Dropout probability (N, output_dim)
        """
        h = self.hidden(z)

        # Apply appropriate activations
        mu = F.softplus(self.mu_head(h))  # Positive
        theta = F.softplus(self.theta_head(h))  # Positive
        pi = torch.sigmoid(self.pi_head(h))  # [0, 1]

        return mu, theta, pi

    def get_mean(self, z: torch.Tensor) -> torch.Tensor:
        """Get expected expression (μ * (1 - π)).

        This is the "denoised" expression estimate accounting for dropout.
        """
        mu, theta, pi = self.forward(z)
        return mu * (1 - pi)


def nb_nll(
    x: torch.Tensor,
    mu: torch.Tensor,
    theta: torch.Tensor,
    eps: float = 1e-8,
    reduction: str = "mean"
) -> torch.Tensor:
    """Compute negative log-likelihood loss for Negative Binomial distribution.

    Simpler than ZINB (no zero-inflation parameter π). Often sufficient for
    scRNA-seq data and more stable to train.

    Parameters
    ----------
    x : torch.Tensor
        Observed gene counts, shape (n_cells, n_genes)
    mu : torch.Tensor
        Predicted mean expression, shape (n_cells, n_genes)
    theta : torch.Tensor
        Inverse dispersion parameter, shape (n_genes,) or (n_cells, n_genes)
        Higher values mean less dispersed (more Poisson-like)
    eps : float, default=1e-8
        Small constant for numerical stability
    reduction : str, default='mean'
        How to reduce the loss: 'mean', 'sum', or 'none'

    Returns
    -------
    loss : torch.Tensor
        Negative log-likelihood loss
    """
    # Use the existing NB log probability function
    log_prob = ZINB.log_nb_positive(x, mu, theta, eps)

    # Negative log-likelihood
    nll = -log_prob

    # Apply reduction
    if reduction == "mean":
        return nll.mean()
    elif reduction == "sum":
        return nll.sum()
    elif reduction == "none":
        return nll
    else:
        raise ValueError(f"Unknown reduction: {reduction}")


class NBDecoder(nn.Module):
    """Negative Binomial decoder with Library Size injection for raw count reconstruction.

    This decoder follows the scVI-style architecture:
    - Input: Log-normalized expression (for stable encoder training)
    - Output: Scale (proportion) + Library Size → μ (raw count mean)
    - Target: Raw integer counts

    Architecture:
        Z (Harmony space) → Adapter (BatchNorm + Linear) → Hidden → Scale (softmax)
        μ = Scale × Library_Size

    The key insight is that we predict the PROPORTION of expression per gene,
    then multiply by the cell's total counts (library size) to get the expected
    raw count. This is mathematically correct for NB distribution.

    Parameters
    ----------
    latent_dim : int
        Dimension of latent space (PCA/Harmony)
    output_dim : int
        Number of genes
    hidden_dim : int, default=128
        Hidden layer size
    n_layers : int, default=2
        Number of decoder layers (excluding adapter)
    adapter_dim : int, optional
        Dimension of adapter output. If None, uses hidden_dim.
    """

    def __init__(
        self,
        latent_dim: int,
        output_dim: int,
        hidden_dim: int = 128,
        n_layers: int = 2,
        adapter_dim: Optional[int] = None,
    ):
        super().__init__()

        self.latent_dim = latent_dim
        self.output_dim = output_dim
        adapter_dim = adapter_dim or hidden_dim

        # Adapter Layer: bridges Harmony/PCA space to decoder space
        self.adapter = nn.Sequential(
            nn.BatchNorm1d(latent_dim),
            nn.Linear(latent_dim, adapter_dim),
            nn.PReLU(),
        )

        # Hidden layers for decoding
        layers = []
        in_dim = adapter_dim
        for _ in range(n_layers - 1):
            layers.append(nn.Linear(in_dim, hidden_dim))
            layers.append(nn.PReLU())
            in_dim = hidden_dim

        self.hidden = nn.Sequential(*layers) if layers else nn.Identity()

        # Output heads
        final_in = hidden_dim if n_layers > 1 else adapter_dim

        # Scale head: predicts proportion of expression per gene
        # Output goes through softmax → sums to 1 across genes
        self.scale_head = nn.Linear(final_in, output_dim)

        # θ (dispersion): learnable per-gene parameter
        # exp() ensures positive, initialized to reasonable values
        self.log_theta = nn.Parameter(torch.zeros(output_dim))

    def forward(
        self,
        z: torch.Tensor,
        library_size: Optional[torch.Tensor] = None,
    ) -> tuple:
        """Decode latent to NB parameters.

        Parameters
        ----------
        z : torch.Tensor
            Latent representation from encoder (N, latent_dim)
        library_size : torch.Tensor, optional
            Total counts per cell (N, 1) or (N,)
            If None, returns scale (proportion) instead of mu.

        Returns
        -------
        mu : torch.Tensor
            Mean expression in raw count space (N, output_dim)
            If library_size is None, returns scale (proportion).
        theta : torch.Tensor
            Dispersion (output_dim,) - per-gene parameter
        """
        # Adapter: transform from Harmony space to decoder space
        h = self.adapter(z)

        # Decode through hidden layers
        h = self.hidden(h)

        # Predict proportion (scale) via softmax
        # This ensures sum across genes = 1
        scale = F.softmax(self.scale_head(h), dim=1)

        # Dispersion (positive via exp)
        theta = torch.exp(self.log_theta)

        # Compute mean: mu = scale * library_size
        if library_size is not None:
            if library_size.dim() == 1:
                library_size = library_size.unsqueeze(1)  # (N,) -> (N, 1)
            mu = scale * library_size
        else:
            mu = scale  # Return proportion if no library size

        return mu, theta

    def get_mean(
        self,
        z: torch.Tensor,
        library_size: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Get expected expression (μ).

        Parameters
        ----------
        z : torch.Tensor
            Latent representation (N, latent_dim)
        library_size : torch.Tensor, optional
            Total counts per cell (N, 1) or (N,)

        Returns
        -------
        mu : torch.Tensor
            Expected raw counts (N, output_dim)
        """
        mu, _ = self.forward(z, library_size)
        return mu

    def get_scale(self, z: torch.Tensor) -> torch.Tensor:
        """Get expression proportion (scale) without library size.

        This is useful for comparing relative expression patterns
        independent of sequencing depth.

        Parameters
        ----------
        z : torch.Tensor
            Latent representation (N, latent_dim)

        Returns
        -------
        scale : torch.Tensor
            Expression proportions (N, output_dim), sum to 1 per cell
        """
        mu, _ = self.forward(z, library_size=None)
        return mu

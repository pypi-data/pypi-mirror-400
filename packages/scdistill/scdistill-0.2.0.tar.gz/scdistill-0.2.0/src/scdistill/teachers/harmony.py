"""Harmony teacher with covariate protection.

This module provides HarmonyTeacher, a batch correction teacher that uses
the Harmony algorithm with optional covariate protection.

The key insight is:
- Clustering step uses all variables (batch + covariate)
- Correction step (moe_correct_ridge) uses only batch → covariate is protected

This allows removing batch effects while preserving biological covariates
like age, treatment dose, etc.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from typing import Optional
import logging

from .base import BaseTeacher

logger = logging.getLogger('harmony_teacher')


class HarmonyWithProtection:
    """Harmony algorithm with covariate protection.

    This is an implementation of Harmony (Korsunsky et al., Nature Methods 2019)
    with the ability to protect specified covariates during batch correction.

    Key difference from standard Harmony:
    - Phi_moe is split into Phi_moe_batch (batch only) and Phi_moe_full (all variables)
    - Clustering uses Phi_moe_full (includes covariate)
    - Correction uses only Phi_moe_batch (excludes covariate → protected)

    Parameters
    ----------
    n_clusters : int, default=100
        Number of clusters
    theta_batch : float, default=2.0
        Diversity penalty for batch
    theta_covariate : float, default=2.0
        Diversity penalty for covariate (clustering only)
    sigma : float, default=0.1
        Soft clustering temperature
    max_iter_harmony : int, default=10
        Maximum Harmony iterations
    max_iter_kmeans : int, default=20
        Maximum k-means iterations per Harmony iteration
    epsilon_harmony : float, default=1e-4
        Convergence threshold
    block_size : float, default=0.05
        Block size for R updates
    lamb : float, default=1.0
        Ridge regression regularization
    verbose : bool, default=True
        Print progress
    random_state : int, default=0
        Random seed
    """

    def __init__(
        self,
        n_clusters: int = 100,
        theta_batch: float = 2.0,
        theta_covariate: float = 2.0,
        sigma: float = 0.1,
        max_iter_harmony: int = 10,
        max_iter_kmeans: int = 20,
        epsilon_harmony: float = 1e-4,
        epsilon_kmeans: float = 1e-5,
        block_size: float = 0.05,
        lamb: float = 1.0,
        verbose: bool = True,
        random_state: int = 0
    ):
        self.n_clusters = n_clusters
        self.theta_batch = theta_batch
        self.theta_covariate = theta_covariate
        self.sigma = sigma
        self.max_iter_harmony = max_iter_harmony
        self.max_iter_kmeans = max_iter_kmeans
        self.epsilon_harmony = epsilon_harmony
        self.epsilon_kmeans = epsilon_kmeans
        self.block_size = block_size
        self.lamb = lamb
        self.verbose = verbose
        self.random_state = random_state

        # Internal state
        self.Z_orig = None
        self.Z_corr = None
        self.Z_cos = None
        self.R = None
        self.Y = None

    def _log(self, msg: str):
        if self.verbose:
            print(msg)

    def fit_transform(
        self,
        Z: np.ndarray,
        batch_labels: np.ndarray,
        covariate_values: Optional[np.ndarray] = None,
        n_covariate_bins: int = 6
    ) -> np.ndarray:
        """Run Harmony with covariate protection.

        Parameters
        ----------
        Z : np.ndarray
            PCA embeddings (N, d) or (d, N)
        batch_labels : np.ndarray
            Batch labels (N,)
        covariate_values : np.ndarray, optional
            Covariate values to protect (N,). Can be continuous or discrete.
        n_covariate_bins : int, default=6
            Number of bins for continuous covariates

        Returns
        -------
        Z_corr : np.ndarray
            Corrected embeddings (d, N)
        """
        # Ensure (d, N) format
        if Z.shape[0] > Z.shape[1]:
            Z = Z.T

        d, N = Z.shape
        self.Z_orig = Z.copy()
        self.Z_corr = Z.copy()

        # Adjust cluster count
        K = min(self.n_clusters, N // 30)
        K = max(K, 10)
        self.K = K

        self._log(f"Harmony with Protection: {N} cells, {d} dims, {K} clusters")

        # One-hot encode batch
        batch_df = pd.DataFrame({'batch': batch_labels})
        Phi_batch = pd.get_dummies(batch_df['batch']).to_numpy().T  # (B, N)
        n_batches = Phi_batch.shape[0]
        self._log(f"  Batches: {n_batches}")

        # One-hot encode covariate (if specified)
        if covariate_values is not None and n_covariate_bins > 1:
            # Discrete vs continuous detection
            unique_vals = np.unique(covariate_values[~pd.isna(covariate_values)])
            is_discrete = (
                len(unique_vals) <= n_covariate_bins or
                not np.issubdtype(np.array(covariate_values).dtype, np.floating)
            )

            if is_discrete:
                # Discrete: use as-is
                cov_df = pd.DataFrame({'cov': np.array(covariate_values).astype(str)})
                self._log(f"  Covariate type: discrete ({len(unique_vals)} categories)")
            else:
                # Continuous: bin
                cov_bins = pd.cut(covariate_values, bins=n_covariate_bins, labels=False)
                cov_df = pd.DataFrame({'cov': cov_bins.astype(str)})
                self._log(f"  Covariate type: continuous (binned to {n_covariate_bins} bins)")

            Phi_cov = pd.get_dummies(cov_df['cov']).to_numpy().T  # (C, N)
            n_cov_bins = Phi_cov.shape[0]
            self._log(f"  Covariate categories: {n_cov_bins}")
        else:
            Phi_cov = None
            n_cov_bins = 0
            self._log(f"  Covariate bins: 0 (no protection)")

        self._log(f"  theta_batch={self.theta_batch}, theta_covariate={self.theta_covariate}")
        if Phi_cov is not None:
            self._log(f"  Covariate will be PROTECTED (not removed in correction step)")

        # === Design matrices ===

        # For clustering: all variables
        if Phi_cov is not None:
            Phi_full = np.vstack([Phi_batch, Phi_cov])  # (B+C, N)
            theta_full = np.concatenate([
                np.full(n_batches, self.theta_batch),
                np.full(n_cov_bins, self.theta_covariate)
            ])
        else:
            Phi_full = Phi_batch
            theta_full = np.full(n_batches, self.theta_batch)

        # For correction: batch only (covariate excluded = protected)
        Phi_moe_batch = np.vstack([np.ones((1, N)), Phi_batch])  # (1+B, N)
        lamb_batch = np.diag(np.insert(np.full(n_batches, self.lamb), 0, 0))

        # Pr_b: proportion of each category
        Pr_b_full = Phi_full.sum(axis=1) / N

        # Sigma array
        sigma = np.full(K, self.sigma)

        # === Initialization ===
        # Z_cos: L2 normalized
        self.Z_cos = self.Z_corr / np.linalg.norm(self.Z_corr, ord=2, axis=0)

        # Initialize cluster centers with k-means
        np.random.seed(self.random_state)
        kmeans = KMeans(n_clusters=K, init='k-means++', n_init=10, max_iter=25,
                        random_state=self.random_state)
        kmeans.fit(self.Z_cos.T)
        self.Y = kmeans.cluster_centers_.T  # (d, K)
        self.Y = self.Y / np.linalg.norm(self.Y, ord=2, axis=0)

        # R: soft cluster assignments
        dist_mat = 2 * (1 - np.dot(self.Y.T, self.Z_cos))  # (K, N)
        self.R = -dist_mat / sigma[:, None]
        self.R -= np.max(self.R, axis=0)
        self.R = np.exp(self.R)
        self.R = self.R / np.sum(self.R, axis=0)

        # O, E: diversity statistics
        E = np.outer(np.sum(self.R, axis=1), Pr_b_full)  # (K, B+C)
        O = np.dot(self.R, Phi_full.T)  # (K, B+C)

        # === Harmony iterations ===
        objective_harmony = []

        for iter_h in range(1, self.max_iter_harmony + 1):
            # --- Clustering step (uses all variables) ---
            for iter_k in range(self.max_iter_kmeans):
                # Update Y
                self.Y = np.dot(self.Z_cos, self.R.T)
                self.Y = self.Y / np.linalg.norm(self.Y, ord=2, axis=0)

                # Update distance matrix
                dist_mat = 2 * (1 - np.dot(self.Y.T, self.Z_cos))

                # Update R (block-wise)
                scale_dist = -dist_mat / sigma[:, None]
                scale_dist -= np.max(scale_dist, axis=0)
                scale_dist = np.exp(scale_dist)

                update_order = np.random.permutation(N)
                n_blocks = max(1, int(np.ceil(1 / self.block_size)))
                blocks = np.array_split(update_order, n_blocks)

                for b in blocks:
                    # 1. Remove cells
                    E -= np.outer(np.sum(self.R[:, b], axis=1), Pr_b_full)
                    O -= np.dot(self.R[:, b], Phi_full[:, b].T)

                    # 2. Recompute R (with diversity penalty)
                    self.R[:, b] = scale_dist[:, b]
                    # Penalty: (E+1)/(O+1)^theta
                    penalty = np.power((E + 1) / (O + 1), theta_full)
                    self.R[:, b] *= np.dot(penalty, Phi_full[:, b])
                    self.R[:, b] /= np.sum(self.R[:, b], axis=0)

                    # 3. Add cells back
                    E += np.outer(np.sum(self.R[:, b], axis=1), Pr_b_full)
                    O += np.dot(self.R[:, b], Phi_full[:, b].T)

            # --- Correction step (uses batch only = covariate protected) ---
            self.Z_corr = self.Z_orig.copy()
            for k in range(K):
                Phi_Rk = Phi_moe_batch * self.R[k, :]  # (1+B, N)
                x = np.dot(Phi_Rk, Phi_moe_batch.T) + lamb_batch
                W = np.dot(np.linalg.inv(x), np.dot(Phi_Rk, self.Z_orig.T))
                W[0, :] = 0  # Don't remove intercept
                self.Z_corr -= np.dot(W.T, Phi_Rk)

            self.Z_cos = self.Z_corr / np.linalg.norm(self.Z_corr, ord=2, axis=0)

            # Convergence check
            obj = np.sum(self.R * dist_mat)
            objective_harmony.append(obj)

            if iter_h > 1:
                diff = abs(objective_harmony[-2] - objective_harmony[-1])
                self._log(f"  Iteration {iter_h}: max diff = {diff:.6f}")
                if diff < self.epsilon_harmony:
                    self._log(f"  Converged at iteration {iter_h}")
                    break
            else:
                self._log(f"  Iteration {iter_h}: initializing")

        return self.Z_corr


class HarmonyTeacher(BaseTeacher):
    """Harmony batch correction with optional covariate protection.

    Uses HarmonyWithProtection to correct batch effects while preserving
    the effects of specified covariates (e.g., age, treatment).

    Parameters
    ----------
    theta : float, default=2.0
        Diversity penalty for batch correction.
    theta_covariate : float, default=2.0
        Diversity penalty for covariate (clustering only).
    covariate_key : str, optional
        Key in obs for continuous covariate to protect.
    n_covariate_bins : int, default=6
        Number of bins for discretizing continuous covariate.
    max_iter : int, default=10
        Maximum Harmony iterations.

    Examples
    --------
    >>> teacher = HarmonyTeacher(covariate_key='age')
    >>> Z_corrected = teacher.fit_transform(X_pca, batch_labels, adata.obs)
    """

    name = "HarmonyTeacher"

    def __init__(
        self,
        theta: float = 2.0,
        theta_covariate: float = 2.0,
        covariate_key: Optional[str] = None,
        n_covariate_bins: int = 6,
        max_iter: int = 10,
    ):
        super().__init__()
        self.theta = theta
        self.theta_covariate = theta_covariate
        self.covariate_key = covariate_key
        self.n_covariate_bins = n_covariate_bins
        self.max_iter = max_iter

    def fit_transform(
        self,
        X_pca: np.ndarray,
        batch_labels: np.ndarray,
        obs: Optional[pd.DataFrame] = None,
        verbose: bool = True,
        adata=None,
        batch_key: str = "batch",
        **kwargs,
    ) -> np.ndarray:
        """Apply Harmony batch correction.

        Parameters
        ----------
        X_pca : np.ndarray
            PCA embeddings (n_cells, n_pcs).
        batch_labels : np.ndarray
            Batch labels (n_cells,).
        obs : pd.DataFrame, optional
            Cell metadata with covariate column.
        verbose : bool
            Print progress.
        adata : AnnData, optional
            Not used by Harmony (for API compatibility).
        batch_key : str
            Not used by Harmony (for API compatibility).
        **kwargs
            Additional arguments (ignored).

        Returns
        -------
        Z_corrected : np.ndarray
            Harmony-corrected embeddings (n_cells, n_pcs).
        """
        # adata and batch_key not needed for Harmony (uses X_pca and batch_labels directly)
        # Get covariate values if specified
        covariate_values = None
        if self.covariate_key is not None:
            if obs is None:
                raise ValueError(f"obs required when covariate_key='{self.covariate_key}'")
            if self.covariate_key not in obs.columns:
                raise ValueError(f"covariate_key '{self.covariate_key}' not in obs")
            covariate_values = obs[self.covariate_key].values

        if verbose:
            print(f"{self.name}: theta={self.theta}", end="")
            if self.covariate_key:
                print(f", covariate={self.covariate_key}", end="")
            print()

        # Create Harmony instance
        harmony = HarmonyWithProtection(
            n_clusters=100,
            theta_batch=self.theta,
            theta_covariate=self.theta_covariate,
            max_iter_harmony=self.max_iter,
            verbose=verbose
        )

        # Run Harmony
        if covariate_values is not None:
            Z_corr = harmony.fit_transform(
                X_pca,
                batch_labels,
                covariate_values,
                n_covariate_bins=self.n_covariate_bins
            )
        else:
            Z_corr = harmony.fit_transform(
                X_pca,
                batch_labels,
                covariate_values=np.zeros(len(batch_labels)),
                n_covariate_bins=1
            )

        # Output as (N, d)
        if Z_corr.shape[0] < Z_corr.shape[1]:
            Z_corr = Z_corr.T

        self.Z_corrected = Z_corr
        self._is_fitted = True
        return self.Z_corrected

    def __repr__(self) -> str:
        cov = f", covariate_key='{self.covariate_key}'" if self.covariate_key else ""
        return f"HarmonyTeacher(theta={self.theta}{cov})"


# Convenience function (backward compatibility)
def run_harmony_with_protection(
    X_pca: np.ndarray,
    batch_labels: np.ndarray,
    covariate_values: Optional[np.ndarray] = None,
    n_covariate_bins: int = 6,
    theta_batch: float = 2.0,
    theta_covariate: float = 2.0,
    n_clusters: int = 100,
    max_iter: int = 10,
    verbose: bool = True
) -> np.ndarray:
    """Run Harmony with covariate protection.

    This is a convenience function that wraps HarmonyWithProtection.

    Parameters
    ----------
    X_pca : np.ndarray
        PCA embeddings (N, d)
    batch_labels : np.ndarray
        Batch labels (N,)
    covariate_values : np.ndarray, optional
        Covariate values to protect (N,)
    n_covariate_bins : int
        Number of bins for continuous covariate
    theta_batch : float
        Diversity penalty for batch
    theta_covariate : float
        Diversity penalty for covariate
    n_clusters : int
        Number of clusters
    max_iter : int
        Maximum iterations
    verbose : bool
        Print progress

    Returns
    -------
    Z_corr : np.ndarray
        Corrected embeddings (N, d)
    """
    harmony = HarmonyWithProtection(
        n_clusters=n_clusters,
        theta_batch=theta_batch,
        theta_covariate=theta_covariate,
        max_iter_harmony=max_iter,
        verbose=verbose
    )

    Z_corr = harmony.fit_transform(
        X_pca,
        batch_labels,
        covariate_values,
        n_covariate_bins=n_covariate_bins
    )

    # Output as (N, d)
    if Z_corr.shape[0] < Z_corr.shape[1]:
        Z_corr = Z_corr.T

    return Z_corr

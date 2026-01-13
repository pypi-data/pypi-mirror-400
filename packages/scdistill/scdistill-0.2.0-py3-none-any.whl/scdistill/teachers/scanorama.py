"""Scanorama teacher for batch correction."""

import numpy as np
import pandas as pd
from typing import Optional
from .base import BaseTeacher


class ScanoramaTeacher(BaseTeacher):
    """Scanorama batch correction in PCA space.

    Scanorama uses mutual nearest neighbors and singular value decomposition
    to integrate datasets. This teacher applies Scanorama to PCA embeddings.

    Note: Requires the 'scanorama' package to be installed.
    Install with: pip install scanorama

    Parameters
    ----------
    knn : int, default=20
        Number of nearest neighbors.
    sigma : float, default=15
        Correction smoothing parameter.
    approx : bool, default=True
        Use approximate nearest neighbors.
    dimred : int, default=100
        Reduced dimensionality.

    Examples
    --------
    >>> teacher = ScanoramaTeacher()
    >>> Z_corrected = teacher.fit_transform(X_pca, batch_labels)
    """

    name = "ScanoramaTeacher"

    def __init__(
        self,
        knn: int = 20,
        sigma: float = 15,
        approx: bool = True,
        dimred: int = 100,
    ):
        super().__init__()
        self.knn = knn
        self.sigma = sigma
        self.approx = approx
        self.dimred = dimred

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
        """Apply Scanorama batch correction.

        Parameters
        ----------
        X_pca : np.ndarray
            PCA embeddings (n_cells, n_pcs).
        batch_labels : np.ndarray
            Batch labels (n_cells,).
        obs : pd.DataFrame, optional
            Not used.
        verbose : bool
            Print progress.

        Returns
        -------
        Z_corrected : np.ndarray
            Scanorama-corrected embeddings.
        """
        try:
            import scanorama
        except ImportError:
            raise ImportError(
                "ScanoramaTeacher requires the 'scanorama' package. "
                "Install with: pip install scanorama"
            )

        if verbose:
            print(f"{self.name}: knn={self.knn}, sigma={self.sigma}")

        # Split by batch
        unique_batches = np.unique(batch_labels)
        datasets = []
        batch_indices = []

        for batch in unique_batches:
            mask = batch_labels == batch
            datasets.append(X_pca[mask])
            batch_indices.append(np.where(mask)[0])

        # Create dummy gene names (required by scanorama API)
        # Since we're working with PCA embeddings, all "genes" are the same
        n_features = X_pca.shape[1]
        genes_list = [[f"PC{i}" for i in range(n_features)] for _ in datasets]

        # Run Scanorama
        dimred = min(self.dimred, X_pca.shape[1])
        integrated, _ = scanorama.integrate(
            datasets,
            genes_list,
            knn=self.knn,
            sigma=self.sigma,
            approx=self.approx,
            dimred=dimred,
            verbose=1 if verbose else 0
        )

        # Reconstruct full array
        self.Z_corrected = np.zeros((X_pca.shape[0], integrated[0].shape[1]))
        for i, (data, indices) in enumerate(zip(integrated, batch_indices)):
            self.Z_corrected[indices] = data

        self._is_fitted = True

        if verbose:
            print(f"  Corrected shape: {self.Z_corrected.shape}")

        return self.Z_corrected

    def __repr__(self) -> str:
        return f"ScanoramaTeacher(knn={self.knn}, sigma={self.sigma})"

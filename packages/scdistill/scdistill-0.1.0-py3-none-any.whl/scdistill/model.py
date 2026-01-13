"""scDistill: Harmony distillation with covariate protection.

scDistill is a convenience wrapper around Distiller that uses
HarmonyTeacher as the default teacher with covariate protection.

For more flexibility (different teachers), use Distiller directly.

Example
-------
    from scdistill import scDistill

    scDistill.setup_anndata(adata, batch_key='batch', covariate_key='age')
    model = scDistill(adata)
    model.train()

    Z_harmony = model.get_teacher_representation()
    X_corrected = model.get_normalized_expression()
"""

import numpy as np
import pandas as pd
from typing import Optional, List
from anndata import AnnData

from .distiller import Distiller
from .teachers.harmony import HarmonyTeacher


class scDistill(Distiller):
    """Harmony distillation with covariate protection.

    scDistill is the recommended model for batch correction when you
    need to protect continuous covariates (e.g., age, treatment dose).

    This is a convenience wrapper around Distiller that:
    1. Uses HarmonyTeacher with covariate protection
    2. Provides setup_anndata() class method for scVI-like API

    For other teachers (ComBat, Scanorama, etc.), use Distiller directly.

    Parameters
    ----------
    adata : AnnData
        AnnData object (must be setup with setup_anndata first).
    n_hidden : int, default=128
        Hidden layer size.
    n_layers_encoder : int, default=2
        Number of layers in encoder.
    n_layers_decoder : int, default=2
        Number of layers in decoder.
    dropout_rate : float, default=0.1
        Dropout rate.

    Examples
    --------
    >>> scDistill.setup_anndata(adata, batch_key='batch', covariate_key='age')
    >>> model = scDistill(adata)
    >>> model.train(max_epochs=200)
    >>> Z_harmony = model.get_teacher_representation()
    >>> X_corrected = model.get_normalized_expression()
    """

    _setup_registry = {}

    def __init__(
        self,
        adata: AnnData,
        n_hidden: int = 128,
        n_layers_encoder: int = 2,
        n_layers_decoder: int = 2,
        dropout_rate: float = 0.1,
    ):
        # Check setup
        adata_id = id(adata)
        if adata_id not in self._setup_registry:
            raise ValueError(
                "adata not setup. Run scDistill.setup_anndata(adata, ...) first."
            )

        setup_info = self._setup_registry[adata_id]
        batch_key = setup_info['batch_key']
        covariate_key = setup_info.get('covariate_key')

        # Create HarmonyTeacher with covariate protection
        teacher = HarmonyTeacher(covariate_key=covariate_key)

        # Initialize Distiller
        super().__init__(
            adata=adata,
            batch_key=batch_key,
            teacher=teacher,
            n_hidden=n_hidden,
            n_layers_encoder=n_layers_encoder,
            n_layers_decoder=n_layers_decoder,
            dropout_rate=dropout_rate,
        )

        self.covariate_key = covariate_key

    @classmethod
    def setup_anndata(
        cls,
        adata: AnnData,
        batch_key: str,
        covariate_key: Optional[str] = None,
    ):
        """Setup AnnData for scDistill.

        Parameters
        ----------
        adata : AnnData
            AnnData with log-normalized expression.
        batch_key : str
            Key in adata.obs for batch labels.
        covariate_key : str, optional
            Key in adata.obs for continuous covariate to protect.
        """
        if batch_key not in adata.obs:
            raise ValueError(f"batch_key '{batch_key}' not in adata.obs")

        if covariate_key is not None and covariate_key not in adata.obs:
            raise ValueError(f"covariate_key '{covariate_key}' not in adata.obs")

        cls._setup_registry[id(adata)] = {
            'batch_key': batch_key,
            'covariate_key': covariate_key,
        }

        print(f"scDistill setup:")
        print(f"  batch_key: {batch_key}")
        if covariate_key:
            print(f"  covariate_key: {covariate_key} (protected)")
        print(f"  n_cells: {adata.n_obs}, n_genes: {adata.n_vars}")

    def train(
        self,
        max_epochs: int = 200,
        lr: float = 1e-3,
        early_stopping: bool = True,
        patience: int = 10,
        harmony_theta: float = 2.0,
        harmony_theta_covariate: float = 2.0,
        n_covariate_bins: int = 6,
        verbose: bool = True,
    ):
        """Train the model.

        Parameters
        ----------
        max_epochs : int
            Maximum number of epochs.
        lr : float
            Learning rate.
        early_stopping : bool
            Stop training when loss stops improving.
        patience : int
            Number of epochs to wait for improvement.
        harmony_theta : float
            Harmony diversity penalty for batch.
        harmony_theta_covariate : float
            Harmony diversity penalty for covariate.
        n_covariate_bins : int
            Number of bins for covariate.
        verbose : bool
            Print progress.
        """
        # Update teacher parameters
        self.teacher.theta = harmony_theta
        self.teacher.theta_covariate = harmony_theta_covariate
        self.teacher.n_covariate_bins = n_covariate_bins

        # Call parent train
        super().train(
            max_epochs=max_epochs,
            lr=lr,
            early_stopping=early_stopping,
            patience=patience,
            verbose=verbose,
        )

    def __repr__(self) -> str:
        cov = f", covariate={self.covariate_key}" if self.covariate_key else ""
        status = "trained" if self.is_trained else "not trained"
        return f"scDistill(batch={self.batch_key}{cov}, {status})"

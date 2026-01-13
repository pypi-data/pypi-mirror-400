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

    def prepare_teacher(
        self,
        harmony_theta: float = 2.0,
        harmony_theta_covariate: float = 2.0,
        n_covariate_bins: int = 6,
        weighted_pca: bool = False,
        verbose: bool = True,
    ):
        """Prepare teacher (Harmony) embeddings.

        This computes Harmony embeddings once and caches them.
        Call this before train() to separate teacher computation from MLP training.

        Parameters
        ----------
        harmony_theta : float
            Harmony diversity penalty for batch.
        harmony_theta_covariate : float
            Harmony diversity penalty for covariate.
        n_covariate_bins : int
            Number of bins for covariate.
        weighted_pca : bool
            If True, use covariate-weighted PCA. Genes with larger
            differences between covariate groups get higher weights,
            preserving covariate-associated signals in the PCA space.
        verbose : bool
            Print progress.
        """
        # Update teacher parameters
        self.teacher.theta = harmony_theta
        self.teacher.theta_covariate = harmony_theta_covariate
        self.teacher.n_covariate_bins = n_covariate_bins

        # Call parent prepare_teacher with weighted_pca
        super().prepare_teacher(verbose=verbose, weighted_pca=weighted_pca)

    def train(
        self,
        max_epochs: int = 200,
        lr: float = 1e-3,
        early_stopping: bool = True,
        patience: int = 10,
        harmony_theta: float = 2.0,
        harmony_theta_covariate: float = 2.0,
        n_covariate_bins: int = 6,
        weighted_pca: bool = False,
        verbose: bool = True,
    ):
        """Train the model.

        If prepare_teacher() was not called, this will call it first.
        If already trained, this will continue training from current state.

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
        weighted_pca : bool
            If True, use covariate-weighted PCA.
        verbose : bool
            Print progress.
        """
        # If teacher not yet prepared, prepare it now
        if not self._teacher_prepared:
            self.prepare_teacher(
                harmony_theta=harmony_theta,
                harmony_theta_covariate=harmony_theta_covariate,
                n_covariate_bins=n_covariate_bins,
                weighted_pca=weighted_pca,
                verbose=verbose,
            )

        # Call parent train (teacher already prepared, so won't recompute)
        super().train(
            max_epochs=max_epochs,
            lr=lr,
            early_stopping=early_stopping,
            patience=patience,
            verbose=verbose,
        )

    @classmethod
    def load(cls, dir_path: str, adata: Optional[AnnData] = None) -> "scDistill":
        """Load a saved scDistill model.

        Parameters
        ----------
        dir_path : str
            Directory containing saved model files.
        adata : AnnData, optional
            AnnData object to associate with the loaded model.
            Must have setup_anndata called first if provided.

        Returns
        -------
        scDistill
            Loaded model instance.
        """
        import os
        import pickle
        import torch

        # Load config
        with open(os.path.join(dir_path, 'config.pkl'), 'rb') as f:
            config = pickle.load(f)

        gene_names = np.array(config['gene_names'])
        n_genes = len(gene_names)
        batch_key = config.get('batch_key', 'batch')
        covariate_key = config.get('covariate_key')

        # Create minimal AnnData if not provided
        if adata is None:
            adata = AnnData(np.zeros((1, n_genes)))
            adata.var_names = gene_names
            adata.obs[batch_key] = 'dummy'
            if covariate_key:
                adata.obs[covariate_key] = 0.0

        # Setup anndata (registers batch_key and covariate_key)
        cls.setup_anndata(adata, batch_key=batch_key, covariate_key=covariate_key)

        # Create instance
        instance = cls(
            adata=adata,
            n_hidden=config.get('n_hidden', 128),
            n_layers_encoder=config.get('n_layers_encoder', 2),
            n_layers_decoder=config.get('n_layers_decoder', 2),
            dropout_rate=config.get('dropout_rate', 0.1),
        )

        # Set n_latent from config
        instance.n_latent = config.get('n_latent', 50)
        instance._gene_names = gene_names
        instance._total_epochs_trained = config.get('total_epochs_trained', 0)

        # Create module with correct dimensions
        from .nn import DistillationMLP
        instance.module = DistillationMLP(
            input_dim=n_genes,
            latent_dim=instance.n_latent,
            hidden_dim=instance.n_hidden,
            n_layers_encoder=instance.n_layers_encoder,
            n_layers_decoder=instance.n_layers_decoder,
            dropout=instance.dropout_rate,
            reconstruction_loss=instance.reconstruction_loss,
            use_layernorm=instance.use_layernorm,
        ).to(instance.device)

        # Load model weights
        state_dict = torch.load(
            os.path.join(dir_path, 'model.pt'),
            map_location='cpu',
            weights_only=True
        )
        instance.module.load_state_dict(state_dict)
        instance.is_trained = True
        instance._teacher_prepared = True

        # Load teacher embeddings
        z_teacher_path = os.path.join(dir_path, 'Z_teacher.npy')
        if os.path.exists(z_teacher_path):
            instance._Z_teacher = np.load(z_teacher_path)

        # Set _X_input from adata for differential expression
        if hasattr(adata.X, 'toarray'):
            instance._X_input = adata.X.toarray()
        else:
            instance._X_input = np.asarray(adata.X)

        print(f"Loaded scDistill model from {dir_path}")
        print(f"  n_genes: {n_genes}, n_latent: {instance.n_latent}")
        print(f"  epochs_trained: {instance._total_epochs_trained}")

        return instance

    def __repr__(self) -> str:
        cov = f", covariate={self.covariate_key}" if self.covariate_key else ""
        status = "trained" if self.is_trained else "not trained"
        return f"scDistill(batch={self.batch_key}{cov}, {status})"

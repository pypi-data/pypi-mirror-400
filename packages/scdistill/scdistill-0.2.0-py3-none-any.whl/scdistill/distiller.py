"""Generic distillation framework for batch correction.

Distiller learns an MLP to reproduce any teacher's batch correction,
then decodes to gene expression for downstream analysis.

Architecture:
    X (genes) → PCA → Teacher (any) → Z_teacher
                          ↓
                   MLP Encoder (student) → MLP Decoder → X_corrected

Example
-------
>>> from scdistill import Distiller
>>> from scdistill.teachers import HarmonyTeacher, CombatTeacher
>>>
>>> # Use Harmony teacher
>>> model = Distiller(adata, teacher=HarmonyTeacher(covariate_key='age'))
>>> model.train()
>>>
>>> # Use ComBat teacher
>>> model = Distiller(adata, teacher=CombatTeacher())
>>> model.train()
"""

import torch
import numpy as np
import pandas as pd
from typing import Optional, List, Union, Literal
from anndata import AnnData

from .teachers.base import BaseTeacher
from .teachers.harmony import HarmonyTeacher
from .subsampling import select_representative_cells


class Distiller:
    """Generic distillation model for batch correction.

    Distiller is a flexible framework that can use any batch correction
    method as a "teacher". It learns an MLP to reproduce the teacher's
    corrections, then decodes back to gene expression.

    Parameters
    ----------
    adata : AnnData
        AnnData object with log-normalized expression.
    batch_key : str
        Key in adata.obs for batch labels.
    teacher : BaseTeacher, optional
        Teacher model for batch correction.
        Default: HarmonyTeacher()
    n_hidden : int, default=128
        Hidden layer size in MLP.
    n_layers_encoder : int, default=2
        Number of layers in encoder.
    n_layers_decoder : int, default=2
        Number of layers in decoder.
    dropout_rate : float, default=0.1
        Dropout rate for encoder.
    reconstruction_loss : str, default='mse'
        Type of reconstruction loss:
        - 'mse': Gaussian decoder with MSE loss (for log-normalized input) [DEFAULT]
          Works well for most cases with good variance preservation.
        - 'nb': Negative Binomial decoder with Adapter Layer
          Hybrid architecture: Encoder targets PCA/Harmony space,
          Adapter + NB decoder outputs count distribution.
          Guarantees non-negative output. Recommended for very sparse data.
        - 'zinb': ZINB decoder with NLL loss (for raw count input)
          Requires 2-stage training. Use 'nb' instead for simpler workflow.
    subsample : bool, default=False
        If True, train on representative cells only (faster for large datasets).
    n_subsample : int, optional
        Number of cells to use for training. If None, uses subsample_ratio.
    subsample_ratio : float, default=0.1
        Fraction of cells to use for training if n_subsample is None.
    subsample_method : str, default="geosketch"
        Subsampling method: "geosketch" or "kmeans_medoid".
    celltype_key : str, default="cell_type"
        Key in adata.obs for cell type labels (used for stratified sampling).
    condition_key : str, optional
        Key in adata.obs for continuous covariate (e.g., "age").
    condition_bins : int, default=6
        Number of bins for discretizing continuous condition.

    Attributes
    ----------
    teacher : BaseTeacher
        The teacher model.
    Z_teacher : np.ndarray
        Teacher's corrected embeddings (after train()).
    Z_student : np.ndarray
        Student's embeddings (after train()).

    Examples
    --------
    >>> from scdistill import Distiller
    >>> from scdistill.teachers import HarmonyTeacher, CombatTeacher
    >>>
    >>> # With default Harmony teacher
    >>> model = Distiller(adata, batch_key='batch')
    >>> model.train()
    >>>
    >>> # With ComBat teacher
    >>> model = Distiller(adata, batch_key='batch', teacher=CombatTeacher())
    >>> model.train()
    >>>
    >>> # Get outputs
    >>> Z_teacher = model.get_teacher_representation()
    >>> Z_student = model.get_latent_representation()
    >>> X_corrected = model.get_normalized_expression()
    """

    def __init__(
        self,
        adata: AnnData,
        batch_key: str,
        teacher: Optional[BaseTeacher] = None,
        n_hidden: int = 128,
        n_layers_encoder: int = 2,
        n_layers_decoder: int = 2,
        dropout_rate: float = 0.1,
        reconstruction_loss: str = 'mse',
        # Subsampling parameters
        subsample: bool = False,
        n_subsample: Optional[int] = None,
        subsample_ratio: float = 0.1,
        subsample_method: Literal["geosketch", "kmeans_medoid"] = "geosketch",
        celltype_key: str = "cell_type",
        condition_key: Optional[str] = None,
        condition_bins: int = 6,
        use_layernorm: bool = True,  # LayerNorm at encoder output for batch mixing preservation
    ):
        # Validate
        if batch_key not in adata.obs:
            raise ValueError(f"batch_key '{batch_key}' not in adata.obs")

        self.adata = adata
        self.batch_key = batch_key
        self.teacher = teacher if teacher is not None else HarmonyTeacher()
        self.n_hidden = n_hidden
        self.n_layers_encoder = n_layers_encoder
        self.n_layers_decoder = n_layers_decoder
        self.dropout_rate = dropout_rate
        self.reconstruction_loss = reconstruction_loss
        self.use_layernorm = use_layernorm

        # Subsampling config
        self.subsample = subsample
        self.n_subsample = n_subsample
        self.subsample_ratio = subsample_ratio
        self.subsample_method = subsample_method
        self.celltype_key = celltype_key
        self.condition_key = condition_key
        self.condition_bins = condition_bins

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        # Internal state
        self.module = None
        self._Z_teacher = None      # Full teacher embeddings (N,)
        self._Z_teacher_full = None  # Same as above, kept for clarity
        self._X_input = None        # Full input expression (N, G)
        self._X_corrected = None    # Batch-corrected expression (N, G) - computed lazily
        self._train_indices = None  # Indices used for training (K,) if subsampled
        self._gene_names = None
        self.n_latent = None
        self.history = None
        self.is_trained = False

        # Caching flags for incremental training
        self._teacher_prepared = False
        self._X_train = None
        self._Z_train = None
        self._X_raw_train = None
        self._library_size_train = None
        self._normalize_teacher = False
        self._total_epochs_trained = 0

    def prepare_teacher(self, verbose: bool = True, weighted_pca: bool = False):
        """Prepare data and compute teacher embeddings (Harmony).

        This method is called automatically by train() if not already done.
        Call this explicitly if you want to separate teacher computation from training.

        Parameters
        ----------
        verbose : bool, default=True
            Print progress.
        weighted_pca : bool, default=False
            If True, use covariate-weighted PCA. Genes with larger t-statistics
            between covariate groups get higher weights, preserving covariate-
            associated signals in the PCA space. Requires covariate_key in teacher.
        """
        if self._teacher_prepared:
            if verbose:
                print("Teacher already prepared, skipping...", flush=True)
            return

        from .nn.distillation import DistillationMLP, pretrain_zinb_autoencoder, get_embedding
        import scanpy as sc

        if verbose:
            print("=" * 60, flush=True)
            print(f"Distiller: Preparing teacher ({self.teacher.name})", flush=True)
            print(f"  Reconstruction loss: {self.reconstruction_loss.upper()}", flush=True)
            print("=" * 60, flush=True)

        # === Step 1: Prepare data ===
        if verbose:
            print("\n[1/3] Preparing data...", flush=True)

        # Get expression (HVG if available)
        if 'highly_variable' in self.adata.var:
            adata_hvg = self.adata[:, self.adata.var['highly_variable']]
            self._gene_names = adata_hvg.var_names.values
            X_input = adata_hvg.X
            if verbose:
                print(f"  Using {len(self._gene_names)} highly variable genes", flush=True)
        else:
            self._gene_names = self.adata.var_names.values
            X_input = self.adata.X
            if verbose:
                print(f"  Using all {len(self._gene_names)} genes", flush=True)

        if hasattr(X_input, 'toarray'):
            X_input = X_input.toarray()
        self._X_input = X_input.astype(np.float32)

        # Batch labels
        batch_cat = pd.Categorical(self.adata.obs[self.batch_key])
        batch_labels = batch_cat.codes

        # ============================================================
        # ZINB 2-stage approach: Pre-train → Harmony on Z → Fine-tune
        # ============================================================
        if self.reconstruction_loss == 'zinb':
            # Determine latent dimension (use 50 like PCA)
            self.n_latent = min(50, min(self.adata.n_obs, X_input.shape[1]) - 1)

            if verbose:
                print(f"  Latent dim: {self.n_latent}", flush=True)

            # === Step 2: Create and Pre-train ZINB Autoencoder ===
            if verbose:
                print(f"\n[2/3] Pre-training ZINB Autoencoder (reconstruction only)...", flush=True)

            self.module = DistillationMLP(
                input_dim=self._X_input.shape[1],
                latent_dim=self.n_latent,
                hidden_dim=self.n_hidden,
                n_layers_encoder=self.n_layers_encoder,
                n_layers_decoder=self.n_layers_decoder,
                dropout=self.dropout_rate,
                reconstruction_loss='zinb',
                use_layernorm=self.use_layernorm,
            )

            pretrain_history = pretrain_zinb_autoencoder(
                model=self.module,
                X=self._X_input,
                n_epochs=100,  # Fixed pre-training epochs
                learning_rate=1e-3,
                device=self.device,
                verbose=verbose,
                early_stopping=True,
                patience=10,
            )

            # Get encoder embeddings Z
            if verbose:
                print(f"\n[2.5/3] Computing encoder embeddings Z...", flush=True)

            Z_encoder = get_embedding(self.module, self._X_input, self.device)
            if verbose:
                print(f"  Z shape: {Z_encoder.shape}", flush=True)

            # Apply Harmony to Z
            if verbose:
                print(f"\n[3/3] Applying {self.teacher.name} to encoder embeddings Z...", flush=True)

            self._Z_teacher = self.teacher.fit_transform(
                X_pca=Z_encoder,  # Use encoder output instead of PCA!
                batch_labels=batch_labels,
                obs=self.adata.obs,
                verbose=verbose,
                adata=self.adata,
                batch_key=self.batch_key,
            )
            self._Z_teacher_full = self._Z_teacher

            if verbose:
                print(f"  Z_teacher shape: {self._Z_teacher.shape}", flush=True)

            # Prepare training data
            self._X_train = self._X_input
            self._Z_train = self._Z_teacher
            self._normalize_teacher = False

        # ============================================================
        # MSE/NB approach: PCA → Harmony → Distillation
        # ============================================================
        else:
            # Compute PCA (standard or weighted)
            n_comps = min(50, min(self.adata.n_obs, X_input.shape[1]) - 1)

            if weighted_pca and hasattr(self.teacher, 'covariate_key') and self.teacher.covariate_key is not None:
                # === Weighted PCA: weight genes by covariate association ===
                if verbose:
                    print("  Computing covariate-weighted PCA...", flush=True)

                covariate_key = self.teacher.covariate_key
                covariate_values = self.adata.obs[covariate_key].values

                # Get unique groups (for binary/categorical covariate)
                unique_groups = np.unique(covariate_values)
                if len(unique_groups) != 2:
                    raise ValueError(
                        f"weighted_pca requires binary covariate, got {len(unique_groups)} groups: {unique_groups}"
                    )

                # Compute t-statistics for each gene
                from scipy import stats as sp_stats
                group1_mask = covariate_values == unique_groups[0]
                group2_mask = covariate_values == unique_groups[1]

                X_dense = X_input if not hasattr(X_input, 'toarray') else X_input.toarray()
                t_stats = np.zeros(X_dense.shape[1])
                for g in range(X_dense.shape[1]):
                    t, _ = sp_stats.ttest_ind(X_dense[group1_mask, g], X_dense[group2_mask, g])
                    t_stats[g] = t if not np.isnan(t) else 0

                # Normalize weights to [0, 1]
                weights = np.abs(t_stats) / (np.abs(t_stats).max() + 1e-8)

                if verbose:
                    top_genes = np.argsort(weights)[-5:][::-1]
                    print(f"    Top 5 weighted genes: {self._gene_names[top_genes].tolist()}", flush=True)
                    print(f"    Weight range: [{weights.min():.3f}, {weights.max():.3f}]", flush=True)

                # Apply weights to expression matrix
                X_weighted = X_dense * weights

                # PCA on weighted data
                from sklearn.decomposition import PCA
                pca = PCA(n_components=n_comps)
                X_pca = pca.fit_transform(X_weighted)

                # Store in adata for compatibility
                self.adata.obsm['X_pca'] = X_pca
                self.adata.uns['pca'] = {'variance_ratio': pca.explained_variance_ratio_}
                self.adata.varm['PCs'] = pca.components_.T

                if verbose:
                    print(f"    Variance explained: {pca.explained_variance_ratio_.sum()*100:.1f}%", flush=True)

            elif 'X_pca' not in self.adata.obsm:
                # === Standard PCA ===
                if verbose:
                    print("  Computing PCA...", flush=True)
                sc.pp.pca(self.adata, n_comps=n_comps)
                X_pca = self.adata.obsm['X_pca'].copy()
            else:
                X_pca = self.adata.obsm['X_pca'].copy()

            self.n_latent = X_pca.shape[1]

            if verbose:
                print(f"  PCA dim: {self.n_latent}", flush=True)

            # === Step 2: Teacher correction (on ALL cells) ===
            if verbose:
                print(f"\n[2/3] Computing teacher signal ({self.teacher.name}) on all {len(X_pca)} cells...", flush=True)

            self._Z_teacher = self.teacher.fit_transform(
                X_pca=X_pca,
                batch_labels=batch_labels,
                obs=self.adata.obs,
                verbose=verbose,
                adata=self.adata,
                batch_key=self.batch_key,
            )
            self._Z_teacher_full = self._Z_teacher

            # Handle dimension mismatch
            if self._Z_teacher.shape[1] != self.n_latent:
                if verbose:
                    print(f"  Teacher output dim: {self._Z_teacher.shape[1]} (adjusted from {self.n_latent})", flush=True)
                self.n_latent = self._Z_teacher.shape[1]

            if verbose:
                print(f"  Teacher shape: {self._Z_teacher.shape}", flush=True)

            # === Prepare raw counts and library size for NB mode ===
            if self.reconstruction_loss == 'nb':
                # Get raw counts for NB loss
                if 'counts' in self.adata.layers:
                    if 'highly_variable' in self.adata.var:
                        X_raw_full = self.adata[:, self.adata.var['highly_variable']].layers['counts']
                    else:
                        X_raw_full = self.adata.layers['counts']
                else:
                    # Assume X is already raw counts
                    X_raw_full = self.adata.X if 'highly_variable' not in self.adata.var else \
                                 self.adata[:, self.adata.var['highly_variable']].X

                if hasattr(X_raw_full, 'toarray'):
                    X_raw_full = X_raw_full.toarray()
                self._X_raw = X_raw_full.astype(np.float32)

                # Compute library size (total counts per cell)
                self._library_size = self._X_raw.sum(axis=1).astype(np.float32)

                if verbose:
                    print(f"  NB mode: Raw counts shape {self._X_raw.shape}", flush=True)
                    print(f"  Library size: mean={self._library_size.mean():.1f}, std={self._library_size.std():.1f}", flush=True)

            # === Subsampling (if enabled) ===
            self._X_train = self._X_input
            self._Z_train = self._Z_teacher

            if self.subsample:
                if verbose:
                    print(f"\n[3/3] Selecting representative cells ({self.subsample_method})...", flush=True)

                if self.celltype_key not in self.adata.obs.columns:
                    raise ValueError(
                        f"celltype_key '{self.celltype_key}' not in adata.obs. "
                        f"Available: {list(self.adata.obs.columns)}"
                    )

                self._train_indices = select_representative_cells(
                    Z_harmony=self._Z_teacher,
                    obs=self.adata.obs,
                    n_cells=self.n_subsample,
                    ratio=self.subsample_ratio,
                    batch_key=self.batch_key,
                    celltype_key=self.celltype_key,
                    condition_key=self.condition_key,
                    condition_bins=self.condition_bins,
                    method=self.subsample_method,
                )

                self._X_train = self._X_input[self._train_indices]
                self._Z_train = self._Z_teacher[self._train_indices]

                # Also subsample raw counts and library size for NB mode
                if self.reconstruction_loss == 'nb':
                    self._X_raw_train = self._X_raw[self._train_indices]
                    self._library_size_train = self._library_size[self._train_indices]

                if verbose:
                    print(f"  Selected {len(self._train_indices)} / {len(self._X_input)} cells "
                          f"({100*len(self._train_indices)/len(self._X_input):.1f}%)", flush=True)
            else:
                self._train_indices = None
                # Use full data for NB mode
                if self.reconstruction_loss == 'nb':
                    self._X_raw_train = self._X_raw
                    self._library_size_train = self._library_size

            # === Create MLP model (only if not ZINB which already created it) ===
            if verbose:
                print(f"\n[3/3] Creating MLP encoder-decoder...", flush=True)

            self.module = DistillationMLP(
                input_dim=self._X_input.shape[1],
                latent_dim=self.n_latent,
                hidden_dim=self.n_hidden,
                n_layers_encoder=self.n_layers_encoder,
                n_layers_decoder=self.n_layers_decoder,
                dropout=self.dropout_rate,
                reconstruction_loss=self.reconstruction_loss,  # 'mse' or 'nb'
                use_layernorm=self.use_layernorm,
            )

            # Use teacher's needs_normalization setting
            self._normalize_teacher = getattr(self.teacher, 'needs_normalization', False)
            if verbose and self._normalize_teacher:
                print(f"  Teacher {self.teacher.name} requires normalization", flush=True)

        self._teacher_prepared = True
        if verbose:
            print("\n" + "=" * 60, flush=True)
            print("Teacher preparation complete!", flush=True)
            print("=" * 60, flush=True)

    def train(
        self,
        max_epochs: int = 200,
        lr: float = 1e-3,
        lambda_cosine: float = 2.0,
        lambda_corr: float = 1.0,
        early_stopping: bool = True,
        patience: int = 10,
        verbose: bool = True,
    ):
        """Train the distillation model.

        If teacher has not been prepared, this will call prepare_teacher() first.
        If already trained, this will continue training from the current state.

        Parameters
        ----------
        max_epochs : int, default=200
            Maximum number of training epochs for this call.
        lr : float, default=1e-3
            Learning rate.
        lambda_cosine : float, default=2.0
            Cosine similarity loss weight for pattern matching.
        lambda_corr : float, default=1.0
            Gene-wise correlation loss weight (shift/scale invariant).
        early_stopping : bool, default=True
            Stop training when loss stops improving.
        patience : int, default=10
            Number of epochs to wait for improvement.
        verbose : bool, default=True
            Print progress.
        """
        from .nn.distillation import train_distillation

        # Prepare teacher if not already done
        if not self._teacher_prepared:
            self.prepare_teacher(verbose=verbose)

        # Training epochs info
        start_epoch = self._total_epochs_trained + 1
        end_epoch = self._total_epochs_trained + max_epochs

        if verbose:
            print("=" * 60, flush=True)
            print(f"Training MLP (epochs {start_epoch} to {end_epoch})", flush=True)
            print("=" * 60, flush=True)

        self.history = train_distillation(
            model=self.module,
            X=self._X_train,
            Z_teacher=self._Z_train,
            n_epochs=max_epochs,
            learning_rate=lr,
            lambda_recon=1.0,
            lambda_cosine=lambda_cosine,
            lambda_corr=lambda_corr,
            X_raw=self._X_raw_train if hasattr(self, '_X_raw_train') else None,
            library_size=self._library_size_train if hasattr(self, '_library_size_train') else None,
            normalize_teacher=self._normalize_teacher,
            device=self.device,
            verbose=verbose,
            early_stopping=early_stopping,
            patience=patience,
            epoch_offset=self._total_epochs_trained,  # Pass offset for correct epoch numbering
        )

        self._total_epochs_trained += max_epochs
        self.is_trained = True

        if verbose:
            print("\n" + "=" * 60, flush=True)
            print(f"Training complete! (Total epochs: {self._total_epochs_trained})", flush=True)
            print(f"  Teacher: {self.teacher.name}", flush=True)
            print(f"  Final loss: {self.history['loss_total'][-1]:.4f}", flush=True)
            print(f"  Distillation: {self.history['loss_distillation'][-1]:.4f}", flush=True)
            if lambda_cosine > 0:
                print(f"  Cosine: {self.history['loss_cosine'][-1]:.4f}", flush=True)
            if lambda_corr > 0:
                print(f"  Correlation: {self.history['loss_corr'][-1]:.4f}", flush=True)
            print(f"  Reconstruction: {self.history['loss_reconstruction'][-1]:.4f}", flush=True)
            print("=" * 60, flush=True)

    def get_teacher_representation(
        self,
        indices: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Get teacher's corrected embeddings.

        Returns
        -------
        Z_teacher : np.ndarray
            Teacher's batch-corrected embeddings.
        """
        if self._Z_teacher is None:
            raise ValueError("Model not trained. Run train() first.")

        if indices is not None:
            return self._Z_teacher[indices].copy()
        return self._Z_teacher.copy()

    def get_latent_representation(
        self,
        indices: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Get MLP encoder embeddings (student output).

        Returns
        -------
        Z_student : np.ndarray
            MLP encoder output.
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Run train() first.")

        from .nn.distillation import get_embedding

        X = self._X_input

        if indices is not None:
            X = X[indices]

        return get_embedding(self.module, X, self.device)

    def get_normalized_expression(
        self,
        indices: Optional[np.ndarray] = None,
        gene_list: Optional[List[str]] = None,
    ) -> np.ndarray:
        """Get batch-corrected gene expression (decoder output).

        Parameters
        ----------
        indices : np.ndarray, optional
            Cell indices to return. If None, return all cells.
        gene_list : list of str, optional
            Genes to decode. If specified, only these genes are computed
            (efficient - avoids computing all genes).

        Returns
        -------
        X_corrected : np.ndarray
            Batch-corrected expression. Shape: (n_cells, n_genes) or
            (n_cells, len(gene_list)) if gene_list is specified.
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Run train() first.")

        from .nn.distillation import get_reconstructed_expression

        X = self._X_input

        if indices is not None:
            X = X[indices]

        # Efficient gene-specific decoding
        gene_indices = None
        if gene_list is not None:
            gene_indices = np.array([
                np.where(self._gene_names == g)[0][0]
                for g in gene_list if g in self._gene_names
            ])
            if len(gene_indices) == 0:
                raise ValueError(f"No genes found. Available: {self._gene_names[:5].tolist()}...")

        X_recon = get_reconstructed_expression(
            self.module, X, self.device,
            gene_indices=gene_indices,
        )

        return X_recon

    def get_gene_names(self, gene_list: Optional[List[str]] = None) -> np.ndarray:
        """Get gene names used in the model.

        Parameters
        ----------
        gene_list : list of str, optional
            If specified, return only these genes (in order).

        Returns
        -------
        gene_names : np.ndarray
            Gene names.
        """
        if gene_list is None:
            return self._gene_names.copy()
        return np.array([g for g in gene_list if g in self._gene_names])

    def differential_expression(
        self,
        adata: Optional['AnnData'] = None,
        groupby: Optional[str] = None,
        group1: Optional[str] = None,
        group2: Optional[str] = None,
        idx1: Optional[np.ndarray] = None,
        idx2: Optional[np.ndarray] = None,
        sample_key: Optional[str] = None,
        how: str = 'pseudobulk',
        # Pseudobulk-specific params
        min_cells_per_sample: int = 5,
        lfc_threshold: float = 0.1,
        fdr_threshold: float = 0.05,
        method: str = 'wilcox',
        # Bayesian-specific params (legacy, not recommended)
        mode: str = 'change',
        delta: Optional[float] = None,
        n_samples: int = 100,
    ) -> pd.DataFrame:
        """Perform differential expression analysis.

        Uses sample-level pseudobulk approach for proper statistical testing.
        Groups cells by sample (biological replicate) and performs t-test
        at sample level.

        Parameters
        ----------
        adata : AnnData, optional
            Subset of cells to use for DE analysis. If provided, only cells
            present in this adata will be used. Cell names must match
            the original training data.
        groupby : str, optional
            Column in adata.obs to group by (e.g., 'condition').
        group1 : str, optional
            Name of reference group (e.g., 'Healthy').
        group2 : str, optional
            Name of comparison group (e.g., 'COVID').
        idx1 : np.ndarray, optional
            Boolean mask for group 1 cells.
        idx2 : np.ndarray, optional
            Boolean mask for group 2 cells.
        sample_key : str, optional
            Column in adata.obs containing sample/donor IDs for pseudobulk.
            Required for pseudobulk method. If None, looks for 'sample' column.
        how : str
            DE method: 'pseudobulk' (default, recommended) or 'bayesian' (legacy).

        Pseudobulk-specific parameters:
        min_cells_per_sample : int
            Minimum cells per sample to include (default: 5).
        lfc_threshold : float
            Minimum |LFC| to consider as DE (default: 0.1).
        fdr_threshold : float
            FDR threshold for significance (default: 0.05).
        method : str
            Statistical test: 'wilcox' (default, robust), 'ttest', or 'deseq2'.

        Bayesian-specific parameters (legacy, not recommended):
        mode : str
            DE mode ('change' or 'vanilla').
        delta : float, optional
            Threshold for DE.
        n_samples : int
            Number of MC Dropout samples.

        Returns
        -------
        results : pd.DataFrame
            DE results with columns: gene, lfc, pval, fdr, is_de, direction.
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Run train() first.")

        from .de import differential_expression

        # Determine which adata to use for groupby lookup
        obs_to_use = adata.obs if adata is not None else self.adata.obs

        if groupby is not None:
            if group1 is None or group2 is None:
                raise ValueError("Specify group1 and group2 with groupby")
            idx1 = (obs_to_use[groupby] == group1).values
            idx2 = (obs_to_use[groupby] == group2).values

        if idx1 is None or idx2 is None:
            raise ValueError("Specify (groupby, group1, group2) or (idx1, idx2)")

        # Get sample labels for pseudobulk
        if how == 'pseudobulk':
            # Determine sample key
            if sample_key is None:
                # Try common column names
                for key in ['sample', 'donor', 'patient', 'Sample', 'Donor']:
                    if key in obs_to_use.columns:
                        sample_key = key
                        break
                if sample_key is None:
                    raise ValueError(
                        "sample_key not specified and no 'sample' column found. "
                        "Provide sample_key to specify which column contains sample IDs."
                    )

            sample_labels = obs_to_use[sample_key].values

            # Get X_corrected
            if self._X_corrected is None:
                # Compute X_corrected on-the-fly
                self.module.eval()
                with torch.no_grad():
                    X_tensor = torch.from_numpy(self._X_input).float().to(self.device)
                    Z = self.module(X_tensor)
                    X_corrected = self.module.decode(Z).cpu().numpy()
            else:
                X_corrected = self._X_corrected

            return differential_expression(
                X_corrected=X_corrected,
                idx1=idx1,
                idx2=idx2,
                sample_labels=sample_labels,
                gene_names=self._gene_names,
                how='pseudobulk',
                min_cells_per_sample=min_cells_per_sample,
                lfc_threshold=lfc_threshold,
                fdr_threshold=fdr_threshold,
                method=method,
            )
        else:
            # Bayesian method (legacy, not recommended)
            return differential_expression(
                model=self.module,
                X=self._X_input,
                idx1=idx1,
                idx2=idx2,
                how='bayesian',
                gene_names=self._gene_names,
                mode=mode,
                delta=delta,
                fdr_target=fdr_threshold,
                n_samples=n_samples,
                device=self.device,
            )

    def save(self, dir_path: str, overwrite: bool = False):
        """Save the model."""
        import os
        import pickle

        if os.path.exists(dir_path) and not overwrite:
            raise FileExistsError(f"{dir_path} exists. Use overwrite=True.")

        os.makedirs(dir_path, exist_ok=True)

        torch.save(self.module.state_dict(), os.path.join(dir_path, 'model.pt'))

        config = {
            'n_latent': self.n_latent,
            'n_hidden': self.n_hidden,
            'n_layers_encoder': self.n_layers_encoder,
            'n_layers_decoder': self.n_layers_decoder,
            'dropout_rate': self.dropout_rate,
            'reconstruction_loss': self.reconstruction_loss,
            'batch_key': self.batch_key,
            'teacher_name': self.teacher.name,
            'gene_names': self._gene_names.tolist(),
            # Subsampling config
            'subsample': self.subsample,
            'n_subsample': self.n_subsample,
            'subsample_ratio': self.subsample_ratio,
            'subsample_method': self.subsample_method,
            'celltype_key': self.celltype_key,
            'condition_key': self.condition_key,
            'condition_bins': self.condition_bins,
            # Training state
            'total_epochs_trained': self._total_epochs_trained,
        }
        with open(os.path.join(dir_path, 'config.pkl'), 'wb') as f:
            pickle.dump(config, f)

        # Save full teacher embeddings (for all cells)
        np.save(os.path.join(dir_path, 'Z_teacher.npy'), self._Z_teacher)

        # Save training indices if subsampled
        if self._train_indices is not None:
            np.save(os.path.join(dir_path, 'train_indices.npy'), self._train_indices)

        print(f"Model saved to {dir_path}", flush=True)

    @classmethod
    def load(cls, dir_path: str, adata: Optional[AnnData] = None) -> "Distiller":
        """Load a saved model.

        Parameters
        ----------
        dir_path : str
            Directory containing saved model files.
        adata : AnnData, optional
            AnnData object to associate with the loaded model.
            If None, a minimal AnnData will be created from saved gene names.

        Returns
        -------
        Distiller
            Loaded model instance.
        """
        import os
        import pickle

        # Load config
        with open(os.path.join(dir_path, 'config.pkl'), 'rb') as f:
            config = pickle.load(f)

        gene_names = np.array(config['gene_names'])
        n_genes = len(gene_names)

        # Create minimal AnnData if not provided
        if adata is None:
            adata = AnnData(np.zeros((1, n_genes)))
            adata.var_names = gene_names

        # Create teacher instance
        from .teachers.harmony import HarmonyTeacher
        from .teachers.combat import CombatTeacher

        teacher_name = config.get('teacher_name', 'HarmonyTeacher')
        if 'Harmony' in teacher_name:
            teacher = HarmonyTeacher()
        elif 'Combat' in teacher_name:
            teacher = CombatTeacher()
        else:
            teacher = HarmonyTeacher()  # Default fallback

        # Create instance
        instance = cls(
            adata=adata,
            batch_key=config.get('batch_key', 'batch'),
            teacher=teacher,
            n_hidden=config.get('n_hidden', 128),
            n_layers_encoder=config.get('n_layers_encoder', 2),
            n_layers_decoder=config.get('n_layers_decoder', 2),
            dropout_rate=config.get('dropout_rate', 0.1),
            reconstruction_loss=config.get('reconstruction_loss', 'mse'),
            subsample=config.get('subsample', False),
            n_subsample=config.get('n_subsample'),
            subsample_ratio=config.get('subsample_ratio'),
            subsample_method=config.get('subsample_method', 'geosketch'),
            celltype_key=config.get('celltype_key'),
            condition_key=config.get('condition_key'),
            condition_bins=config.get('condition_bins', 10),
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

        # Load training indices if available
        train_indices_path = os.path.join(dir_path, 'train_indices.npy')
        if os.path.exists(train_indices_path):
            instance._train_indices = np.load(train_indices_path)

        # Restore _X_input from adata if provided
        if adata is not None and adata.n_obs > 1:
            # Filter adata to genes used during training
            gene_mask = [g in gene_names for g in adata.var_names]
            if sum(gene_mask) == len(gene_names):
                # All genes present - use them
                X_input = adata[:, gene_names].X
            else:
                # Use whatever genes match
                common_genes = [g for g in gene_names if g in adata.var_names]
                if common_genes:
                    X_input = adata[:, common_genes].X
                else:
                    X_input = None

            if X_input is not None:
                if hasattr(X_input, 'toarray'):
                    X_input = X_input.toarray()
                instance._X_input = X_input.astype(np.float32)
                instance._X_train = instance._X_input
                instance._Z_train = instance._Z_teacher

        print(f"Model loaded from {dir_path}", flush=True)
        return instance

    def __repr__(self) -> str:
        status = "trained" if self.is_trained else "not trained"
        return f"Distiller(teacher={self.teacher.name}, {status})"

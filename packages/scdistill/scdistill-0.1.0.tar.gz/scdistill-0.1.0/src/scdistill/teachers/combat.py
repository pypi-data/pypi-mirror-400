"""ComBat teacher for batch correction."""

import numpy as np
import pandas as pd
from typing import Optional
from .base import BaseTeacher


class CombatTeacher(BaseTeacher):
    """ComBat batch correction in PCA space.

    ComBat uses empirical Bayes to estimate and remove batch effects.
    This teacher applies ComBat to PCA embeddings.

    Note: Requires the 'combat' package (pycombat) to be installed.
    Install with: pip install combat

    Parameters
    ----------
    parametric : bool, default=True
        Use parametric empirical Bayes.
    covariate_cols : list of str, optional
        Column names in obs to protect as covariates (e.g., ['condition']).
        These biological variables will be preserved during batch correction.

    Examples
    --------
    >>> teacher = CombatTeacher()
    >>> Z_corrected = teacher.fit_transform(X_pca, batch_labels)

    >>> # Protect condition as covariate
    >>> teacher = CombatTeacher(covariate_cols=['condition'])
    >>> Z_corrected = teacher.fit_transform(X_pca, batch_labels, obs=adata.obs)
    """

    name = "CombatTeacher"

    def __init__(self, parametric: bool = True, covariate_cols: Optional[list] = None):
        super().__init__()
        self.parametric = parametric
        self.covariate_cols = covariate_cols

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
        """Apply ComBat batch correction.

        Parameters
        ----------
        X_pca : np.ndarray
            PCA embeddings (n_cells, n_pcs).
        batch_labels : np.ndarray
            Batch labels (n_cells,).
        obs : pd.DataFrame, optional
            Observation metadata. Required if covariate_cols is specified.
        verbose : bool
            Print progress.

        Returns
        -------
        Z_corrected : np.ndarray
            ComBat-corrected embeddings.
        """
        try:
            from pycombat.pycombat import Combat
        except ImportError:
            try:
                from combat.pycombat import pycombat as combat_func
                Combat = None
            except ImportError:
                raise ImportError(
                    "CombatTeacher requires the 'pycombat' package. "
                    "Install with: pip install pycombat"
                )

        if verbose:
            print(f"{self.name}: parametric={self.parametric}")

        # Prepare covariate matrix if specified
        X_cov = None
        if self.covariate_cols is not None:
            if obs is None:
                raise ValueError(
                    f"obs must be provided when covariate_cols={self.covariate_cols} is specified"
                )

            from sklearn.preprocessing import LabelEncoder

            cov_arrays = []
            for col in self.covariate_cols:
                covariate_values = obs[col].values
                if covariate_values.dtype == object or isinstance(covariate_values[0], str):
                    le = LabelEncoder()
                    encoded = le.fit_transform(covariate_values)
                    cov_arrays.append(encoded)
                else:
                    cov_arrays.append(covariate_values)
            X_cov = np.column_stack(cov_arrays)

            if verbose:
                print(f"  Protecting covariates: {self.covariate_cols}")

        # Apply ComBat
        if Combat is not None:
            # New pycombat API (>= 0.20)
            mode = 'p' if self.parametric else 'np'
            combat = Combat(mode=mode)
            # X_pca is (n_cells, n_pcs), pycombat expects (n_samples, n_features)
            corrected = combat.fit_transform(X_pca, batch_labels, X=X_cov)
            self.Z_corrected = np.array(corrected)
        else:
            # Old pycombat API
            data = pd.DataFrame(X_pca.T)
            batch = pd.Series(batch_labels)
            mod = [X_cov[:, i].tolist() for i in range(X_cov.shape[1])] if X_cov is not None else []
            corrected = combat_func(data, batch, mod=mod)
            self.Z_corrected = corrected.T.values
        self._is_fitted = True

        if verbose:
            print(f"  Corrected shape: {self.Z_corrected.shape}")

        return self.Z_corrected

    def __repr__(self) -> str:
        return f"CombatTeacher(parametric={self.parametric}, covariate_cols={self.covariate_cols})"

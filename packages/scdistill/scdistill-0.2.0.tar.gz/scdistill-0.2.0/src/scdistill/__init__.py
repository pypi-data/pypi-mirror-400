"""scDistill: Batch correction with covariate protection.

scDistill corrects batch effects in scRNA-seq data while preserving
biological variation (e.g., age effects, treatment effects).

Architecture:
    X (genes) → PCA → Teacher (Harmony/ComBat/etc.)
                          ↓
                   MLP Encoder (student) → MLP Decoder → X_corrected

Models
------
- scDistill: Harmony distillation with covariate protection (recommended)
- Distiller: Generic distillation with any teacher

Teachers
--------
- HarmonyTeacher: Harmony with covariate protection (default)
- CombatTeacher: ComBat batch correction
- ScanoramaTeacher: Scanorama integration

Quick Start (scDistill - Harmony with covariate protection)
-----------------------------------------------------------
>>> from scdistill import scDistill
>>>
>>> scDistill.setup_anndata(adata, batch_key='batch', covariate_key='age')
>>> model = scDistill(adata)
>>> model.train(max_epochs=200)
>>> X_corrected = model.get_normalized_expression()

Using Different Teachers (Distiller)
------------------------------------
>>> from scdistill import Distiller
>>> from scdistill.teachers import CombatTeacher
>>>
>>> model = Distiller(adata, batch_key='batch', teacher=CombatTeacher())
>>> model.train()
>>> X_corrected = model.get_normalized_expression()
"""

from .model import scDistill
from .distiller import Distiller
from .nn import ZINB, zinb_nll
from . import teachers
from .subsampling import select_representative_cells

__version__ = "0.7.0"
__all__ = [
    "scDistill",
    "Distiller",
    "teachers",
    "ZINB",
    "zinb_nll",
    "select_representative_cells",
]

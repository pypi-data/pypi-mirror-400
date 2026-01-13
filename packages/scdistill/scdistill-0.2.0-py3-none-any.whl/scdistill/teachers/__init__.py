"""Teacher models for batch correction distillation.

Teachers are batch correction methods that operate in PCA/latent space.
Their corrected embeddings serve as teaching signals for the MLP student.

Available Teachers:
- HarmonyTeacher: Harmony with covariate protection (default, needs_normalization=False)
- CombatTeacher: ComBat batch correction (needs_normalization=False)
- ScanoramaTeacher: Scanorama integration (needs_normalization=False)
- FastMNNTeacher: fastMNN batch correction (requires: R, batchelor, needs_normalization=True)
- LIGERTeacher: LIGER integration (requires: R, rliger, needs_normalization=True)
- SymphonyTeacher: Symphony reference-based (requires: R, symphony, needs_normalization=False)

Each teacher has a `needs_normalization` property indicating whether its embeddings
need to be normalized before distillation (due to small-scale output).

Example
-------
>>> from scdistill.teachers import HarmonyTeacher, FastMNNTeacher, LIGERTeacher
>>>
>>> # Harmony (normal scale, no normalization needed)
>>> teacher = HarmonyTeacher(theta=2.0)
>>> print(teacher.needs_normalization)  # False
>>>
>>> # fastMNN (small scale, normalization needed)
>>> teacher = FastMNNTeacher()
>>> print(teacher.needs_normalization)  # True
"""

from .base import (
    BaseTeacher,
    RScriptRunner,
    generate_r_header,
    generate_data_loading_code,
    generate_data_saving_code,
)
from .harmony import HarmonyTeacher
from .fastmnn import FastMNNTeacher
from .liger import LIGERTeacher
from .symphony import SymphonyTeacher
from .combat import CombatTeacher
from .scanorama import ScanoramaTeacher

__all__ = [
    # Base classes and utilities
    'BaseTeacher',
    'RScriptRunner',
    'generate_r_header',
    'generate_data_loading_code',
    'generate_data_saving_code',
    # Python-based teachers
    'HarmonyTeacher',
    'CombatTeacher',
    'ScanoramaTeacher',
    # R-based teachers
    'FastMNNTeacher',
    'LIGERTeacher',
    'SymphonyTeacher',
    # Registry
    'TEACHER_REGISTRY',
    'get_available_teachers',
    'get_teacher_config',
]

# Single source of truth for teacher configurations
TEACHER_REGISTRY = {
    "Harmony": {
        "class": HarmonyTeacher,
        "kwargs": {"theta": 2.0, "covariate_key": "condition"},
        "requires_r": False,
        "description": "Harmony with covariate protection",
    },
    "ComBat": {
        "class": CombatTeacher,
        "kwargs": {},
        "requires_r": False,
        "description": "ComBat batch correction",
    },
    "Scanorama": {
        "class": ScanoramaTeacher,
        "kwargs": {},
        "requires_r": False,
        "description": "Scanorama integration",
    },
    "fastMNN": {
        "class": FastMNNTeacher,
        "kwargs": {},
        "requires_r": True,
        "description": "Fast MNN (R batchelor)",
    },
    "Symphony": {
        "class": SymphonyTeacher,
        "kwargs": {},
        "requires_r": True,
        "description": "Symphony reference-based",
    },
    "LIGER": {
        "class": LIGERTeacher,
        "kwargs": {},
        "requires_r": True,
        "description": "LIGER integration",
    },
}


def get_available_teachers(include_r: bool = True) -> list[str]:
    """Get list of available teacher names.

    Parameters
    ----------
    include_r : bool
        If True, include teachers that require R. Default True.

    Returns
    -------
    list[str]
        List of teacher names.
    """
    if include_r:
        return list(TEACHER_REGISTRY.keys())
    return [k for k, v in TEACHER_REGISTRY.items() if not v["requires_r"]]


def get_teacher_config(name: str) -> dict | None:
    """Get configuration for a specific teacher.

    Parameters
    ----------
    name : str
        Teacher name (case-sensitive).

    Returns
    -------
    dict or None
        Teacher configuration dict with 'class', 'kwargs', 'requires_r', 'description'.
        Returns None if teacher not found.
    """
    return TEACHER_REGISTRY.get(name)

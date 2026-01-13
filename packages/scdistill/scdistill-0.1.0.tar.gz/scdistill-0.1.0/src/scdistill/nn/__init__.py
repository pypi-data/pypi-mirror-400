"""Neural network modules for scDistill."""

from .zinb import ZINB, zinb_nll, ZINBDecoder, nb_nll, NBDecoder
from .distillation import (
    DistillationMLP,
    train_distillation,
    pretrain_zinb_autoencoder,
    get_embedding,
    get_reconstructed_expression,
    # Backward compatibility
    HarmonyMLP,
    train_harmony_distillation,
)

__all__ = [
    # Distillation MLP
    "DistillationMLP",
    "train_distillation",
    "pretrain_zinb_autoencoder",
    "get_embedding",
    "get_reconstructed_expression",
    # ZINB / NB
    "ZINB",
    "zinb_nll",
    "ZINBDecoder",
    "nb_nll",
    "NBDecoder",
    # Backward compatibility
    "HarmonyMLP",
    "train_harmony_distillation",
]

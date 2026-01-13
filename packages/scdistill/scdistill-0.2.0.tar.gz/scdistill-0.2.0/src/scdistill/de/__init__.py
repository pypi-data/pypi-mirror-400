"""Differential Expression module for scDistill.

Sample-level pseudobulk differential expression analysis with proper
statistical testing. Groups cells by sample (biological replicate) and
performs t-test at sample level.

Main function:
- differential_expression: Perform DE analysis between two conditions
"""

from .differential_expression import (
    differential_expression,
    differential_expression_pseudobulk,
    differential_expression_bayesian,
)

__all__ = [
    'differential_expression',
    'differential_expression_pseudobulk',
    'differential_expression_bayesian',
]

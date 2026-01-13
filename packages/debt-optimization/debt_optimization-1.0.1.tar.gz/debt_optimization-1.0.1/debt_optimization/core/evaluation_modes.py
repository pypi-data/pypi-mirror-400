"""
Evaluation mode definitions for debt optimization framework.
"""

from enum import Enum


class EvaluationMode(Enum):
    """Evaluation fidelity modes"""
    FAST = "fast"           # Surrogate-based (learned)
    ACCURATE = "accurate"   # Real training
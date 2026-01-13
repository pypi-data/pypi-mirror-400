"""
Debt-Based Optimization Framework

A novel optimization approach based on debt-paying mechanics,
combining conditional debt, severity scaling, and directional intelligence.
"""

from .optimizer.optimizer import DebtOptimizer
from .core.evaluation_modes import EvaluationMode
from .architecture.neural_architecture import DynamicNeuralArchitecture
from .utils.visualization import plot_convergence

__version__ = "1.0.1"

__all__ = [
    'DebtOptimizer',
    'EvaluationMode',
    'DynamicNeuralArchitecture',
    'plot_convergence'
]
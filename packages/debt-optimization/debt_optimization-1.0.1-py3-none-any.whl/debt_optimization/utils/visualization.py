"""
Visualization utilities for optimization progress.
"""

from typing import List
from ..core.evaluation_modes import EvaluationMode


def plot_convergence(fitness_history: List[float], eval_history: List[int],
                    mode: EvaluationMode, title_suffix: str = ""):
    """Plot search convergence"""
    try:
        import matplotlib.pyplot as plt
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Fitness convergence
        ax1.plot(fitness_history, linewidth=2.5, color='darkred', label='Best Fitness')
        ax1.fill_between(range(len(fitness_history)), fitness_history, alpha=0.3, color='red')
        ax1.axhline(y=min(fitness_history), color='green', linestyle='--', alpha=0.5, label='Best Found')
        ax1.set_title(f'Debt Optimization: Fitness Convergence ({mode.value}) {title_suffix}', 
                     fontsize=14, fontweight='bold')
        ax1.set_xlabel('Iteration', fontsize=12)
        ax1.set_ylabel('Fitness (Lower = Better)', fontsize=12)
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.legend()
        
        # Anytime performance
        ax2.plot(eval_history, fitness_history, linewidth=2.5, color='darkblue', 
                label='Anytime Performance')
        ax2.fill_between(eval_history, fitness_history, alpha=0.3, color='blue')
        ax2.set_title(f'Debt Optimization: Anytime Performance ({mode.value}) {title_suffix}', 
                     fontsize=14, fontweight='bold')
        ax2.set_xlabel('Total Evaluations', fontsize=12)
        ax2.set_ylabel('Best Fitness', fontsize=12)
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.legend()
        
        plt.tight_layout()
        plt.show()
    except ImportError:
        print("⚠️  Matplotlib not available - skipping plots")
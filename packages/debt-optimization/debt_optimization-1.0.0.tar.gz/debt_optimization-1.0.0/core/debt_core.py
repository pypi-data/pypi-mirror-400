"""
Pure debt-paying optimization core logic.
Domain-agnostic debt mechanics based on conditional debt, 
severity scaling, and directional intelligence.
"""

import numpy as np
from typing import List, Callable
from collections import deque
from dataclasses import dataclass


@dataclass
class DebtRecord:
    """Records a debt transaction"""
    vector: np.ndarray
    severity: float
    exists: bool
    fitness_before: float
    fitness_after: float


class PureDebtCore:
    """
    Pure Debt-Paying Optimization Core
    
    Domain-agnostic optimization based on debt mechanics.
    """
    
    def __init__(self,
                 alpha_init: float = 0.3,
                 beta: float = 1.2,
                 gamma: float = 0.8,
                 delta: float = 0.5,
                 n_agents: int = 3,
                 council_weight: float = 0.15,
                 enable_council: bool = True,
                 enable_directional: bool = True,
                 enable_severity_scaling: bool = True):
        
        self.alpha_init = alpha_init
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.n_agents = n_agents
        self.council_weight = council_weight
        
        # Ablation flags
        self.enable_council = enable_council
        self.enable_directional = enable_directional
        self.enable_severity_scaling = enable_severity_scaling
        
        self.improvement_history = deque(maxlen=10)
    
    def natural_risk_decay(self, iteration: int, max_iterations: int) -> float:
        """Calculate exploration risk with natural decay"""
        progress = iteration / max_iterations
        base_decay = self.alpha_init * np.exp(-2.0 * progress)
        
        if len(self.improvement_history) > 5:
            recent_improvement = np.mean(list(self.improvement_history))
            improvement_factor = 1.0 + (1.0 - min(recent_improvement, 1.0)) * 0.5
        else:
            improvement_factor = 1.0
        
        return base_decay * improvement_factor
    
    def conditional_debt_move(self,
                            X_current: np.ndarray,
                            fitness_current: float,
                            alpha: float,
                            evaluate_fn: Callable) -> DebtRecord:
        """Step 1: Conditional debt (debt exists only if exploration worsens)"""
        perturbation = alpha * np.random.randn(len(X_current))
        X_debt = np.clip(X_current + perturbation, 0, 1)
        
        fitness_debt = evaluate_fn(X_debt)
        
        if fitness_debt > fitness_current:
            debt_vector = X_debt - X_current
            severity = fitness_debt - fitness_current
            has_debt = True
        else:
            debt_vector = np.zeros_like(X_current)
            severity = 0.0
            has_debt = False
        
        return DebtRecord(
            vector=debt_vector,
            severity=severity,
            exists=has_debt,
            fitness_before=fitness_current,
            fitness_after=fitness_debt
        )
    
    def severity_scaled_repayment(self,
                                  X_current: np.ndarray,
                                  debt: DebtRecord) -> np.ndarray:
        """Step 2: Severity-scaled repayment"""
        if not debt.exists:
            return X_current
        
        if self.enable_severity_scaling:
            severity_scale = np.tanh(debt.severity / 10.0)
            D_scaled = severity_scale * debt.vector
        else:
            D_scaled = debt.vector
        
        X_repay = X_current - self.beta * D_scaled
        return np.clip(X_repay, 0, 1)
    
    def severity_scaled_double_pay(self,
                                  X_repay: np.ndarray,
                                  debt: DebtRecord) -> np.ndarray:
        """Step 3: Double payment (overshoot beyond repayment)"""
        if not debt.exists:
            return X_repay
        
        if self.enable_severity_scaling:
            severity_scale = np.tanh(debt.severity / 10.0)
            D_scaled = severity_scale * debt.vector
        else:
            D_scaled = debt.vector
        
        X_double = X_repay - self.gamma * D_scaled
        return np.clip(X_double, 0, 1)
    
    def directional_intelligence(self,
                                X_double: np.ndarray,
                                X_best: np.ndarray,
                                debt: DebtRecord) -> np.ndarray:
        """Step 4: Directional intelligence (learn from best when aligned)"""
        if not self.enable_directional:
            return X_double
        
        direction_to_best = X_best - X_double
        
        if debt.exists:
            alignment = np.dot(direction_to_best, -debt.vector)
            if alignment > 0:
                X_smart = X_double + self.delta * direction_to_best
            else:
                X_smart = X_double
        else:
            X_smart = X_double + self.delta * direction_to_best
        
        return np.clip(X_smart, 0, 1)
    
    def council_consensus(self,
                         X_agents: List[np.ndarray],
                         debt_records: List[DebtRecord]) -> List[np.ndarray]:
        """Step 5: Council consensus (multi-agent wisdom)"""
        if not self.enable_council:
            return X_agents
        
        valid_debts = [d.vector for d in debt_records if d.exists]
        
        if len(valid_debts) > 0:
            avg_debt_direction = np.mean(valid_debts, axis=0)
            norm = np.linalg.norm(avg_debt_direction)
            if norm > 1e-10:
                avg_debt_direction = avg_debt_direction / norm
            else:
                avg_debt_direction = np.zeros_like(X_agents[0])
        else:
            avg_debt_direction = np.zeros_like(X_agents[0])
        
        adjusted_agents = []
        for X in X_agents:
            X_adjusted = X - self.council_weight * avg_debt_direction
            adjusted_agents.append(np.clip(X_adjusted, 0, 1))
        
        return adjusted_agents
    
    def record_improvement(self, fitness_before: float, fitness_after: float):
        """Record improvement for natural decay"""
        if fitness_after < fitness_before:
            improvement_rate = (fitness_before - fitness_after) / (abs(fitness_before) + 1e-10)
            self.improvement_history.append(improvement_rate)
"""
Unified NAS adapter combining surrogate and real training evaluation.
"""

import numpy as np
import random
from typing import Optional

try:
    import torch
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

from ..core.evaluation_modes import EvaluationMode
from .surrogate import LearnedSurrogate
from .real_training import RealTrainingEvaluator


class UnifiedNASAdapter:
    """
    Enhanced NAS Adapter with:
    - Global memory buffer for surrogate training
    - Learned surrogate in FAST mode
    - Successive Halving in ACCURATE mode
    """
    
    def __init__(self,
                 mode: EvaluationMode = EvaluationMode.FAST,
                 eval_budget: int = 200,
                 enable_early_reject: bool = True,
                 enable_complexity_penalty: bool = True,
                 enable_successive_halving: bool = True,
                 min_layers: int = 2,
                 max_layers: int = 6,
                 device: str = 'cpu'):
        
        self.mode = mode
        self.eval_budget = eval_budget
        self.enable_early_reject = enable_early_reject
        self.enable_complexity_penalty = enable_complexity_penalty
        self.enable_successive_halving = enable_successive_halving
        
        self.evaluation_count = 0
        self.fidelity_counts = {'low': 0, 'medium': 0, 'high': 0}
        
        # Global memory buffer (Bayesian-lite)
        self.memory_vectors = []
        self.memory_fitness = []
        self.max_memory_size = 500
        
        # Initialize evaluators
        if mode == EvaluationMode.FAST:
            if PYTORCH_AVAILABLE:
                # Learned surrogate - calculate correct vector dimension
                n_activation_options = 4  # relu, tanh, elu, gelu
                values_per_layer = 1 + n_activation_options + 1 + 1  # units + act_probs + dropout + skip
                vector_dim = 1 + (max_layers * values_per_layer)  # depth + (layers × values)
                self.surrogate = LearnedSurrogate(vector_dim)
                print("📊 Mode: FAST (learned surrogate)")
            else:
                self.surrogate = None
                print("📊 Mode: FAST (fallback heuristic - PyTorch unavailable)")
        else:
            if not PYTORCH_AVAILABLE:
                raise RuntimeError("ACCURATE mode requires PyTorch")
            self.evaluator = RealTrainingEvaluator(device=device, 
                                                  enable_successive_halving=enable_successive_halving)
            print(f"📊 Mode: ACCURATE (real training, successive_halving={enable_successive_halving})")
    
    def add_to_memory(self, vector: np.ndarray, fitness: float):
        """Add evaluation to global memory"""
        self.memory_vectors.append(vector.copy())
        self.memory_fitness.append(fitness)
        
        # Limit memory size
        if len(self.memory_vectors) > self.max_memory_size:
            self.memory_vectors.pop(0)
            self.memory_fitness.pop(0)
    
    def update_surrogate(self):
        """Train surrogate on accumulated memory"""
        if self.mode != EvaluationMode.FAST or self.surrogate is None:
            return
        
        if len(self.memory_vectors) >= 10:
            X_batch = np.array(self.memory_vectors)
            y_batch = np.array(self.memory_fitness)
            self.surrogate.update(X_batch, y_batch, epochs=10)
    
    def heuristic_score(self, arch) -> float:
        """Fallback heuristic (if PyTorch unavailable)"""
        score = 100.0
        score -= abs(arch.n_layers - 3) * 10
        for units in arch.layer_units:
            if 64 <= units <= 256:
                score -= 15
            else:
                score += abs(128 - units) / 128 * 5
        score -= sum(arch.use_skip) * 5
        score -= len(set(arch.activations)) / len(arch.activations) * 20
        score += sum([abs(d - 0.2) * 10 for d in arch.dropouts])
        score += random.gauss(0, 2)
        return max(0, score)
    
    def should_reject_early(self, arch) -> bool:
        """Early rejection filter"""
        if not self.enable_early_reject or self.evaluation_count < 10:
            return False
        
        # Simple heuristic check
        if arch.n_layers < 2 or arch.n_layers > 6:
            return True
        if any(u < 32 or u > 512 for u in arch.layer_units):
            return True
        
        return False
    
    def select_fidelity(self, iteration: int, max_iterations: int, 
                       is_best: bool = False) -> str:
        """Multi-fidelity strategy"""
        if self.mode == EvaluationMode.FAST:
            return 'fast'
        
        progress = iteration / max_iterations
        
        if is_best and progress > 0.7:
            return 'high'
        elif progress < 0.33:
            return 'low'
        elif progress < 0.67:
            return 'medium'
        else:
            return 'high'
    
    def evaluate(self, arch,
                iteration: int = 0, max_iterations: int = 100,
                is_best: bool = False) -> float:
        """Unified evaluation with memory tracking"""
        
        # Budget check
        if self.evaluation_count >= self.eval_budget:
            return 999.0
        
        # Early rejection
        if self.should_reject_early(arch):
            return 999.0
        
        # Get vector for memory
        vector = arch.to_vector()
        
        # Evaluate
        if self.mode == EvaluationMode.FAST:
            if self.surrogate is not None and self.surrogate.trained:
                fitness = self.surrogate.predict(vector)
            else:
                fitness = self.heuristic_score(arch)
        else:
            fidelity = self.select_fidelity(iteration, max_iterations, is_best)
            fitness = self.evaluator.evaluate(arch, fidelity)
            self.fidelity_counts[fidelity] += 1
        
        self.evaluation_count += 1
        
        # Add to memory for surrogate learning
        self.add_to_memory(vector, fitness)
        
        # Complexity penalty
        if self.enable_complexity_penalty:
            complexity_penalty = (sum(arch.layer_units) / 1000.0) * 0.01
            fitness += complexity_penalty
        
        return fitness
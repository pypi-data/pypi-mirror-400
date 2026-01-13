"""
Main debt-based optimization system.
"""

import numpy as np
from typing import List, Tuple

from ..core.debt_core import PureDebtCore
from ..core.evaluation_modes import EvaluationMode
from ..architecture.neural_architecture import DynamicNeuralArchitecture
from ..evaluation.adapter import UnifiedNASAdapter


class DebtOptimizer:
    """
    Debt-Based Optimization Framework
    
    Features:
    1. Stable encoding (soft-max, noise buffering)
    2. Learned surrogate (MLP trained on history)
    3. Successive Halving (budget optimization)
    4. Ablation flags (for benchmarking)
    5. Global memory (Bayesian-lite buffer)
    
    CORE: Pure debt-paying philosophy preserved
    """
    
    def __init__(self,
                 # Architecture params
                 min_layers: int = 2,
                 max_layers: int = 6,
                 max_units: int = 512,
                 # Debt core params
                 alpha_init: float = 0.3,
                 beta: float = 1.2,
                 gamma: float = 0.8,
                 delta: float = 0.5,
                 n_agents: int = 3,
                 council_weight: float = 0.15,
                 # Ablation flags
                 enable_council: bool = True,
                 enable_directional: bool = True,
                 enable_severity_scaling: bool = True,
                 # Evaluation params
                 mode: EvaluationMode = EvaluationMode.FAST,
                 eval_budget: int = 200,
                 enable_successive_halving: bool = True,
                 surrogate_update_freq: int = 20,
                 device: str = 'cpu'):
        
        self.min_layers = min_layers
        self.max_layers = max_layers
        self.max_units = max_units
        self.surrogate_update_freq = surrogate_update_freq
        
        # Pure debt core (with ablation support)
        self.core = PureDebtCore(
            alpha_init=alpha_init,
            beta=beta,
            gamma=gamma,
            delta=delta,
            n_agents=n_agents,
            council_weight=council_weight,
            enable_council=enable_council,
            enable_directional=enable_directional,
            enable_severity_scaling=enable_severity_scaling
        )
        
        # Enhanced adapter
        self.adapter = UnifiedNASAdapter(
            mode=mode,
            eval_budget=eval_budget,
            enable_early_reject=True,
            enable_complexity_penalty=True,
            enable_successive_halving=enable_successive_halving,
            min_layers=min_layers,
            max_layers=max_layers,
            device=device
        )
    
    def vector_to_arch(self, X: np.ndarray) -> DynamicNeuralArchitecture:
        """Convert vector to architecture"""
        arch = DynamicNeuralArchitecture(self.min_layers, self.max_layers, self.max_units)
        arch.from_vector(X)
        return arch
    
    def search(self, max_iterations: int = 200, verbose: bool = True) -> Tuple:
        """Main search loop with surrogate updates"""
        
        # Initialize council
        agents = []
        agent_fitness = []
        
        for _ in range(self.core.n_agents):
            arch = DynamicNeuralArchitecture(self.min_layers, self.max_layers, self.max_units)
            arch.initialize_random()
            X = arch.to_vector()
            fitness = self.adapter.evaluate(arch, 0, max_iterations, False)
            agents.append(X)
            agent_fitness.append(fitness)
        
        # Global best
        best_idx = np.argmin(agent_fitness)
        X_best = agents[best_idx].copy()
        best_fitness = agent_fitness[best_idx]
        best_arch = self.vector_to_arch(X_best)
        
        fitness_history = [best_fitness]
        eval_history = [self.adapter.evaluation_count]
        
        if verbose:
            self._print_header(best_fitness)
        
        # Main loop
        for iteration in range(max_iterations):
            if self.adapter.evaluation_count >= self.adapter.eval_budget:
                if verbose:
                    print(f"\n💰 Budget exhausted at iteration {iteration}")
                break
            
            # Update surrogate periodically
            if iteration % self.surrogate_update_freq == 0 and iteration > 0:
                self.adapter.update_surrogate()
                if verbose and self.adapter.mode == EvaluationMode.FAST:
                    print(f"🧠 Surrogate updated (memory size: {len(self.adapter.memory_vectors)})")
            
            alpha = self.core.natural_risk_decay(iteration, max_iterations)
            debt_records = []
            
            # Each agent performs debt-based optimization cycle
            for i in range(self.core.n_agents):
                X_current = agents[i]
                fitness_current = agent_fitness[i]
                
                # Fitness function for core
                def evaluate_fn(X):
                    arch = self.vector_to_arch(X)
                    return self.adapter.evaluate(arch, iteration, max_iterations, False)
                
                # Debt-based optimization cycle (UNCHANGED core logic)
                debt = self.core.conditional_debt_move(X_current, fitness_current, alpha, evaluate_fn)
                debt_records.append(debt)
                
                X_repay = self.core.severity_scaled_repayment(X_current, debt)
                X_double = self.core.severity_scaled_double_pay(X_repay, debt)
                X_smart = self.core.directional_intelligence(X_double, X_best, debt)
                
                smart_fitness = evaluate_fn(X_smart)
                
                # Accept if better
                if smart_fitness < agent_fitness[i]:
                    agents[i] = X_smart
                    agent_fitness[i] = smart_fitness
                    
                    # Update global best
                    if smart_fitness < best_fitness:
                        improvement = (best_fitness - smart_fitness) / best_fitness
                        self.core.record_improvement(best_fitness, smart_fitness)
                        
                        X_best = X_smart.copy()
                        best_fitness = smart_fitness
                        best_arch = self.vector_to_arch(X_best)
                        
                        if verbose and (iteration % 20 == 0 or improvement > 0.05):
                            mode_str = f"Mode: {self.adapter.mode.value}"
                            if self.adapter.mode == EvaluationMode.ACCURATE:
                                fid_str = f"L:{self.adapter.fidelity_counts['low']} " \
                                         f"M:{self.adapter.fidelity_counts['medium']} " \
                                         f"H:{self.adapter.fidelity_counts['high']}"
                                mode_str += f" [{fid_str}]"
                            
                            print(f"💰 Iter {iteration:4d}: Fitness {best_fitness:.4f} "
                                  f"(↓ {improvement*100:.2f}%) | α={alpha:.3f} | "
                                  f"Evals: {self.adapter.evaluation_count}/{self.adapter.eval_budget} | "
                                  f"{mode_str}")
            
            # Council consensus
            adjusted_agents = self.core.council_consensus(agents, debt_records)
            
            # Update agents and re-evaluate
            for i in range(self.core.n_agents):
                agents[i] = adjusted_agents[i]
                arch = self.vector_to_arch(agents[i])
                agent_fitness[i] = self.adapter.evaluate(arch, iteration, max_iterations, False)
                
                if agent_fitness[i] < best_fitness:
                    X_best = agents[i].copy()
                    best_fitness = agent_fitness[i]
                    best_arch = self.vector_to_arch(X_best)
            
            fitness_history.append(best_fitness)
            eval_history.append(self.adapter.evaluation_count)
        
        # Final surrogate update and high-fidelity evaluation
        if self.adapter.mode == EvaluationMode.FAST:
            self.adapter.update_surrogate()
        elif self.adapter.mode == EvaluationMode.ACCURATE:
            if self.adapter.evaluation_count < self.adapter.eval_budget:
                if verbose:
                    print(f"\n{'='*70}")
                    print("🔧 Final high-fidelity evaluation of best architecture...")
                
                final_fitness = self.adapter.evaluator.evaluate(best_arch, 'high')
                self.adapter.evaluation_count += 1
                self.adapter.fidelity_counts['high'] += 1
                
                if final_fitness < best_fitness:
                    best_fitness = final_fitness
                    if verbose:
                        print(f"✅ Improved to {best_fitness:.4f}")
        
        if verbose:
            self._print_summary(fitness_history, best_arch, best_fitness)
        
        return best_arch, best_fitness, fitness_history, eval_history
    
    def _print_header(self, initial_fitness: float):
        """Print search header"""
        print(f"{'='*70}")
        print(f"🍷 Debt-Based Optimization Framework")
        print(f"{'='*70}")
        print(f"📊 Evaluation Mode: {self.adapter.mode.value.upper()}")
        print(f"👥 Council Size: {self.core.n_agents} agents")
        print(f"⚙️  Core Parameters: α₀={self.core.alpha_init} β={self.core.beta} "
              f"γ={self.core.gamma} δ={self.core.delta}")
        print(f"🏗️  Search Space: {self.min_layers}-{self.max_layers} layers, "
              f"max {self.max_units} units")
        print(f"💰 Eval Budget: {self.adapter.eval_budget}")
        
        # Ablation status
        ablations = []
        if not self.core.enable_council:
            ablations.append("Council OFF")
        if not self.core.enable_directional:
            ablations.append("Directional OFF")
        if not self.core.enable_severity_scaling:
            ablations.append("Severity OFF")
        
        if ablations:
            print(f"🔬 Ablations: {', '.join(ablations)}")
        
        if self.adapter.mode == EvaluationMode.FAST:
            if self.adapter.surrogate is not None:
                print(f"🧠 Surrogate: Learned MLP")
            else:
                print(f"🧠 Surrogate: Heuristic (fallback)")
        else:
            print(f"🧠 Successive Halving: {self.adapter.enable_successive_halving}")
        
        print(f"🎯 Initial Best Fitness: {initial_fitness:.4f}")
        print(f"{'='*70}\n")
    
    def _print_summary(self, fitness_history: List[float],
                      best_arch: DynamicNeuralArchitecture,
                      best_fitness: float):
        """Print search summary"""
        print(f"\n{'='*70}")
        print("✅ SEARCH COMPLETE")
        print(f"{'='*70}")
        print(f"📊 Initial Fitness: {fitness_history[0]:.4f}")
        print(f"📊 Final Fitness: {best_fitness:.4f}")
        improvement_pct = ((fitness_history[0] - best_fitness) / fitness_history[0] * 100)
        print(f"📊 Total Improvement: {(fitness_history[0] - best_fitness):.4f} "
              f"({improvement_pct:.2f}%)")
        print(f"🔍 Total Evaluations: {self.adapter.evaluation_count}")
        print(f"💰 Budget Usage: {self.adapter.evaluation_count}/{self.adapter.eval_budget} "
              f"({self.adapter.evaluation_count/self.adapter.eval_budget*100:.1f}%)")
        
        if self.adapter.mode == EvaluationMode.ACCURATE:
            print(f"📈 Fidelity Distribution:")
            print(f"   Low: {self.adapter.fidelity_counts['low']} evals")
            print(f"   Medium: {self.adapter.fidelity_counts['medium']} evals")
            print(f"   High: {self.adapter.fidelity_counts['high']} evals")
            
            if self.adapter.enable_successive_halving:
                n_survivors = len(self.adapter.evaluator.sh_survivors)
                n_promoted = len(self.adapter.evaluator.sh_promoted)
                print(f"📈 Successive Halving:")
                print(f"   Survived to Medium: {n_survivors} architectures")
                print(f"   Promoted to High: {n_promoted} architectures")
        
        if self.adapter.mode == EvaluationMode.FAST:
            print(f"🧠 Surrogate Memory Size: {len(self.adapter.memory_vectors)} samples")
            if self.adapter.surrogate is not None:
                print(f"🧠 Surrogate Trained: {self.adapter.surrogate.trained}")
        
        print(f"\n{'='*70}")
        print("🏆 BEST ARCHITECTURE FOUND:")
        print(f"{'='*70}")
        print(best_arch)
        print(f"{'='*70}\n")
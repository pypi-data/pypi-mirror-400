import numpy as np
import pytest

from debt_optimization.evaluation.adapter import UnifiedNASAdapter
from debt_optimization.architecture.neural_architecture import DynamicNeuralArchitecture
from debt_optimization.core.evaluation_modes import EvaluationMode


def test_add_to_memory_and_limits():
    adapter = UnifiedNASAdapter(mode=EvaluationMode.FAST, eval_budget=10)
    v = np.zeros(10)
    for i in range(adapter.max_memory_size + 5):
        adapter.add_to_memory(v, float(i))

    assert len(adapter.memory_vectors) == adapter.max_memory_size
    assert len(adapter.memory_fitness) == adapter.max_memory_size


def test_heuristic_evaluate_and_complexity_penalty():
    adapter = UnifiedNASAdapter(mode=EvaluationMode.FAST, eval_budget=100)
    arch = DynamicNeuralArchitecture()
    arch.initialize_random()
    f1 = adapter.evaluate(arch)
    # subsequent calls increase evaluation count and memory
    f2 = adapter.evaluate(arch)
    assert isinstance(f1, float)
    assert adapter.evaluation_count >= 2
    # complexity penalty added, so fitness should be finite and non-negative
    assert f1 >= 0


def test_select_fidelity_fast_mode():
    adapter = UnifiedNASAdapter(mode=EvaluationMode.FAST, eval_budget=10)
    assert adapter.select_fidelity(0, 100) == 'fast'

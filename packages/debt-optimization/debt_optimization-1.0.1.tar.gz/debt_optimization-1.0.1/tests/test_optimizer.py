from debt_optimization.optimizer.optimizer import DebtOptimizer
from debt_optimization import EvaluationMode


def test_optimizer_runs_minimal_search():
    opt = DebtOptimizer(mode=EvaluationMode.FAST, eval_budget=10, n_agents=2)
    best_arch, best_fitness, history, evals = opt.search(max_iterations=5, verbose=False)

    assert hasattr(best_arch, 'n_layers')
    assert isinstance(best_fitness, float)
    assert len(history) >= 1

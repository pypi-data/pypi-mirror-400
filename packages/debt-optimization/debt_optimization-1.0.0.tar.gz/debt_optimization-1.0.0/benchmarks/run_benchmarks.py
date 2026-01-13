"""
Lightweight benchmarking harness for TL-DPO vs simple NAS baselines.

Usage: run from repository root or after editable install:
    python -m debt_optimization.benchmarks.run_benchmarks

This script runs quick, repeatable comparisons in FAST mode and
saves results to `benchmarks/results.csv`.
"""
import time
import csv
import os
from typing import Callable, Dict

import numpy as np

from debt_optimization import DebtOptimizer, EvaluationMode
from debt_optimization.architecture.neural_architecture import DynamicNeuralArchitecture
try:
    import torch
    PYTORCH_AVAILABLE = True
except Exception:
    PYTORCH_AVAILABLE = False


def random_search(eval_fn: Callable, n_evals: int):
    best = None
    best_f = float('inf')
    for _ in range(n_evals):
        arch = DynamicNeuralArchitecture()
        arch.initialize_random()
        f = eval_fn(arch)
        if f < best_f:
            best_f = f
            best = arch
    return best, best_f


def hill_climber(eval_fn: Callable, n_iters: int):
    # start with random
    arch = DynamicNeuralArchitecture()
    arch.initialize_random()
    best = arch
    best_f = eval_fn(arch)

    for _ in range(n_iters):
        # make a small random neighbor by perturbing vector
        v = arch.to_vector()
        v2 = np.clip(v + 0.05 * np.random.randn(len(v)), 0, 1)
        cand = DynamicNeuralArchitecture()
        cand.from_vector(v2)
        f = eval_fn(cand)
        if f < best_f:
            best_f = f
            best = cand
            arch = cand

    return best, best_f


def genetic_search(eval_fn: Callable, n_evals: int, pop_size: int = 10):
    # Simple GA on vector encoding
    # initialize population
    pop = []
    pop_f = []
    for _ in range(pop_size):
        a = DynamicNeuralArchitecture()
        a.initialize_random()
        pop.append(a)
        pop_f.append(eval_fn(a))

    evals = 0
    while evals < n_evals:
        # tournament selection
        i1, i2 = np.random.choice(len(pop), 2, replace=False)
        parent = pop[i1] if pop_f[i1] < pop_f[i2] else pop[i2]

        # mutate: small gaussian on vector
        v = parent.to_vector()
        child_v = np.clip(v + 0.08 * np.random.randn(len(v)), 0, 1)
        child = DynamicNeuralArchitecture()
        child.from_vector(child_v)
        child_f = eval_fn(child)
        evals += 1

        # replace worst if child better
        worst_idx = int(np.argmax(pop_f))
        if child_f < pop_f[worst_idx]:
            pop[worst_idx] = child
            pop_f[worst_idx] = child_f

    best_idx = int(np.argmin(pop_f))
    return pop[best_idx], pop_f[best_idx]


def regularized_evolution(eval_fn: Callable, n_evals: int, population_size: int = 10, tournament_size: int = 3):
    # Simple age-based evolution (regularized evolution)
    population = []  # list of (arch, fitness, age)
    # init
    for _ in range(population_size):
        a = DynamicNeuralArchitecture(); a.initialize_random()
        population.append([a, eval_fn(a), 0])

    evals = 0
    while evals < n_evals:
        # sample tournament
        contenders = np.random.choice(len(population), tournament_size, replace=False)
        # select best
        best_idx = min(contenders, key=lambda i: population[i][1])
        parent = population[best_idx][0]

        # mutate
        v = parent.to_vector()
        child_v = np.clip(v + 0.06 * np.random.randn(len(v)), 0, 1)
        child = DynamicNeuralArchitecture(); child.from_vector(child_v)
        child_f = eval_fn(child)
        evals += 1

        # add child and remove oldest
        population.append([child, child_f, 0])
        # increment ages
        for p in population:
            p[2] += 1
        # remove oldest
        population.sort(key=lambda x: x[2], reverse=True)
        population = population[:population_size]

    best = min(population, key=lambda x: x[1])
    return best[0], best[1]


def run_once(trial_id: int, eval_budget: int = 60):
    # create a DebtOptimizer in FAST mode (surrogate)
    opt = DebtOptimizer(mode=EvaluationMode.FAST, eval_budget=eval_budget, n_agents=3)

    def eval_fn(arch):
        return opt.adapter.evaluate(arch, 0, 10, False)

    results: Dict[str, Dict] = {}

    start = time.time()
    best_tl, f_tl, history, evals = opt.search(max_iterations=50, verbose=False)
    results['tl_dpo'] = {'fitness': float(f_tl), 'time': time.time() - start}

    # Random search baseline
    start = time.time()
    best_rs, f_rs = random_search(eval_fn, eval_budget)
    results['random'] = {'fitness': float(f_rs), 'time': time.time() - start}

    # Hill-climber baseline
    start = time.time()
    best_hc, f_hc = hill_climber(eval_fn, int(eval_budget / 2))
    results['hill_climber'] = {'fitness': float(f_hc), 'time': time.time() - start}

    # Genetic NAS baseline
    start = time.time()
    best_ga, f_ga = genetic_search(eval_fn, eval_budget, pop_size=12)
    results['genetic'] = {'fitness': float(f_ga), 'time': time.time() - start}

    # Regularized evolution baseline
    start = time.time()
    best_re, f_re = regularized_evolution(eval_fn, eval_budget, population_size=12, tournament_size=3)
    results['reg_evo'] = {'fitness': float(f_re), 'time': time.time() - start}

    # Optional: ENAS-like controller (requires PyTorch)
    if PYTORCH_AVAILABLE:
        try:
            start = time.time()
            # lightweight controller: sample random architectures but bias by learned linear model (placeholder)
            # This is a proxy for ENAS; full ENAS requires training a controller and shared weights.
            best_enas_f = float('inf')
            for _ in range(int(eval_budget/2)):
                a = DynamicNeuralArchitecture(); a.initialize_random()
                f = eval_fn(a)
                if f < best_enas_f:
                    best_enas_f = f
            results['enas_proxy'] = {'fitness': float(best_enas_f), 'time': time.time() - start}
        except Exception:
            results['enas_proxy'] = {'fitness': float('inf'), 'time': 0.0}

    return results


def main(repeats: int = 3, eval_budget: int = 80):
    out_dir = os.path.join(os.path.dirname(__file__), '.')
    os.makedirs(out_dir, exist_ok=True)
    out_csv = os.path.join(out_dir, 'results.csv')

    rows = []
    for t in range(repeats):
        print(f"Running trial {t+1}/{repeats} (budget={eval_budget})...")
        res = run_once(t, eval_budget=eval_budget)
        for alg, info in res.items():
            rows.append({'trial': t, 'algorithm': alg, 'fitness': info['fitness'], 'time': info['time']})

    # write CSV
    with open(out_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['trial', 'algorithm', 'fitness', 'time'])
        writer.writeheader()
        writer.writerows(rows)

    # Print summary
    print('\nBenchmark summary:')
    summary = {}
    for r in rows:
        summary.setdefault(r['algorithm'], []).append(r['fitness'])

    for alg, vals in summary.items():
        print(f" - {alg}: mean fitness={np.mean(vals):.4f}, std={np.std(vals):.4f}")

    print(f"\nResults saved to: {out_csv}")


if __name__ == '__main__':
    main()

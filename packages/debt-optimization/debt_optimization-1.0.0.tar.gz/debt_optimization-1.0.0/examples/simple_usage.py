"""
Simple usage example of the Debt-Based Optimization Framework.

This demonstrates the most basic usage pattern.
"""

from debt_optimization import DebtOptimizer, EvaluationMode, plot_convergence


def main():
    print("=" * 70)
    print("Simple Usage Example: Debt-Based Optimization")
    print("=" * 70 + "\n")
    
    # Create optimizer with default settings
    optimizer = DebtOptimizer(
        mode=EvaluationMode.FAST,  # Use fast surrogate-based evaluation
        eval_budget=100,            # Allow 100 evaluations
        n_agents=3                  # Use 3 agents in the council
    )
    
    # Run the optimization
    print("Starting optimization...\n")
    best_arch, fitness, history, evals = optimizer.search(
        max_iterations=100,
        verbose=True
    )
    
    # Display results
    print("\n" + "=" * 70)
    print("OPTIMIZATION COMPLETE")
    print("=" * 70)
    print(f"\nBest Architecture Found:")
    print(best_arch)
    print(f"\nFinal Fitness: {fitness:.4f}")
    print(f"Total Evaluations: {len(evals)}")
    
    # Plot convergence
    print("\nGenerating plots...")
    plot_convergence(history, evals, EvaluationMode.FAST, "(Simple Example)")


if __name__ == "__main__":
    main()
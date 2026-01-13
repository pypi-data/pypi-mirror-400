"""
Visualize benchmark results saved by `run_benchmarks.py`.

Generates boxplots and bar charts comparing algorithms.
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_results(csv_path: str, out_dir: str = None):
    df = pd.read_csv(csv_path)
    if out_dir is None:
        out_dir = os.path.dirname(csv_path)
    os.makedirs(out_dir, exist_ok=True)

    sns.set(style='whitegrid')

    plt.figure(figsize=(8, 5))
    sns.boxplot(x='algorithm', y='fitness', data=df)
    plt.title('Fitness Distribution by Algorithm')
    plt.tight_layout()
    out = os.path.join(out_dir, 'fitness_boxplot.png')
    plt.savefig(out)
    plt.close()

    # Mean fitness bar
    means = df.groupby('algorithm')['fitness'].agg(['mean','std']).reset_index()
    plt.figure(figsize=(8,4))
    ax = sns.barplot(x='algorithm', y='mean', data=means, ci=None)
    # Add error bars manually to avoid passing yerr into seaborn (compatibility issues)
    x_coords = range(len(means))
    y_vals = means['mean'].values
    y_err = means['std'].values
    ax.errorbar(x=x_coords, y=y_vals, yerr=y_err, fmt='none', ecolor='k', capsize=5)
    plt.title('Mean Fitness by Algorithm')
    plt.tight_layout()
    out = os.path.join(out_dir, 'fitness_mean.png')
    plt.savefig(out)
    plt.close()

    # Time comparison
    plt.figure(figsize=(8,4))
    sns.barplot(x='algorithm', y='time', data=df)
    plt.title('Run Time by Algorithm (per trial)')
    plt.tight_layout()
    out = os.path.join(out_dir, 'time_by_algorithm.png')
    plt.savefig(out)
    plt.close()

    print(f"Saved plots to {out_dir}")


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Usage: python visualize_results.py path/to/results.csv')
    else:
        plot_results(sys.argv[1])

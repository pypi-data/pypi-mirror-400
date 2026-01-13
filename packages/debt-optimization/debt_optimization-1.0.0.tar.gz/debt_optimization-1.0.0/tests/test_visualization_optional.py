import os
import csv
import pytest

try:
    import pandas as pd
except Exception:
    pd = None


def test_visualization_runs(tmp_path):
    if pd is None:
        pytest.skip("pandas not installed")

    # create small CSV
    csv_path = tmp_path / "results.csv"
    rows = [
        {'trial': 0, 'algorithm': 'a', 'fitness': 1.0, 'time': 0.1},
        {'trial': 0, 'algorithm': 'b', 'fitness': 2.0, 'time': 0.2},
    ]
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['trial','algorithm','fitness','time'])
        writer.writeheader()
        writer.writerows(rows)

    # import and run plot
    from debt_optimization.benchmarks.visualize_results import plot_results
    plot_results(str(csv_path), out_dir=str(tmp_path))

    # check outputs
    assert (tmp_path / 'fitness_boxplot.png').exists()
    assert (tmp_path / 'fitness_mean.png').exists()
    assert (tmp_path / 'time_by_algorithm.png').exists()

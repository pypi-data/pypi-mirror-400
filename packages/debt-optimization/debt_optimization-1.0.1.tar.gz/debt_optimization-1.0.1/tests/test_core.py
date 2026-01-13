import numpy as np
from debt_optimization.core.debt_core import PureDebtCore, DebtRecord


def test_conditional_debt_move_creates_debt_when_worse():
    core = PureDebtCore()

    X = np.array([0.5, 0.5, 0.5])

    def evaluate_fn_worse(x):
        # make the perturbed candidate always worse
        return 10.0

    debt = core.conditional_debt_move(X, fitness_current=1.0, alpha=0.1, evaluate_fn=evaluate_fn_worse)
    assert isinstance(debt, DebtRecord)
    assert debt.exists is True
    assert debt.severity > 0


def test_repayment_moves_opposite_direction():
    core = PureDebtCore(beta=1.5, gamma=0.5)
    X = np.array([0.2, 0.4, 0.6])
    debt_record = DebtRecord(vector=np.array([0.1, -0.05, 0.0]), severity=0.1, exists=True, fitness_before=2.0, fitness_after=3.0)

    X_repay = core.severity_scaled_repayment(X, debt_record)
    # repayment should move opposite sign of debt vector
    assert np.allclose(np.sign(X_repay - X), -np.sign(debt_record.vector)) or np.all(debt_record.vector == 0)

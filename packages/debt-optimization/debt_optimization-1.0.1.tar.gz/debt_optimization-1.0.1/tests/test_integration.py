import numpy as np
from debt_optimization.architecture.neural_architecture import DynamicNeuralArchitecture


def test_vector_roundtrip_consistency():
    arch = DynamicNeuralArchitecture(min_layers=2, max_layers=4, max_units=128)
    arch.initialize_random()
    v = arch.to_vector()

    arch2 = DynamicNeuralArchitecture(min_layers=2, max_layers=4, max_units=128)
    arch2.from_vector(v)
    v2 = arch2.to_vector()

    # vectors should be same length and reasonably close for encoded fields
    assert v.shape == v2.shape
    assert np.allclose(v[:5], v2[:5], atol=1.0)

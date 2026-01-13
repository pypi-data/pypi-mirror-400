def test_examples_modules_importable():
    import importlib
    mods = [
        'debt_optimization.examples.simple_usage',
        'debt_optimization.examples.demo'
    ]
    for m in mods:
        mod = importlib.import_module(m)
        assert mod is not None

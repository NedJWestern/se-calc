"""Checks every calculator follows the conventions in CLAUDE.md, so the site can be generated."""

from pathlib import Path

import pytest

from se_calc.registry import discover
from se_calc.spec import output_units, params

CALCULATORS = discover()
TESTS = Path(__file__).parent


def test_at_least_one_calculator():
    assert CALCULATORS


@pytest.mark.parametrize("module, func", CALCULATORS, ids=[f.__name__ for _, f in CALCULATORS])
def test_calculator_conventions(module, func):
    assert func.__doc__ and func.__doc__.strip(), "needs a docstring describing the calculation"
    params(func)  # raises if an argument lacks Input metadata or a default
    result = func()
    assert isinstance(result, dict), "must return a dict of outputs"
    undeclared = set(result) - set(output_units(func))
    assert not undeclared, f"returned outputs missing from @calculator(outputs=...): {undeclared}"
    assert (TESTS / f"test_{module}.py").exists(), f"needs tests in tests/test_{module}.py"


def test_dropdown_defaults_are_options():
    for _, func in CALCULATORS:
        for p in params(func):
            if p.spec.options is not None:
                assert p.default in p.spec.options, f"{func.__name__}.{p.name}"

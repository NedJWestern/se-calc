"""Reference values from the worked example in .github/ISSUE_TEMPLATE/calculator.md."""

import pytest

from calcs.example_beam import example_simply_supported_beam


def test_matches_worked_example():
    result = example_simply_supported_beam(span=6, dead_load=5, live_load=3, phi_Mu=50)
    assert result["w_star"] == pytest.approx(10.5)
    assert result["M_star"] == pytest.approx(47.25)
    assert result["V_star"] == pytest.approx(31.5)
    assert result["bending_check"] == "PASS"


def test_bending_fails_when_capacity_too_low():
    result = example_simply_supported_beam(span=6, dead_load=5, live_load=3, phi_Mu=47)
    assert result["bending_check"] == "FAIL"


def test_bending_passes_when_moment_equals_capacity():
    result = example_simply_supported_beam(span=6, dead_load=5, live_load=3, phi_Mu=47.25)
    assert result["bending_check"] == "PASS"

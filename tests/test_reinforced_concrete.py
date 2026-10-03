"""Reference values come from tmp/Reinforced Concrete strip calculator.xlsx (Calculator sheet)."""

import pytest

from calcs.reinforced_concrete import reinforced_concrete_strip

EXCEL_DEFAULTS = {
    "Ec": 30100,
    "depth_to_compression_steel": 60,
    "depth_to_tensile_steel": 140,
    "converted_compression_steel": 5672.740863787375,
    "converted_tensile_steel": 6677.740863787375,
    "f_ct_f": 3.394112549695428,
    "gamma": 0.89,
    "alpha_2": 0.802,
    "serviceability_dn": 39.64019767189173,
    "kcs": 2,
    "ultimate_dn": 37.660216241661466,
    "kuo": 0.26900154458329617,
    "capacity_reduction_factor_bending": 0.85,
    "slenderness_limit": 60,
    "beam_minimum_strength_moment": 27.152900397563425,
}


@pytest.mark.parametrize("key, expected", EXCEL_DEFAULTS.items())
def test_matches_excel_for_default_inputs(key, expected):
    assert reinforced_concrete_strip()[key] == pytest.approx(expected, rel=1e-9)


def test_default_checks_pass():
    result = reinforced_concrete_strip()
    assert result["kuo_check"] == "PASS"
    assert result["slenderness_check"] == "PASS"


def test_forces_are_in_equilibrium():
    result = reinforced_concrete_strip()
    assert result["force_equilibrium_error"] == pytest.approx(0, abs=1e-6)


def test_cantilever_uses_cantilever_slenderness_limit():
    assert reinforced_concrete_strip(beam_type="Cantilever")["slenderness_limit"] == 25


def test_slenderness_fails_for_long_unrestrained_length():
    result = reinforced_concrete_strip(distance_between_lateral_supports=61_000)
    assert result["slenderness_check"] == "FAIL"


@pytest.mark.parametrize("slab_support", ["Columns", "Walls or beams"])
def test_slab_reports_minimum_strength_check_instead_of_beam_moment(slab_support):
    result = reinforced_concrete_strip(member="Slab", slab_support=slab_support)
    assert result["slab_minimum_strength_check"] == "PASS"
    assert "beam_minimum_strength_moment" not in result


def test_capacity_reduction_factor_floor_for_heavily_reinforced_section():
    result = reinforced_concrete_strip(as_tension=6000, as_compression=0)
    assert result["kuo_check"] == "FAIL"
    assert result["capacity_reduction_factor_bending"] == 0.65

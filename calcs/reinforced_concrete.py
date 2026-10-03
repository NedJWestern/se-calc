from math import sqrt
from typing import Annotated

from calcs.common import CONCRETE_EC
from se_calc import Input, calculator

# Fixed values mandated by AS 3600
XI_CU = 0.003  # ultimate concrete strain
ES = 200_000  # MPa, modulus of elasticity of steel
F_SY = 500  # MPa, yield strength of reinforcement


@calculator(
    title="Reinforced Concrete Strip",
    outputs={
        "Ec": "MPa",
        "n": "-",
        "depth_to_compression_steel": "mm",
        "depth_to_tensile_steel": "mm",
        "converted_compression_steel": "mm²",
        "converted_tensile_steel": "mm²",
        "f_ct_f": "MPa",
        "gamma": "-",
        "alpha_2": "-",
        "serviceability_dn": "mm",
        "kcs": "-",
        "ultimate_dn": "mm",
        "kuo": "-",
        "kuo_check": "-",
        "capacity_reduction_factor_bending": "-",
        "slenderness_limit": "-",
        "slenderness_check": "-",
        "beam_minimum_strength_moment": "kNm",
        "slab_minimum_strength_check": "-",
        "force_equilibrium_error": "N",
    },
)
def reinforced_concrete_strip(
    member: Annotated[str, Input(options=("Beam", "Slab"))] = "Beam",
    slab_support: Annotated[str, Input(options=("Columns", "Walls or beams"))] = "Columns",
    beam_type: Annotated[
        str, Input(options=("Simply supported", "Continuous", "Cantilever"))
    ] = "Simply supported",
    depth: Annotated[float, Input("mm", min=100, max=1500, step=10)] = 200,
    width: Annotated[float, Input("mm", min=100, max=3000, step=50)] = 1000,
    distance_between_lateral_supports: Annotated[float, Input("mm", min=0, step=100)] = 0,
    fc: Annotated[int, Input("MPa", label="f'c", options=tuple(CONCRETE_EC))] = 32,
    as_compression: Annotated[float, Input("mm²", label="As compression", min=0)] = 1005,
    as_tension: Annotated[float, Input("mm²", label="As tension", min=1)] = 1005,
    cover_compression: Annotated[float, Input("mm", min=0)] = 60,
    cover_tension: Annotated[float, Input("mm", min=0)] = 60,
) -> dict:
    r"""
    Section properties, ultimate neutral axis depth, capacity reduction factor,
    slenderness and minimum strength checks for a rectangular reinforced concrete
    beam or slab strip to AS 3600:2018.

    Fixed values: $\xi_{cu} = 0.003$, $E_s = 200\,000$ MPa, $f_{sy} = 500$ MPa.
    """
    Ec = CONCRETE_EC[fc]
    n = ES / Ec

    # Simple outputs
    d_sc = cover_compression
    d = depth - cover_tension
    converted_compression_steel = as_compression * (n - 1)
    converted_tensile_steel = as_tension * n
    f_ct_f = 0.6 * sqrt(fc)
    gamma = max(0.67, 0.97 - 0.0025 * fc)
    alpha_2 = max(0.67, 0.85 - 0.0015 * fc)

    # Serviceability neutral axis depth: a*dn^2 + b*dn + c = 0
    a = width / 2
    b = converted_compression_steel + converted_tensile_steel
    c = -(converted_compression_steel * d_sc + converted_tensile_steel * d)
    serviceability_dn = (-b + sqrt(b**2 - 4 * a * c)) / (2 * a)

    # Kcs: compression steel only counts if it lies within the compression zone
    as_compression_effective = as_compression if serviceability_dn > d_sc else 0
    kcs = max(0.8, 2 - 1.2 * as_compression_effective / as_tension)

    # Ultimate neutral axis depth from Cc + Cs = Ts, assuming tension steel yields
    a = gamma * width * alpha_2 * fc
    b = ES * as_compression * XI_CU - as_tension * F_SY
    c = -ES * as_compression * XI_CU * d_sc
    ultimate_dn = (-b + sqrt(b**2 - 4 * a * c)) / (2 * a)

    kuo = ultimate_dn / d
    capacity_reduction_factor_bending = min(0.85, max(0.65, 1.24 - 13 * kuo / 12))

    # Slenderness
    if beam_type == "Cantilever":
        slenderness_limit = min(25, 100 * width / depth)
    else:
        slenderness_limit = min(60, 180 * width / depth)
    slenderness_ok = distance_between_lateral_supports / width < slenderness_limit

    result = {
        "Ec": Ec,
        "n": n,
        "depth_to_compression_steel": d_sc,
        "depth_to_tensile_steel": d,
        "converted_compression_steel": converted_compression_steel,
        "converted_tensile_steel": converted_tensile_steel,
        "f_ct_f": f_ct_f,
        "gamma": gamma,
        "alpha_2": alpha_2,
        "serviceability_dn": serviceability_dn,
        "kcs": kcs,
        "ultimate_dn": ultimate_dn,
        "kuo": kuo,
        "kuo_check": "PASS" if kuo < 0.36 else "FAIL",
        "capacity_reduction_factor_bending": capacity_reduction_factor_bending,
        "slenderness_limit": slenderness_limit,
        "slenderness_check": "PASS" if slenderness_ok else "FAIL",
    }

    # Minimum strength
    if member == "Beam":
        result["beam_minimum_strength_moment"] = 1.2 * (width * depth**2 / 6) * f_ct_f / 1e6
    else:
        coefficient = 0.24 if slab_support == "Columns" else 0.19
        ok = coefficient * (depth / d) ** 2 * f_ct_f / F_SY < as_tension / (d * width)
        result["slab_minimum_strength_check"] = "PASS" if ok else "FAIL"

    # Force equilibrium check, should be ~0
    ts = as_tension * F_SY
    cc = gamma * ultimate_dn * width * alpha_2 * fc
    xi_sc = XI_CU * (ultimate_dn - d_sc) / ultimate_dn
    cs = xi_sc * ES * as_compression
    result["force_equilibrium_error"] = ts - cc - cs

    return result

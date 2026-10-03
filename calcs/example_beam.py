"""Example calculator, matching the default issue template.

Submitting the template unchanged asks Claude to rewrite this file, which demonstrates the
workflow without adding a new calculator each time.
"""

from typing import Annotated

from se_calc import Input, calculator

# AS/NZS 1170.0 Cl 4.2.2 ultimate load combination 1.2G + 1.5Q
G_FACTOR = 1.2
Q_FACTOR = 1.5


@calculator(
    title="Example: Simply Supported Beam",
    outputs={
        "w_star": "kN/m",
        "M_star": "kNm",
        "V_star": "kN",
        "bending_check": "-",
    },
)
def example_simply_supported_beam(
    span: Annotated[float, Input("m", label="Span L", min=0.5, max=20, step=0.1)] = 6,
    dead_load: Annotated[float, Input("kN/m", label="Dead load G", min=0)] = 5,
    live_load: Annotated[float, Input("kN/m", label="Live load Q", min=0)] = 3,
    phi_Mu: Annotated[float, Input("kNm", label="Bending capacity φMu", min=0)] = 50,
) -> dict:
    r"""
    Design bending moment and shear for a simply supported beam under a uniformly
    distributed load, factored per AS/NZS 1170.0 Cl 4.2.2 ($1.2G + 1.5Q$).

    $w^* = 1.2G + 1.5Q$, $\quad M^* = w^* L^2 / 8$, $\quad V^* = w^* L / 2$
    """
    w_star = G_FACTOR * dead_load + Q_FACTOR * live_load
    M_star = w_star * span**2 / 8
    V_star = w_star * span / 2
    return {
        "w_star": w_star,
        "M_star": M_star,
        "V_star": V_star,
        "bending_check": "PASS" if M_star <= phi_Mu else "FAIL",
    }

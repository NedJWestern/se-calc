"""Shared engineering data used by several calculators."""

# AS 3600:2018 Table 3.1.2 - mean modulus of elasticity of concrete at 28 days.
# f'c (MPa) -> Ec (MPa)
CONCRETE_EC = {
    20: 24000,
    25: 26700,
    32: 30100,
    40: 32800,
    50: 34800,
    65: 37400,
    80: 39600,
    100: 42200,
}

---
name: New or changed calculator
about: Ask Claude to add or modify a calculator
title: "Calculator: "
---

@claude please implement this calculator request.

**New calculator or change to an existing one?**
Replace the example calculator in `calcs/example_beam.py`.

**What does it calculate, and which standard/clause?**
Design bending moment and shear for a simply supported beam under a uniformly
distributed load, factored per AS/NZS 1170.0 Cl 4.2.2 (1.2G + 1.5Q).

**Inputs** (name, unit, typical value, sensible min/max)
- Span L, m, typical 6, min 0.5, max 20
- Dead load G, kN/m, typical 5, min 0
- Live load Q, kN/m, typical 3, min 0
- Bending capacity φMu, kNm, typical 50, min 0

**Formulas / method** (paste from Excel, a textbook page, or describe in words)
w* = 1.2G + 1.5Q
M* = w* L² / 8
V* = w* L / 2

**Outputs and checks** (name, unit, pass/fail condition)
- w*, kN/m
- M*, kNm
- V*, kN
- Bending check: PASS if M* <= φMu

**Worked example** (input values and the answers you expect; these become the tests)
L = 6, G = 5, Q = 3, φMu = 50
w* = 1.2(5) + 1.5(3) = 10.5 kN/m
M* = 10.5 × 6² / 8 = 47.25 kNm
V* = 10.5 × 6 / 2 = 31.5 kN
Bending check: 47.25 <= 50 → PASS

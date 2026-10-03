# se-calc

Structural engineering calculators. Each calculator is a plain Python function; the web pages
are generated from it and published to GitHub Pages when changes reach `main`.

Requests usually come from structural engineers who are not programmers, via GitHub issues
mentioning @claude. Explain changes in engineering terms, not code terms.

## Where things go

- `calcs/<topic>.py`: calculators. This is the only place engineering logic lives.
- `calcs/common.py`: shared tables and constants (e.g. `CONCRETE_EC`).
- `calcs/example_beam.py`: demo calculator matching the default issue template. Requests that
  say to replace it should rewrite this file and `tests/test_example_beam.py` in place, not add new ones.
- `tests/test_<topic>.py`: tests for `calcs/<topic>.py`. Required for every calcs module.
- `se_calc/`: the framework (UI generation, site build). Don't change it for a calculator request.

## Calculator conventions

```python
from typing import Annotated
from se_calc import Input, calculator

@calculator(title="Human readable title", outputs={"result_name": "unit", ...})
def my_calc(
    depth: Annotated[float, Input("mm", min=100, max=1500, step=10)] = 200,
    grade: Annotated[int, Input("MPa", label="f'c", options=(25, 32, 40))] = 32,
) -> dict:
    r"""What it calculates and the standard/clause it follows. Markdown and $LaTeX$ allowed."""
    ...
    return {"result_name": value, "some_check": "PASS" if ok else "FAIL"}
```

- Every argument needs `Annotated[..., Input(unit, ...)]` and a sensible default. `options=`
  gives a dropdown, and the default must be one of the options.
- Return a flat dict. Every key must be listed in `outputs=` with its unit (`"-"` if none),
  in the order to display. Checks return the strings `"PASS"` or `"FAIL"`.
- Pure maths only: no printing, files, Marimo or network. Standard library only, because
  pages run in the browser via Pyodide.
- Units: mm, m (spans), MPa, N, kN, kN/m, kNm, mm². Put fixed code values (e.g. ξcu, Es) as module-level
  constants with a comment citing the standard.
- Use engineering variable names close to the standard's symbols, with comments citing clauses.

## Tests

- Every calculator needs reference-value tests from an independent source: the engineer's
  worked example, a spreadsheet, or a textbook. Never derive expected values by running the code.
  If the issue has no worked example, ask for one before writing the calculator.
- Also test each branch (e.g. slab vs beam) and each PASS/FAIL check flipping.
- `tests/test_conventions.py` checks every calculator automatically; keep it passing.

## Commands

- `uv run pytest`: run all tests (must pass before opening a PR).
- `uv run python -m se_calc.build --no-export`: generate notebooks in `build/notebooks/`.
- `uv run python -m se_calc.build`: also export the static site to `build/site/`.
- `uv run marimo edit build/notebooks/<name>.py`: try a generated calculator locally.

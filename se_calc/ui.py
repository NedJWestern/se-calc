"""Build a Marimo interface from a calculator's signature and outputs."""

import inspect

import marimo as mo

from se_calc.spec import output_units, params, title


def header(func):
    doc = inspect.cleandoc(func.__doc__ or "")
    return mo.md(f"# {title(func)}\n\n{doc}")


def input_form(func):
    """A form of widgets whose `.value` can be passed straight to `func(**value)`."""
    widgets = {}
    for p in params(func):
        label = p.label if p.spec.unit == "-" else f"{p.label} ({p.spec.unit})"
        if p.spec.options is not None:
            options = {str(o): o for o in p.spec.options}
            widgets[p.name] = mo.ui.dropdown(options=options, value=str(p.default), label=label)
        else:
            widgets[p.name] = mo.ui.number(
                start=p.spec.min,
                stop=p.spec.max,
                step=p.spec.step,
                value=p.default,
                label=label,
            )
    template = "\n\n".join(f"{{{name}}}" for name in widgets)
    return mo.md("## Inputs\n\n" + template).batch(**widgets)


def _format(value) -> str:
    if value == "PASS":
        return "✅ PASS"
    if value == "FAIL":
        return "❌ FAIL"
    if isinstance(value, float):
        return f"{value:.4g}" if abs(value) < 1e5 else f"{value:,.0f}"
    return str(value)


def results(func, values: dict):
    try:
        result = func(**values)
    except Exception as e:  # show engineering errors (e.g. sqrt of negative) to the user
        return mo.callout(mo.md(f"**Could not calculate:** {e}"), kind="danger")
    units = output_units(func)
    rows = ["| Output | Value | Unit |", "| -- | -- | -- |"]
    for key in [k for k in units if k in result] + [k for k in result if k not in units]:
        rows.append(f"| {key} | {_format(result[key])} | {units.get(key, '')} |")
    return mo.md("## Results\n\n" + "\n".join(rows))

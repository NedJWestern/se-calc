"""Generate and export one Marimo WASM page per calculator, plus an index page.

Usage: uv run python -m se_calc.build [--no-export]

Output:
  build/notebooks/<calculator>.py   generated Marimo notebooks (open with `marimo edit` to debug)
  build/site/                       static site for GitHub Pages
"""

import html
import shutil
import subprocess
import sys
from pathlib import Path

import marimo

from se_calc.registry import discover
from se_calc.spec import title

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
PACKAGES = ("se_calc", "calcs")

# The WASM page cannot import files from this repo, so the generated notebook carries the
# source of `se_calc` and `calcs` and writes them into the in-browser filesystem on start-up.
NOTEBOOK = '''\
import marimo

__generated_with = {version!r}
app = marimo.App(width="medium", app_title={title!r})


@app.cell(hide_code=True)
def _():
    import importlib
    import pathlib
    import sys
    import tempfile

    import marimo as mo

    _sources = {sources!r}
    _root = pathlib.Path(tempfile.mkdtemp())
    for _path, _text in _sources.items():
        (_root / _path).parent.mkdir(parents=True, exist_ok=True)
        (_root / _path).write_text(_text)
    sys.path.insert(0, str(_root))

    ui = importlib.import_module("se_calc.ui")
    calc = getattr(importlib.import_module({module!r}), {function!r})
    return calc, mo, ui


@app.cell(hide_code=True)
def _(calc, ui):
    ui.header(calc)
    return


@app.cell(hide_code=True)
def _(calc, ui):
    form = ui.input_form(calc)
    form
    return (form,)


@app.cell(hide_code=True)
def _(calc, form, ui):
    ui.results(calc, form.value)
    return


if __name__ == "__main__":
    app.run()
'''

INDEX = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Structural Engineering Calculators</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 40rem; margin: 2rem auto; padding: 0 1rem; }}
  li {{ margin: 0.5rem 0; }}
</style>
</head>
<body>
<h1>Structural Engineering Calculators</h1>
<ul>
{items}
</ul>
</body>
</html>
"""


def _sources() -> dict[str, str]:
    return {
        str(path.relative_to(ROOT)): path.read_text()
        for package in PACKAGES
        for path in sorted((ROOT / package).rglob("*.py"))
    }


def generate_notebooks() -> list[tuple[str, str]]:
    """Write a notebook per calculator; return `(slug, title)` pairs."""
    out = BUILD / "notebooks"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    sources = _sources()
    pages = []
    for module, func in discover():
        slug = func.__name__
        if any(slug == s for s, _ in pages):
            sys.exit(f"Two calculators are both called '{slug}'; rename one.")
        notebook = NOTEBOOK.format(
            version=marimo.__version__,
            title=title(func),
            sources=sources,
            module=f"calcs.{module}",
            function=func.__name__,
        )
        (out / f"{slug}.py").write_text(notebook)
        pages.append((slug, title(func)))
    return pages


def export_site(pages: list[tuple[str, str]]) -> None:
    site = BUILD / "site"
    shutil.rmtree(site, ignore_errors=True)
    site.mkdir(parents=True)
    for slug, _ in pages:
        subprocess.run(
            [
                sys.executable, "-m", "marimo", "export", "html-wasm",
                str(BUILD / "notebooks" / f"{slug}.py"),
                "-o", str(site / slug), "--mode", "run", "--force",
            ],
            check=True,
        )
    items = "\n".join(
        f'<li><a href="{slug}/">{html.escape(name)}</a></li>' for slug, name in pages
    )
    (site / "index.html").write_text(INDEX.format(items=items))


def main() -> None:
    pages = generate_notebooks()
    print(f"Generated {len(pages)} calculator notebook(s) in {BUILD / 'notebooks'}")
    if "--no-export" not in sys.argv:
        export_site(pages)
        print(f"Site written to {BUILD / 'site'}")


if __name__ == "__main__":
    main()

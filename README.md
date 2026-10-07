# se-calc

Structural Engineering Calculators, published at <https://nedjwestern.github.io/se-calc/>.

## Adding or changing a calculator

**Engineers:** open a new issue using the *New or changed calculator* template and fill it in.
Claude will reply on the issue and open a pull request with the calculator and its tests.
Check the results against your worked example, then ask a reviewer to merge. Once it is
merged, the website updates automatically.

**Developers:** see [CLAUDE.md](CLAUDE.md) for the calculator conventions.

## How it works

```
calcs/          calculators as plain Python functions  <- the only code engineers see
tests/          pytest tests with reference values
se_calc/        framework: turns each function into a Marimo web page (WASM)
.github/        CI (prek: lint, secrets, tests), deploy to GitHub Pages, @claude integration
```

1. Each `@calculator` function in `calcs/` is discovered automatically.
2. `se_calc.build` generates a Marimo notebook per calculator (inputs from the function
   arguments, results table from the returned dict) and exports it to a static WASM page.
3. On every push to `main`, GitHub Actions runs the tests and, if they pass, publishes the site.

## Local development

- Install [uv](https://docs.astral.sh/uv/), then `uv sync`
- Run tests: `uv run pytest`
- Install the git hooks once: `uv run prek install`. Commits then run ruff, gitleaks,
  pytest and file checks (see `.pre-commit-config.yaml`). Run them all with `uv run prek run --all-files`.
- Build the site: `uv run python -m se_calc.build`, then
  `python -m http.server --directory build/site` and open http://localhost:8000

## One-off setup

- GitHub repo settings → Pages → Source: **GitHub Actions**.
- Install the Claude GitHub App (`/install-github-app` in Claude Code, or https://github.com/apps/claude)
  and add a `CLAUDE_CODE_OAUTH_TOKEN` repository secret (run `claude setup-token` to get one). Usage counts
  against that Claude subscription's limits.
- Engineers need write access to the repository to trigger @claude.
- Recommended: protect `main` so pull requests need the *Checks* workflow and one review.

"""Find every `@calculator` function in the `calcs` package."""

import importlib
import pkgutil

import calcs
from se_calc.spec import is_calculator


def discover() -> list:
    """Return `(module_name, function)` pairs, sorted by module then function name."""
    found = []
    for info in sorted(pkgutil.iter_modules(calcs.__path__), key=lambda i: i.name):
        module = importlib.import_module(f"calcs.{info.name}")
        for name, obj in sorted(vars(module).items()):
            if is_calculator(obj) and obj.__module__ == module.__name__:
                found.append((info.name, obj))
    return found

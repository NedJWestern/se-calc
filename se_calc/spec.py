"""The small vocabulary calculator authors use: `Input` and `@calculator`."""

import inspect
import typing
from dataclasses import dataclass


@dataclass(frozen=True)
class Input:
    """Describes how a calculator argument is shown to the user.

    Used inside `Annotated`, e.g. `depth: Annotated[float, Input("mm", min=100, max=300)] = 200`.
    Pass `options` to show a dropdown instead of a number box.
    """

    unit: str = "-"
    label: str | None = None
    min: float | None = None
    max: float | None = None
    step: float | None = None
    options: tuple | None = None


@dataclass(frozen=True)
class Param:
    name: str
    default: object
    spec: Input

    @property
    def label(self) -> str:
        return self.spec.label or self.name.replace("_", " ").capitalize()


def calculator(title: str, outputs: dict[str, str]):
    """Mark a function as a published calculator.

    `outputs` maps each key of the returned dict to its unit, in display order.
    """

    def decorate(func):
        func.__calculator__ = {"title": title, "outputs": dict(outputs)}
        return func

    return decorate


def is_calculator(obj) -> bool:
    return callable(obj) and hasattr(obj, "__calculator__")


def title(func) -> str:
    return func.__calculator__["title"]


def output_units(func) -> dict[str, str]:
    return func.__calculator__["outputs"]


def params(func) -> list[Param]:
    """Arguments of a calculator with their `Input` metadata."""
    hints = typing.get_type_hints(func, include_extras=True)
    result = []
    for name, p in inspect.signature(func).parameters.items():
        spec = next(
            (m for m in getattr(hints.get(name), "__metadata__", ()) if isinstance(m, Input)),
            None,
        )
        if spec is None:
            raise TypeError(f"{func.__name__}: argument '{name}' needs Annotated[..., Input(...)]")
        if p.default is inspect.Parameter.empty:
            raise TypeError(f"{func.__name__}: argument '{name}' needs a default value")
        result.append(Param(name, p.default, spec))
    return result

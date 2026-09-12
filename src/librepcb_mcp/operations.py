"""Cooperative operation deadlines and cancellation, independent of transport."""

from collections.abc import Callable
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
import math
import time

from librepcb_mcp.errors import ProjectError


@dataclass(frozen=True)
class OperationBudget:
    deadline: float
    cancel_check: Callable[[], None] | None = None

    def check(self) -> None:
        if self.cancel_check is not None:
            self.cancel_check()
        if time.monotonic() >= self.deadline:
            raise ProjectError("operation_timeout", "The whole operation exceeded its time budget. Partial copies and diagnostics are retained.")


_active: ContextVar[OperationBudget | None] = ContextVar("librepcb_operation", default=None)


def validate_timeout(seconds: float) -> None:
    if not math.isfinite(seconds) or not 0 < seconds <= 600:
        raise ValueError("operation timeout must be finite and in (0, 600] seconds")


@contextmanager
def operation_scope(seconds: float, cancel_check: Callable[[], None] | None = None):
    validate_timeout(seconds)
    budget = OperationBudget(time.monotonic() + seconds, cancel_check)
    token = _active.set(budget)
    try:
        yield budget
    finally:
        _active.reset(token)


def checkpoint() -> None:
    budget = _active.get()
    if budget is not None:
        budget.check()

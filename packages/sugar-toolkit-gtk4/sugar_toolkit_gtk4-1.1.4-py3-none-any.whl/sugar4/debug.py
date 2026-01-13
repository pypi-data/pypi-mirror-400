"""Small helpers for gating debug output on ``SUGAR_DEBUG``."""

import builtins
import os
from typing import Any, Optional

_FALSEY_VALUES = {"0", "", "false", "off", "no"}
_BUILTIN_PRINT = builtins.print


def _raw_debug_value() -> Optional[str]:
    """Return the raw environment value for the debug flag."""

    value = os.environ.get("SUGAR_DEBUG")
    return value


def _to_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    return value.strip().lower() not in _FALSEY_VALUES


def is_debug_enabled() -> bool:
    """Evaluate the current state of the debug flag."""

    return _to_bool(_raw_debug_value())


def debug_print(*args: Any, **kwargs: Any) -> None:
    """Proxy to :func:`print` when debugging is active."""

    if is_debug_enabled():
        _BUILTIN_PRINT(*args, **kwargs)


__all__ = ["debug_print", "is_debug_enabled"]

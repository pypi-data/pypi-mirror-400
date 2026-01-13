import os
from typing import Final

BYTES_IN_MB: Final[int] = 1024 * 1024

DATA_DIR: Final[str] = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
MODELS_DIR: Final[str] = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))

MICROSECOND_THRESHOLD: Final[float] = 1e-6
MILLISECOND_THRESHOLD: Final[float] = 1e-3


def string_length_mb(text: str) -> float:
    return len(text.encode("utf-8")) / BYTES_IN_MB


def format_time(seconds: float) -> str:
    """Format time in appropriate units."""
    if seconds < MICROSECOND_THRESHOLD:
        return f"{seconds * 1e9:.2f}ns"
    elif seconds < MILLISECOND_THRESHOLD:
        return f"{seconds * 1e6:.2f}µs"
    elif seconds < 1:
        return f"{seconds * 1e3:.2f}ms"
    else:
        return f"{seconds:.2f}s"

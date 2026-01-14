from importlib.metadata import version

__version__ = version("k3httpmultipart")

from .multipart import (
    Multipart,
    InvalidArgumentTypeError,
    MultipartError,
)

__all__ = [
    "Multipart",
    "InvalidArgumentTypeError",
    "MultipartError",
]

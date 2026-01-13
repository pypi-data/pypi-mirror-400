"""Top-level package for init_python_package."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("init_python_package")
except PackageNotFoundError:
    __version__ = "0.0.0"  # fallback for local dev

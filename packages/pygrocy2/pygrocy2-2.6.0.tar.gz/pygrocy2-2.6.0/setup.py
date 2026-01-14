"""Legacy setuptools fallback.

The project uses pyproject.toml for metadata and builds.
"""

from setuptools import setup


if __name__ == "__main__":  # pragma: no cover - compatibility shim only
    setup()

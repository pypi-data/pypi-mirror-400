"""Truthound Dashboard - Open-source data quality dashboard.

A GX Cloud alternative that provides:
- Data source management
- Automated schema learning
- Data validation and profiling
- Real-time monitoring dashboard
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("truthound-dashboard")
except PackageNotFoundError:
    # Package not installed (e.g., running from source without pip install -e)
    __version__ = "0.0.0.dev"

__all__ = ["__version__"]

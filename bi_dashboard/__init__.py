"""
BI Platform Dashboard

An interactive dashboard for data visualization and business intelligence.
"""

from .app import app, run_server
from .components.dashboard import Dashboard
from .core.data_connector import DataSourceManager
from .core.viz_engine import ChartBuilder
from .core.interactivity import InteractivityManager

__version__ = "0.1.0"
__all__ = [
    "app",
    "run_server",
    "Dashboard",
    "DataSourceManager",
    "ChartBuilder",
    "InteractivityManager",
]


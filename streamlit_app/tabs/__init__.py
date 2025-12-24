"""
Tab Modules Package
==================

Individual tab implementations for the LSL Stream Receiver application.
"""

from .dashboard import display_dashboard_tab
from .streams import display_streams_tab
from .graphs import display_graphs_tab
from .data import display_data_tab
from .settings import display_settings_tab

__all__ = [
    'display_dashboard_tab',
    'display_streams_tab',
    'display_graphs_tab',
    'display_data_tab',
    'display_settings_tab'
]

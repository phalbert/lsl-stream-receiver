"""
State Manager Module
===================

Session state management and initialization utilities.
"""

import streamlit as st
import time
from datetime import datetime


def initialize_session_state(st_module):
    """Initialize all session state variables."""

    # Core application state
    if 'manager' not in st.session_state:
        st.session_state.manager = None
    if 'logger' not in st.session_state:
        st.session_state.logger = None
    if 'assessor' not in st.session_state:
        st.session_state.assessor = None
    if 'status_history' not in st.session_state:
        st.session_state.status_history = []

    # Real-time data management
    if 'auto_refresh' not in st.session_state:
        st.session_state.auto_refresh = True
    if 'refresh_interval' not in st.session_state:
        st.session_state.refresh_interval = 2  # seconds
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    if 'realtime_data' not in st.session_state:
        st.session_state.realtime_data = {}
    if 'data_cache' not in st.session_state:
        st.session_state.data_cache = {}
    if 'last_data_update' not in st.session_state:
        st.session_state.last_data_update = 0

    # UI state
    if 'current_time' not in st.session_state:
        st.session_state.current_time = time.time()


def get_session_state():
    """Get current session state with defaults."""
    return {
        'manager': st.session_state.get('manager'),
        'logger': st.session_state.get('logger'),
        'assessor': st.session_state.get('assessor'),
        'auto_refresh': st.session_state.get('auto_refresh', True),
        'refresh_interval': st.session_state.get('refresh_interval', 2),
        'realtime_data': st.session_state.get('realtime_data', {}),
        'last_refresh': st.session_state.get('last_refresh', time.time()),
        'last_data_update': st.session_state.get('last_data_update', 0),
    }

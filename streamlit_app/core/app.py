"""
Core Application Module
======================

Main application logic and session management for the LSL Stream Receiver.
"""

import streamlit as st
import time
from datetime import datetime
from pathlib import Path
import json

from ..tabs.dashboard import display_dashboard_tab
from ..tabs.streams import display_streams_tab
from ..tabs.graphs import display_graphs_tab
from ..tabs.data import display_data_tab
from ..tabs.settings import display_settings_tab
from ..utils.state_manager import initialize_session_state
from ..utils.data_manager import update_realtime_data, export_all_data
from ..utils.stream_manager import start_recording_process, stop_recording_process


def render_main_interface(session_name: str, output_dir: str):
    """Render the main application interface with modular tabs."""

    # Global refresh controls
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🔄 Manual Refresh", type="primary", use_container_width=True):
            update_realtime_data()
            st.success("✅ Data refreshed!")
            st.rerun()

    # Main content area with modular tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", "📡 Streams", "📈 Graphs", "📋 Data", "⚙️ Settings"
    ])

    with tab1:
        display_dashboard_tab(session_name, output_dir)

    with tab2:
        display_streams_tab()

    with tab3:
        display_graphs_tab()

    with tab4:
        display_data_tab()

    with tab5:
        display_settings_tab()


def render_sidebar_controls():
    """Render the sidebar with configuration controls."""

    with st.sidebar:
        st.header("⚙️ Configuration")

        # Session settings
        session_name = st.text_input(
            "Session Name",
            value=f"lab_session_{datetime.now().strftime('%Y%m%d_%H%M')}",
            help="Name for this recording session"
        )

        output_dir = st.text_input(
            "Output Directory",
            value="lsl_data",
            help="Directory to save recorded data"
        )

        # Stream discovery options
        st.subheader("Stream Discovery")
        auto_discovery = st.checkbox("Auto-discover streams", value=True)
        target_streams = st.text_area(
            "Target Streams (one per line, leave empty for all)",
            height=100,
            help="Specific stream names to connect to. Leave empty to connect to all available streams."
        )

        target_streams_list = [s.strip() for s in target_streams.split('\n') if s.strip()] if target_streams else None

        # Recording settings
        st.subheader("Recording Settings")
        formats = st.multiselect(
            "Output Formats",
            ["csv", "json", "parquet"],
            default=["csv", "json"],
            help="File formats for data logging"
        )

        buffer_size = st.slider("Buffer Size (samples)", 100, 5000, 1000, 100)
        save_interval = st.slider("Save Interval (seconds)", 5, 300, 30, 5)

        # Quality monitoring
        st.subheader("Quality Monitoring")
        enable_quality = st.checkbox("Enable quality monitoring", value=True)
        quality_interval = st.slider("Quality check interval (seconds)", 10, 300, 30, 10)

        # Real-time settings
        st.subheader("Real-time Display")
        st.session_state.auto_refresh = st.checkbox("Auto-refresh dashboard", value=True)
        st.session_state.refresh_interval = st.slider("Refresh interval (seconds)", 0.5, 10.0, 2.0, 0.5)
        st.slider("Max plot points", 100, 2000, 500, 50)  # For future use

        # Quick performance info
        if st.session_state.manager and st.session_state.manager.running:
            total_samples = sum(len(samples) for samples in st.session_state.realtime_data.values())
            st.caption(f"📊 Buffered: {total_samples:,} samples | 📈 See Graphs tab for detailed metrics")

        # Enhanced signal quality indicators
        if st.session_state.manager and st.session_state.manager.running:
            with st.expander("🔍 Signal Quality Overview"):
                stream_info = st.session_state.manager.get_stream_info()

                quality_cols = st.columns(len(stream_info))
                for i, (stream_name, info) in enumerate(stream_info.items()):
                    with quality_cols[i]:
                        # Calculate quality metrics
                        if info.get('samples_received', 0) > 0:
                            time_since_last = time.time() - info.get('last_sample_time', time.time())
                            quality_color = "🟢" if time_since_last < 2 else "🟡" if time_since_last < 5 else "🔴"
                            st.metric(f"{stream_name[:10]}", f"{quality_color} {time_since_last:.1f}s")
                        else:
                            st.metric(f"{stream_name[:10]}", "⚪ No Data")

        # Control buttons
        st.subheader("Control")
        col1, col2 = st.columns(2)

        with col1:
            start_button = st.button(
                "▶️ Start Recording",
                type="primary",
                use_container_width=True,
                disabled=st.session_state.manager is not None
            )

        with col2:
            stop_button = st.button(
                "⏹️ Stop Recording",
                type="secondary",
                use_container_width=True,
                disabled=st.session_state.manager is None
            )

    return {
        'session_name': session_name,
        'output_dir': output_dir,
        'auto_discovery': auto_discovery,
        'target_streams': target_streams_list,
        'formats': formats,
        'buffer_size': buffer_size,
        'save_interval': save_interval,
        'enable_quality': enable_quality,
        'quality_interval': quality_interval,
        'start_button': start_button,
        'stop_button': stop_button
    }

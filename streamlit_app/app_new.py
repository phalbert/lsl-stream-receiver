"""
LSL Stream Receiver - Streamlit Interface (Refactored)
======================================================

Modular architecture for real-time LSL stream acquisition and visualization.
This is the main entry point that orchestrates all components.
"""

import streamlit as st
import time
import numpy as np
from datetime import datetime
from lsl_receiver import StreamManager, QualityAssessor
from lsl_receiver.data_logger import create_multi_format_logger

# Import modular components
from .core.app import render_main_interface, render_sidebar_controls
from .utils.state_manager import initialize_session_state
from .utils.data_manager import update_realtime_data

# Page configuration
st.set_page_config(
    page_title="LSL Stream Receiver",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
/* Main container padding */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Compact header */
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 1rem;
}

/* Stream health indicators */
.stream-healthy { color: #28a745; font-weight: bold; }
.stream-warning { color: #ffc107; font-weight: bold; }
.stream-error { color: #dc3545; font-weight: bold; }

/* Enhanced status cards */
.status-card {
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
    border-left: 4px solid;
    transition: all 0.3s ease;
}

.status-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

/* Real-time indicator */
.realtime-indicator {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 0.5rem;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

/* Plot containers */
.plot-container {
    margin: 1rem 0;
    padding: 1rem;
    background-color: #ffffff;
    border-radius: 0.5rem;
    border: 1px solid #dee2e6;
}
</style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point with modular architecture."""

    # Header
    st.markdown('<h1 class="main-header">📡 LSL Stream Receiver</h1>', unsafe_allow_html=True)
    st.markdown("**Multi-stream data acquisition and monitoring system**")

    # Initialize session state FIRST
    initialize_session_state(st)

    # Auto-refresh logic with performance optimization
    current_time = time.time()
    if (st.session_state.auto_refresh and
        current_time - st.session_state.last_refresh > st.session_state.refresh_interval):

        # Update data in background
        update_realtime_data()
        st.session_state.last_refresh = current_time

        # Only rerun if data actually changed or if it's been a while
        if (st.session_state.realtime_data and
            (current_time - st.session_state.last_data_update < st.session_state.refresh_interval * 2)):
            st.rerun()

    # Get sidebar controls
    sidebar_config = render_sidebar_controls()

    # Handle start/stop actions
    if sidebar_config['start_button']:
        success = start_recording(
            sidebar_config['session_name'],
            sidebar_config['output_dir'],
            sidebar_config['formats'],
            sidebar_config['buffer_size'],
            sidebar_config['save_interval'],
            sidebar_config['auto_discovery'],
            sidebar_config['target_streams'],
            sidebar_config['enable_quality'],
            sidebar_config['quality_interval']
        )
        if success:
            st.balloons()

    if sidebar_config['stop_button']:
        stop_recording()

    # Render main interface
    render_main_interface(sidebar_config['session_name'], sidebar_config['output_dir'])


def start_recording(session_name: str, output_dir: str, formats: list,
                   buffer_size: int, save_interval: int, auto_discovery: bool,
                   target_streams: list, enable_quality: bool, quality_interval: int):
    """Start the recording process with enhanced error recovery."""

    try:
        # Validate inputs
        if not session_name.strip():
            st.error("❌ Session name cannot be empty")
            return False

        if not output_dir.strip():
            st.error("❌ Output directory cannot be empty")
            return False

        # Create output directory if it doesn't exist
        from pathlib import Path
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Check if we can write to the directory
        try:
            test_file = output_path / ".write_test"
            test_file.touch()
            test_file.unlink()
        except Exception:
            st.error(f"❌ Cannot write to output directory: {output_dir}")
            return False

        # Clean up any existing connections first
        if st.session_state.manager:
            st.session_state.manager.stop_receiving()

        # Create data logger
        logger = create_multi_format_logger(
            output_dir=output_dir,
            session_name=session_name
        )

        # Create quality assessor
        assessor = QualityAssessor(check_interval=quality_interval) if enable_quality else None

        # Create stream manager with enhanced settings
        manager = StreamManager(
            target_streams=target_streams,
            auto_discovery=auto_discovery
        )

        # Start recording with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            st.info(f"🔄 Starting recording (attempt {attempt + 1}/{max_retries})...")
            success = manager.start_receiving(data_logger=logger, quality_assessor=assessor)

            if success:
                break

            if attempt < max_retries - 1:
                st.warning(f"⚠️ Attempt {attempt + 1} failed, retrying...")
                time.sleep(1)

        if success:
            st.session_state.manager = manager
            st.session_state.logger = logger
            st.session_state.assessor = assessor

            # Initialize data structures
            st.session_state.realtime_data = {}
            st.session_state.data_cache = {}
            st.session_state.last_data_update = time.time()

            st.success(f"🎉 Recording started! Session: {session_name}")
            return True
        else:
            st.error("❌ Failed to start recording after multiple attempts. Check stream connections.")
            return False

    except Exception as e:
        st.error(f"❌ Error starting recording: {e}")
        # Clean up on failure
        if 'manager' in st.session_state and st.session_state.manager:
            st.session_state.manager.stop_receiving()
        return False


def stop_recording():
    """Stop the recording process."""

    try:
        if st.session_state.manager:
            st.session_state.manager.stop_receiving()

        if st.session_state.logger:
            st.session_state.logger.save_session_summary()
            st.session_state.logger.close()

        # Clear session state
        st.session_state.manager = None
        st.session_state.logger = None
        st.session_state.assessor = None
        st.session_state.realtime_data = {}

        st.success("🛑 Recording stopped and data saved!")
        return True

    except Exception as e:
        st.error(f"❌ Error stopping recording: {e}")
        return False


if __name__ == "__main__":
    main()

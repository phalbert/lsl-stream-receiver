"""
Stream Manager Module
====================

Stream connection, management, and recording utilities.
"""

import streamlit as st
import time
from pathlib import Path
from lsl_receiver import StreamManager, QualityAssessor
from lsl_receiver.data_logger import create_multi_format_logger


def start_recording_process(session_name: str, output_dir: str, formats: list,
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


def stop_recording_process():
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

        return True

    except Exception as e:
        st.error(f"❌ Error stopping recording: {e}")
        return False


def get_stream_status_summary():
    """Get comprehensive stream status summary."""
    if not st.session_state.manager:
        return {
            'running': False,
            'connected_streams': 0,
            'total_samples_received': 0,
            'stream_info': {},
            'latest_data_count': {}
        }

    return st.session_state.manager.get_status_summary()


def get_stream_info(stream_name=None):
    """Get information about connected streams."""
    if not st.session_state.manager:
        return {} if stream_name is None else {}

    return st.session_state.manager.get_stream_info(stream_name)

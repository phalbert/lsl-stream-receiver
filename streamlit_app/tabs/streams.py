"""
Streams Tab Module
==================

Stream management and detailed stream information.
"""

import streamlit as st
import pandas as pd
import time
from ..utils.stream_manager import get_stream_info


def display_streams_tab():
    """Display stream information and controls."""

    st.header("Stream Management")

    if st.session_state.manager is None:
        st.info("Start recording to see stream information")
        return

    # Stream details
    stream_info = get_stream_info()

    for stream_name, info in stream_info.items():
        with st.expander(f"🔍 {stream_name} Details"):
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Stream Information:**")
                st.write(f"- Name: {info.get('name', 'Unknown')}")
                st.write(f"- Type: {info.get('stream_type', 'Unknown')}")
                st.write(f"- Sampling Rate: {info.get('sampling_rate', 'Unknown')} Hz")
                st.write(f"- Channels: {info.get('channels', 'Unknown')}")

            with col2:
                st.write("**Connection Status:**")
                st.write(f"- Connected: {'✅ Yes' if info.get('connected') else '❌ No'}")
                st.write(f"- Samples Received: {info.get('samples_received', 0):,}")
                st.write(f"- Connection Errors: {info.get('connection_errors', 0)}")
                if info.get('last_sample_time'):
                    time_since = st.session_state.get('current_time', time.time()) - info['last_sample_time']
                    st.write(f"- Last Sample: {time_since:.1f}s ago")

            # Latest samples for this stream
            latest_samples = st.session_state.manager.get_latest_data(stream_name, n_samples=20)
            if latest_samples[stream_name]:
                st.write("**Recent Samples:**")
                samples_df = pd.DataFrame(latest_samples[stream_name])
                st.dataframe(samples_df, use_container_width=True)

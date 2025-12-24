"""
Settings Tab Module
===================

Current settings, configuration, and manual controls.
"""

import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from datetime import datetime


def display_settings_tab():
    """Display current settings and configuration."""

    st.header("Settings & Configuration")

    if st.session_state.manager is None:
        st.info("Start recording to see current configuration")
        return

    # Current settings
    with st.expander("📋 Current Configuration"):
        st.write("**Session:**")
        if st.session_state.logger:
            st.write(f"- Session Name: {st.session_state.logger.session_name}")
            st.write(f"- Output Directory: {st.session_state.logger.output_dir}")

        st.write("**Streams:**")
        stream_info = st.session_state.manager.get_stream_info()
        for name, info in stream_info.items():
            st.write(f"- {name}: {info.get('stream_type', 'Unknown')} ({info.get('sampling_rate', 'Unknown')} Hz)")

    # Performance metrics
    with st.expander("⚡ Performance Metrics"):
        if st.session_state.status_history:
            # Create performance chart
            history_df = pd.DataFrame(st.session_state.status_history[-100:])  # Last 100 records

            if not history_df.empty:
                fig = go.Figure()

                if 'samples_received' in history_df.columns:
                    fig.add_trace(go.Scatter(
                        x=history_df.index,
                        y=history_df['samples_received'],
                        mode='lines',
                        name='Samples Received'
                    ))

                fig.update_layout(
                    title="Performance Over Time",
                    xaxis_title="Time",
                    yaxis_title="Samples",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)

    # Manual controls
    with st.expander("🔧 Manual Controls"):
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Refresh Stream Status", use_container_width=True):
                st.rerun()

        with col2:
            if st.button("💾 Save Status Report", use_container_width=True):
                status = st.session_state.manager.get_status_summary()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_file = f"status_report_{timestamp}.json"

                with open(report_file, 'w') as f:
                    json.dump(status, f, indent=2, default=str)

                st.success(f"Status report saved to: {report_file}")

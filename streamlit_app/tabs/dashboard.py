"""
Dashboard Tab Module
===================

Main dashboard display with status, metrics, and overview information.
"""

import streamlit as st
import time
from datetime import datetime
from ..utils.stream_manager import get_stream_status_summary


def display_dashboard_tab(session_name: str, output_dir: str):
    """Display main dashboard with status and metrics."""

    st.header("Dashboard")

    if st.session_state.manager is None:
        st.info("👈 Configure settings in the sidebar and click 'Start Recording' to begin")
        return

    # Status summary
    status = get_stream_status_summary()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        status_icon = "🟢" if status['running'] else "🔴"
        st.metric(
            "Status",
            f"{status_icon} Running" if status['running'] else "🔴 Stopped",
            delta=None
        )

    with col2:
        st.metric(
            "Connected Streams",
            status['connected_streams'],
            delta=None
        )

    with col3:
        st.metric(
            "Total Samples",
            f"{status['total_samples_received']:,}",
            delta=None
        )

    with col4:
        latest_data_count = sum(status['latest_data_count'].values())
        st.metric(
            "Buffered Samples",
            f"{latest_data_count:,}",
            delta=None
        )

    # Real-time refresh indicator
    if st.session_state.auto_refresh:
        st.success(f"🔄 Auto-refresh: ON ({st.session_state.refresh_interval}s interval)")
    else:
        st.warning("⏸️ Auto-refresh: OFF")

    # Quick preview of available data
    if st.session_state.realtime_data:
        st.info("📈 **Real-time graphs available!** → Check the '📈 Graphs' tab for detailed visualizations")
    else:
        st.info("📊 No real-time data available yet. Data will appear once streams start sending data.")

    # Stream quality overview
    if st.session_state.assessor:
        st.subheader("🎯 Stream Quality Overview")
        stream_info = status['stream_info']

        quality_cols = st.columns(len(stream_info))
        for i, (stream_name, info) in enumerate(stream_info.items()):
            with quality_cols[i]:
                quality_score = "Good" if info['connected'] else "Disconnected"
                quality_color = "🟢" if info['connected'] else "🔴"
                st.metric(f"{stream_name}", f"{quality_color} {quality_score}")

    # Enhanced Stream Status with Health Monitoring
    st.subheader("🔍 Stream Health Monitor")

    stream_info = status['stream_info']

    # Real-time health indicators
    cols = st.columns(len(stream_info))

    for i, (stream_name, info) in enumerate(stream_info.items()):
        with cols[i]:
            # Calculate health metrics
            time_since_last = time.time() - info.get('last_sample_time', time.time())
            samples_received = info.get('samples_received', 0)
            connection_errors = info.get('connection_errors', 0)

            # Determine health status
            if not info.get('connected', False):
                health_status = "Disconnected"
                health_class = "stream-error"
                health_icon = "🔴"
            elif connection_errors > 5:
                health_status = "Error"
                health_class = "stream-error"
                health_icon = "🔴"
            elif time_since_last > 5:
                health_status = "Stale"
                health_class = "stream-warning"
                health_icon = "🟡"
            elif samples_received == 0:
                health_status = "No Data"
                health_class = "stream-warning"
                health_icon = "🟡"
            else:
                health_status = "Healthy"
                health_class = "stream-healthy"
                health_icon = "🟢"

            # Enhanced status card with hover effects
            st.markdown(f"""
            <div class="status-card" style="border-left-color: {health_icon == '🟢' and '#28a745' or health_icon == '🟡' and '#ffc107' or '#dc3545'}">
                <h4>{health_icon} <span class="{health_class}">{stream_name}</span></h4>
                <p><strong>Status:</strong> {health_status}</p>
                <p><strong>Samples:</strong> {samples_received:,}</p>
                <p><strong>Errors:</strong> {connection_errors}</p>
                <p><strong>Last Update:</strong> {time_since_last:.1f}s ago</p>
            </div>
            """, unsafe_allow_html=True)

    # Recent activity
    st.subheader("Recent Activity")

    latest_data = st.session_state.manager.get_latest_data()
    if latest_data:
        for stream_name, samples in latest_data.items():
            if samples:
                latest_sample = samples[-1]
                values = latest_sample.get('values', [])

                with st.expander(f"📊 {stream_name} (Latest Sample)"):
                    st.write(f"**Timestamp:** {datetime.fromtimestamp(latest_sample['timestamp'])}")
                    st.write(f"**LSL Timestamp:** {latest_sample['lsl_timestamp']:.3f}")
                    st.write(f"**Values:** {[f'{v:.3f}' for v in values]}")

                    # Simple plot for recent values
                    if len(samples) >= 10:
                        timestamps = [s['timestamp'] for s in samples[-50:]]
                        channel_values = [s['values'][0] for s in samples[-50:] if len(s['values']) > 0]

                        if channel_values:
                            import plotly.graph_objects as go
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=timestamps,
                                y=channel_values,
                                mode='lines',
                                name=stream_name
                            ))
                            fig.update_layout(
                                title=f"{stream_name} - Recent Values",
                                xaxis_title="Time",
                                yaxis_title="Value",
                                height=200
                            )
                            st.plotly_chart(fig, use_container_width=True)

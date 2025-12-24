"""
LSL Stream Receiver - Streamlit Interface
========================================

Web interface for configuring and monitoring LSL stream reception.
"""

import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import json
import numpy as np
from scipy import signal

from lsl_receiver import StreamManager, QualityAssessor
from lsl_receiver.data_logger import create_multi_format_logger

# Page configuration
st.set_page_config(
    page_title="LSL Stream Receiver",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better layout
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}
.stream-status {
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}
.status-good { background-color: #d4edda; border-left: 5px solid #28a745; }
.status-warning { background-color: #fff3cd; border-left: 5px solid #ffc107; }
.status-critical { background-color: #f8d7da; border-left: 5px solid #dc3545; }
.status-disconnected { background-color: #f5f5f5; border-left: 5px solid #6c757d; }
.metric-card {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #dee2e6;
    margin: 0.5rem 0;
}
.plot-container {
    margin: 1rem 0;
    padding: 1rem;
    background-color: #ffffff;
    border-radius: 0.5rem;
    border: 1px solid #dee2e6;
}

/* Control buttons - ensure visibility */

/* Make buttons more prominent */
.streamlit-button {
    font-weight: bold !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
}

/* Ensure sidebar content doesn't get cut off */
.sidebar-content {
    max-height: none !important;
    overflow-y: visible !important;
}

/* Stream health indicators */
.stream-healthy {
    color: #28a745;
    font-weight: bold;
}
.stream-warning {
    color: #ffc107;
    font-weight: bold;
}
.stream-error {
    color: #dc3545;
    font-weight: bold;
}

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

/* Data export styles */
.export-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    margin: 1rem 0;
}

/* Performance metrics styling */
.performance-metric {
    background: #f8f9fa;
    padding: 0.5rem;
    border-radius: 0.25rem;
    margin: 0.25rem 0;
    border: 1px solid #e9ecef;
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
</style>
""", unsafe_allow_html=True)


def update_realtime_data():
    """Update real-time data for plotting with caching optimization and error recovery."""
    if not st.session_state.manager or not st.session_state.manager.running:
        return

    current_time = time.time()

    # Only update data if enough time has passed to avoid excessive updates
    if current_time - st.session_state.last_data_update < 0.5:  # Update every 0.5 seconds max
        return

    try:
        latest_data = st.session_state.manager.get_latest_data()

        if latest_data:
            # Use caching to avoid unnecessary re-renders
            data_changed = False

            for stream_name, samples in latest_data.items():
                if stream_name not in st.session_state.data_cache:
                    st.session_state.data_cache[stream_name] = []
                    data_changed = True

                if samples != st.session_state.data_cache[stream_name]:
                    st.session_state.data_cache[stream_name] = samples.copy()
                    data_changed = True

            if data_changed:
                st.session_state.realtime_data = latest_data.copy()
                st.session_state.last_data_update = current_time

    except Exception as e:
        # Error recovery - log but don't crash
        st.error(f"⚠️ Data update error: {e}")
        # Attempt to reconnect streams if there are persistent errors
        if "connection" in str(e).lower() or "timeout" in str(e).lower():
            st.warning("🔄 Attempting to reconnect streams...")
            try:
                if st.session_state.manager:
                    # Force stream rediscovery and reconnection
                    stream_infos = st.session_state.manager.discover_streams()
                    if stream_infos:
                        st.session_state.manager.connect_to_streams(stream_infos)
                        st.success("✅ Streams reconnected successfully")
                    else:
                        st.error("❌ No streams available for reconnection")
            except Exception as reconnect_error:
                st.error(f"❌ Reconnection failed: {reconnect_error}")


def main():
    # Header
    st.markdown('<h1 class="main-header">📡 LSL Stream Receiver</h1>', unsafe_allow_html=True)
    st.markdown("**Multi-stream data acquisition and monitoring system**")

    # Initialize session state FIRST
    if 'manager' not in st.session_state:
        st.session_state.manager = None
    if 'logger' not in st.session_state:
        st.session_state.logger = None
    if 'assessor' not in st.session_state:
        st.session_state.assessor = None
    if 'status_history' not in st.session_state:
        st.session_state.status_history = []
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
    if 'start_button_clicked' not in st.session_state:
        st.session_state.start_button_clicked = False
    if 'stop_button_clicked' not in st.session_state:
        st.session_state.stop_button_clicked = False

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
            # Use a more efficient rerun approach
            st.rerun()

    # Sidebar configuration - Simplified for better visibility
    with st.sidebar:
        st.header("⚙️ Configuration")

        # === ESSENTIAL CONTROLS FIRST ===
        st.subheader("🎮 Recording Controls")
        st.markdown("---")

        # Control buttons - Always visible at the top

        # === SESSION SETTINGS ===
        st.subheader("📝 Session Settings")
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

        # === STREAM SETTINGS ===
        st.subheader("📡 Stream Discovery")
        auto_discovery = st.checkbox("Auto-discover streams", value=True)
        target_streams = st.text_area(
            "Target Streams (one per line, leave empty for all)",
            height=80,  # Shorter
            help="Specific stream names to connect to"
        )
        target_streams_list = [s.strip() for s in target_streams.split('\n') if s.strip()] if target_streams else None

        # === RECORDING SETTINGS ===
        st.subheader("⚙️ Recording Settings")
        formats = st.multiselect(
            "Output Formats",
            ["csv", "json", "parquet"],
            default=["csv", "json"],
            help="File formats for data logging"
        )

        buffer_size = st.slider("Buffer Size (samples)", 100, 5000, 1000, 100)
        save_interval = st.slider("Save Interval (seconds)", 5, 300, 30, 5)

        # === QUALITY MONITORING ===
        st.subheader("🔍 Quality Monitoring")
        enable_quality = st.checkbox("Enable quality monitoring", value=True)
        quality_interval = st.slider("Quality check interval (seconds)", 10, 300, 30, 10)

        # === REAL-TIME SETTINGS ===
        st.subheader("🔄 Real-time Display")
        st.session_state.auto_refresh = st.checkbox("Auto-refresh dashboard", value=True)
        st.session_state.refresh_interval = st.slider("Refresh interval (seconds)", 0.5, 10.0, 2.0, 0.5)

        # Performance info (collapsible)
        with st.expander("📊 Performance Info"):
            if st.session_state.manager and st.session_state.manager.running:
                total_samples = sum(len(samples) for samples in st.session_state.realtime_data.values())
                st.caption(f"Buffered: {total_samples:,} samples")

                stream_info = st.session_state.manager.get_stream_info()
                for stream_name, info in stream_info.items():
                    time_since_last = time.time() - info.get('last_sample_time', time.time())
                    st.caption(f"{stream_name}: {time_since_last:.1f}s ago")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Start Recording")
            start_clicked = st.button(
                "▶️ START RECORDING",
                type="primary",
                use_container_width=True,
                disabled=st.session_state.manager is not None,
                help="Begin recording LSL streams"
            )
            # Store button state in session state for access outside sidebar
            if start_clicked:
                st.session_state.start_button_clicked = True
                st.success("🎬 Recording started!")

        with col2:
            st.markdown("### Stop Recording")
            stop_clicked = st.button(
                "⏹️ STOP RECORDING",
                type="secondary",
                use_container_width=True,
                disabled=st.session_state.manager is None,
                help="Stop recording and save data"
            )
            # Store button state in session state for access outside sidebar
            if stop_clicked:
                st.session_state.stop_button_clicked = True
                st.success("⏹️ Recording stopped!")

        # Status indicator
        if st.session_state.manager:
            st.success("🔴 **RECORDING ACTIVE** - Check Dashboard tab for real-time data")
        else:
            st.info("⚪ **READY** - Configure settings and click Start Recording")

        # Close the styled container
        st.markdown('</div>', unsafe_allow_html=True)

    # Global refresh controls
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🔄 Manual Refresh", type="primary", use_container_width=True):
            update_realtime_data()
            st.success("✅ Data refreshed!")
            st.rerun()

    # Main content area
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "📡 Streams", "📈 Graphs", "📋 Data", "⚙️ Settings"])

    with tab1:
        display_dashboard(session_name, output_dir)

    with tab2:
        display_streams_tab()

    with tab3:
        display_graphs_tab()

    with tab4:
        display_data_tab()

    with tab5:
        display_settings_tab()

    # Handle start/stop actions using session state
    if st.session_state.get('start_button_clicked', False):
        start_recording(
            session_name, output_dir, formats, buffer_size, save_interval,
            auto_discovery, target_streams_list, enable_quality, quality_interval
        )
        st.session_state.start_button_clicked = False  # Reset the flag

    if st.session_state.get('stop_button_clicked', False):
        stop_recording()
        st.session_state.stop_button_clicked = False  # Reset the flag


def display_dashboard(session_name: str, output_dir: str):
    """Display main dashboard with status and metrics."""
    st.header("Dashboard")

    if st.session_state.manager is None:
        st.info("👈 Configure settings in the sidebar and click 'Start Recording' to begin")
        return

    # Status summary
    status = st.session_state.manager.get_status_summary()

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


def display_streams_tab():
    """Display stream information and controls."""
    st.header("Stream Management")

    if st.session_state.manager is None:
        st.info("Start recording to see stream information")
        return

    # Stream details
    stream_info = st.session_state.manager.get_stream_info()

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
                    time_since = time.time() - info['last_sample_time']
                    st.write(f"- Last Sample: {time_since:.1f}s ago")

            # Latest samples for this stream
            latest_samples = st.session_state.manager.get_latest_data(stream_name, n_samples=20)
            if latest_samples[stream_name]:
                st.write("**Recent Samples:**")
                samples_df = pd.DataFrame(latest_samples[stream_name])
                st.dataframe(samples_df, use_container_width=True)


def display_data_tab():
    """Display data logging and quality information."""
    st.header("Data & Quality")

    if st.session_state.manager is None:
        st.info("Start recording to see data information")
        return

    # Data logger status
    if st.session_state.logger:
        st.subheader("Data Logging")

        # Session info
        session_dir = Path(st.session_state.logger.output_dir) / st.session_state.logger.session_name
        if session_dir.exists():
            st.success(f"📁 Session data: {session_dir}")

            # List files
            files = list(session_dir.glob("*"))
            if files:
                files_df = pd.DataFrame([
                    {
                        'File': f.name,
                        'Size (KB)': round(f.stat().st_size / 1024, 1),
                        'Modified': datetime.fromtimestamp(f.stat().st_mtime)
                    }
                    for f in files
                ])
                st.dataframe(files_df, use_container_width=True)

        # Quality assessor
        if st.session_state.assessor:
            st.subheader("Quality Assessment")

            # Trigger manual quality check
            if st.button("🔍 Run Quality Check"):
                stream_infos = st.session_state.manager.get_stream_info()
                quality_report = st.session_state.assessor.assess_quality(stream_infos)

                st.write("**Quality Report:**")
                st.json(quality_report)

                # Display quality scores
                if 'streams' in quality_report:
                    quality_data = []
                    for stream_name, stream_quality in quality_report['streams'].items():
                        quality_data.append({
                            'Stream': stream_name,
                            'Status': stream_quality.get('status', 'unknown').upper(),
                            'Score': f"{stream_quality.get('score', 0):.2f}",
                            'Issues': ', '.join(stream_quality.get('issues', []))
                        })

                    if quality_data:
                        quality_df = pd.DataFrame(quality_data)
                        st.dataframe(quality_df, use_container_width=True)

    # Download options
    st.subheader("Data Export")

    if st.session_state.logger and st.session_state.manager:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📊 Export Latest Data", use_container_width=True):
                latest_data = st.session_state.manager.get_latest_data()
                if latest_data:
                    # Convert to DataFrame
                    all_samples = []
                    for stream_name, samples in latest_data.items():
                        for sample in samples:
                            all_samples.append(sample)

                    if all_samples:
                        df = pd.DataFrame(all_samples)
                        csv_data = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv_data,
                            file_name=f"lsl_latest_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

        with col2:
            if st.button("📋 Export Status Report", use_container_width=True):
                status = st.session_state.manager.get_status_summary()
                status_json = json.dumps(status, indent=2, default=str)
                st.download_button(
                    label="📥 Download JSON",
                    data=status_json,
                    file_name=f"lsl_status_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )


def display_graphs_tab():
    """Display real-time graphs and visualization."""
    st.header("📈 Real-time Graphs & Visualization")

    if st.session_state.manager is None:
        st.info("👈 Configure settings in the sidebar and click 'Start Recording' to see graphs")
        return

    # Real-time refresh indicator
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.session_state.auto_refresh:
            st.success(f"🔄 Auto-refresh: ON ({st.session_state.refresh_interval}s interval)")
        else:
            st.warning("⏸️ Auto-refresh: OFF")

    with col2:
        st.info("💡 Use global refresh button above")

    # Real-time stream visualization
    if st.session_state.realtime_data:
        # Create tabs for different visualization modes
        vis_tab1, vis_tab2, vis_tab3, vis_tab4 = st.tabs(["📊 Line Charts", "📋 Multi-Channel", "🔄 Latest Values", "🌊 Spectrogram"])

        with vis_tab1:
            display_realtime_charts()

        with vis_tab2:
            display_multichannel_view()

        with vis_tab3:
            display_latest_values_table()

        with vis_tab4:
            display_spectrogram_analysis()
    else:
        st.info("📊 No real-time data available yet. Data will appear once streams start sending data.")

    # Performance metrics
    st.subheader("⚡ Performance Metrics")

    if st.session_state.manager and st.session_state.manager.running:
        col1, col2, col3 = st.columns(3)

        with col1:
            current_time = time.time()
            refresh_rate = 1.0 / max((current_time - st.session_state.last_refresh), 0.1)
            st.metric("Refresh Rate", f"{refresh_rate:.1f} Hz")

        with col2:
            total_samples = sum(len(samples) for samples in st.session_state.realtime_data.values())
            st.metric("Buffered Samples", f"{total_samples:,}")

        with col3:
            if st.session_state.last_data_update > 0:
                data_update_rate = 1.0 / max((current_time - st.session_state.last_data_update), 0.1)
                st.metric("Data Update Rate", f"{data_update_rate:.1f} Hz")

        # Graph controls
        st.subheader("📊 Graph Controls")

        col1, col2 = st.columns(2)
        with col1:
            st.slider("Max plot points", 100, 2000, 500, 50, key="graph_max_points")
        with col2:
            if st.button("📥 Export All Data", use_container_width=True):
                export_all_data()

        # Advanced streaming options
        with st.expander("⚙️ Advanced Options"):
            col1, col2 = st.columns(2)
            with col1:
                st.slider("Buffer size (samples)", 500, 5000, 1000, 100)
            with col2:
                st.slider("Update interval (ms)", 100, 2000, 500, 100)

    else:
        st.info("Start recording to see performance metrics")


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


def start_recording(session_name: str, output_dir: str, formats: list,
                   buffer_size: int, save_interval: int, auto_discovery: bool,
                   target_streams: list, enable_quality: bool, quality_interval: int):
    """Start the recording process with enhanced error recovery."""
    try:
        # Validate inputs
        if not session_name.strip():
            st.error("❌ Session name cannot be empty")
            return

        if not output_dir.strip():
            st.error("❌ Output directory cannot be empty")
            return

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
            return

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
            st.balloons()

            # Start status monitoring
            st.session_state.status_monitoring = True
        else:
            st.error("❌ Failed to start recording after multiple attempts. Check stream connections.")
            return

    except Exception as e:
        st.error(f"❌ Error starting recording: {e}")
        # Clean up on failure
        if 'manager' in st.session_state and st.session_state.manager:
            st.session_state.manager.stop_receiving()
        return

    # Force rerun to update UI
    st.rerun()


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

    except Exception as e:
        st.error(f"❌ Error stopping recording: {e}")


def display_realtime_charts():
    """Display real-time line charts for all streams."""
    if not st.session_state.realtime_data:
        st.info("No data available for plotting")
        return

    # Get the maximum number of plot points from session state (set in Graphs tab)
    max_points = st.session_state.get('graph_max_points', 500)

    for stream_name, samples in st.session_state.realtime_data.items():
        if not samples:
            continue

        st.subheader(f"📈 {stream_name}")

        # Extract data for plotting
        timestamps = [sample['timestamp'] for sample in samples[-max_points:]]
        values = [sample['values'][0] if len(sample['values']) > 0 else 0
                 for sample in samples[-max_points:]]

        if not timestamps or not values:
            st.warning(f"No valid data for {stream_name}")
            continue

        # Create the plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=values,
            mode='lines+markers',
            name=stream_name,
            line=dict(width=2),
            marker=dict(size=4)
        ))

        fig.update_layout(
            title=f"{stream_name} - Real-time Data",
            xaxis_title="Time",
            yaxis_title="Value",
            height=300,
            showlegend=True,
            xaxis=dict(
                tickformat='%H:%M:%S',
                tickangle=45
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        # Show statistics
        if values:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Current", f"{values[-1]:.3f}")
            with col2:
                st.metric("Mean", f"{np.mean(values):.3f}")
            with col3:
                st.metric("Min", f"{np.min(values):.3f}")
            with col4:
                st.metric("Max", f"{np.max(values):.3f}")


def display_multichannel_view():
    """Display multi-channel view for streams with multiple channels."""
    if not st.session_state.realtime_data:
        st.info("No data available for multi-channel view")
        return

    # Get the maximum number of plot points from session state
    max_points = st.session_state.get('graph_max_points', 500)

    for stream_name, samples in st.session_state.realtime_data.items():
        if not samples:
            continue

        st.subheader(f"📊 {stream_name} - Multi-Channel View")

        # Check if we have multi-channel data
        latest_sample = samples[-1] if samples else None
        if not latest_sample or len(latest_sample['values']) <= 1:
            st.info(f"{stream_name} appears to be single-channel")
            continue

        n_channels = len(latest_sample['values'])

        # Create subplots for each channel
        cols = min(3, n_channels)  # Max 3 columns
        rows = (n_channels + cols - 1) // cols

        for row in range(rows):
            row_cols = st.columns(cols)
            for col in range(cols):
                channel_idx = row * cols + col
                if channel_idx >= n_channels:
                    break

                with row_cols[col]:
                    # Extract data for this channel
                    channel_values = []
                    timestamps = []

                    for sample in samples[-max_points:]:  # Use configurable max points
                        if len(sample['values']) > channel_idx:
                            channel_values.append(sample['values'][channel_idx])
                            timestamps.append(sample['timestamp'])

                    if channel_values:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=timestamps,
                            y=channel_values,
                            mode='lines',
                            name=f'Channel {channel_idx + 1}',
                            line=dict(width=2)
                        ))

                        fig.update_layout(
                            title=f"Channel {channel_idx + 1}",
                            height=250,
                            margin=dict(l=20, r=20, t=40, b=20),
                            xaxis_title="Time" if row == rows - 1 else "",
                            yaxis_title="Value",
                            showlegend=False
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        # Channel stats
                        st.caption(f"Ch{channel_idx + 1}: {channel_values[-1]:.3f} "
                                 f"(μ={np.mean(channel_values):.3f}, "
                                 f"σ={np.std(channel_values):.3f})")


def display_latest_values_table():
    """Display latest values in a table format."""
    if not st.session_state.realtime_data:
        st.info("No data available")
        return

    st.subheader("🔄 Latest Values")

    all_latest_data = []

    for stream_name, samples in st.session_state.realtime_data.items():
        if samples:
            latest_sample = samples[-1]
            values = latest_sample['values']

            # Create a row for this stream
            row_data = {
                'Stream': stream_name,
                'Timestamp': datetime.fromtimestamp(latest_sample['timestamp']).strftime('%H:%M:%S.%f')[:-3],
                'LSL Time': f"{latest_sample['lsl_timestamp']:.3f}"
            }

            # Add channel values
            for i, value in enumerate(values):
                row_data[f'Ch{i+1}'] = f"{value:.4f}"

            all_latest_data.append(row_data)

    if all_latest_data:
        df = pd.DataFrame(all_latest_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Export button
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("📥 Export Latest Data", use_container_width=True):
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="💾 Download CSV",
                    data=csv_data,
                    file_name=f"lsl_latest_values_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    else:
        st.info("No recent data available")


def export_all_data():
    """Export all collected data in various formats."""
    if not st.session_state.realtime_data:
        st.warning("No data available for export")
        return

    try:
        # Create export data
        all_samples = []
        for stream_name, samples in st.session_state.realtime_data.items():
            for sample in samples:
                all_samples.append(sample)

        if not all_samples:
            st.warning("No samples available for export")
            return

        # Convert to DataFrame
        df = pd.DataFrame(all_samples)

        # Create export options
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📄 Export as CSV", use_container_width=True):
                csv_data = df.to_csv(index=False)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    label="💾 Download CSV",
                    data=csv_data,
                    file_name=f"lsl_export_{timestamp}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        with col2:
            if st.button("📊 Export as JSON", use_container_width=True):
                json_data = df.to_json(orient='records', indent=2)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                st.download_button(
                    label="💾 Download JSON",
                    data=json_data,
                    file_name=f"lsl_export_{timestamp}.json",
                    mime="application/json",
                    use_container_width=True
                )

        with col3:
            if st.button("📈 Export as Parquet", use_container_width=True):
                try:
                    import io
                    buffer = io.BytesIO()
                    df.to_parquet(buffer, index=False)
                    parquet_data = buffer.getvalue()
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        label="💾 Download Parquet",
                        data=parquet_data,
                        file_name=f"lsl_export_{timestamp}.parquet",
                        mime="application/octet-stream",
                        use_container_width=True
                    )
                except ImportError:
                    st.error("Parquet export requires pyarrow library")

        # Show data preview
        with st.expander("📊 Export Data Preview"):
            st.write(f"**Total Samples:** {len(df):,}")
            st.write(f"**Streams:** {', '.join(df['stream_name'].unique())}")
            st.write(f"**Time Range:** {df['timestamp'].min():.2f} to {df['timestamp'].max():.2f}")
            st.dataframe(df.head(10), use_container_width=True)

    except Exception as e:
        st.error(f"Export failed: {e}")


def display_spectrogram_analysis():
    """Display spectrogram analysis for frequency domain visualization."""
    if not st.session_state.realtime_data:
        st.info("No data available for spectrogram analysis")
        return

    st.subheader("🌊 Frequency Domain Analysis")

    # Controls for spectrogram
    col1, col2, col3 = st.columns(3)
    with col1:
        window_size = st.slider("FFT Window Size", 64, 1024, 256, 64)
    with col2:
        overlap = st.slider("Overlap", 0.1, 0.9, 0.5, 0.1)
    with col3:
        nperseg = st.slider("Window Length", 32, min(window_size, 512), 128, 32)

    # Get the maximum number of plot points from session state
    max_points = st.session_state.get('graph_max_points', 500)

    for stream_name, samples in st.session_state.realtime_data.items():
        if not samples or len(samples) < 100:
            st.warning(f"Need more data for {stream_name} spectrogram (at least 100 samples)")
            continue

        st.subheader(f"📊 {stream_name} - Spectrogram")

        # Extract data for spectrogram
        # For multi-channel streams, use the first channel for spectrogram
        channel_idx = 0
        channel_values = []

        for sample in samples[-max_points:]:  # Use configurable max points
            if len(sample['values']) > channel_idx:
                channel_values.append(sample['values'][channel_idx])

        if len(channel_values) < 100:
            st.warning(f"Insufficient data for spectrogram of {stream_name}")
            continue

        # Convert to numpy array
        data = np.array(channel_values)

        # Calculate spectrogram
        try:
            # Estimate sampling rate from data timing
            if len(samples) > 1:
                timestamps = [s['timestamp'] for s in samples[-max_points:]]
                time_diffs = np.diff(timestamps)
                avg_sample_time = np.mean(time_diffs)
                fs = 1.0 / avg_sample_time if avg_sample_time > 0 else 100  # Default 100 Hz
            else:
                fs = 100  # Default sampling rate

            # Create spectrogram
            frequencies, times, Sxx = signal.spectrogram(
                data,
                fs=fs,
                window='hann',
                nperseg=nperseg,
                noverlap=int(nperseg * overlap),
                nfft=window_size
            )

            # Convert to dB for better visualization
            Sxx_db = 10 * np.log10(Sxx + 1e-10)  # Add small value to avoid log(0)

            # Create the spectrogram plot
            fig = go.Figure(data=go.Heatmap(
                z=Sxx_db,
                x=times,
                y=frequencies,
                colorscale='Viridis',
                colorbar=dict(title="Power (dB)")
            ))

            fig.update_layout(
                title=f"{stream_name} - Spectrogram (Channel {channel_idx + 1})",
                xaxis_title="Time (s)",
                yaxis_title="Frequency (Hz)",
                height=400,
                yaxis=dict(autorange="reversed")  # Flip frequency axis
            )

            st.plotly_chart(fig, use_container_width=True)

            # Show frequency statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Frequency Range", f"{frequencies[0]:.1f} - {frequencies[-1]:.1f} Hz")
            with col2:
                dominant_freq_idx = np.unravel_index(np.argmax(Sxx_db), Sxx_db.shape)[0]
                st.metric("Peak Frequency", f"{frequencies[dominant_freq_idx]:.1f} Hz")
            with col3:
                st.metric("Time Window", f"{times[-1] - times[0]:.2f} s")
            with col4:
                st.metric("Max Power", f"{np.max(Sxx_db):.1f} dB")

        except Exception as e:
            st.error(f"Error creating spectrogram for {stream_name}: {e}")


if __name__ == "__main__":
    main()

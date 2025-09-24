"""
LSL Stream Receiver - Streamlit Interface
========================================

Web interface for configuring and monitoring LSL stream reception.
"""

import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import json

from lsl_receiver import StreamManager, DataLogger, QualityAssessor
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
</style>
""", unsafe_allow_html=True)


def main():
    # Header
    st.markdown('<h1 class="main-header">📡 LSL Stream Receiver</h1>', unsafe_allow_html=True)
    st.markdown("**Multi-stream data acquisition and monitoring system**")

    # Initialize session state
    if 'manager' not in st.session_state:
        st.session_state.manager = None
    if 'logger' not in st.session_state:
        st.session_state.logger = None
    if 'assessor' not in st.session_state:
        st.session_state.assessor = None
    if 'status_history' not in st.session_state:
        st.session_state.status_history = []

    # Sidebar configuration
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

    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📡 Streams", "📈 Data", "⚙️ Settings"])

    with tab1:
        display_dashboard(session_name, output_dir)

    with tab2:
        display_streams_tab()

    with tab3:
        display_data_tab()

    with tab4:
        display_settings_tab()

    # Handle start/stop actions
    if start_button:
        start_recording(
            session_name, output_dir, formats, buffer_size, save_interval,
            auto_discovery, target_streams_list, enable_quality, quality_interval
        )

    if stop_button:
        stop_recording()


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
        st.metric(
            "Status",
            "🟢 Running" if status['running'] else "🔴 Stopped",
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

    # Stream status cards
    st.subheader("Stream Status")

    stream_info = status['stream_info']

    for stream_name, info in stream_info.items():
        status_class = "status-good" if info['connected'] else "status-disconnected"
        status_icon = "🟢" if info['connected'] else "🔴"

        st.markdown(f"""
        <div class="stream-status {status_class}">
            <h4>{status_icon} {stream_name}</h4>
            <p><strong>Type:</strong> {info.get('stream_type', 'Unknown')}</p>
            <p><strong>Samples:</strong> {info.get('samples_received', 0):,}</p>
            <p><strong>Errors:</strong> {info.get('connection_errors', 0)}</p>
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
    """Start the recording process."""
    try:
        # Update buffer size in data logger
        # (This would need to be configurable in the DataLogger class)

        # Create data logger
        logger = create_multi_format_logger(
            output_dir=output_dir,
            session_name=session_name
        )

        # Create quality assessor
        assessor = QualityAssessor(check_interval=quality_interval) if enable_quality else None

        # Create stream manager
        manager = StreamManager(
            target_streams=target_streams,
            auto_discovery=auto_discovery
        )

        # Start recording
        success = manager.start_receiving(data_logger=logger, quality_assessor=assessor)

        if success:
            st.session_state.manager = manager
            st.session_state.logger = logger
            st.session_state.assessor = assessor

            st.success(f"🎉 Recording started! Session: {session_name}")
            st.balloons()

            # Start status monitoring
            st.session_state.status_monitoring = True
        else:
            st.error("❌ Failed to start recording. Check stream connections.")
            return

    except Exception as e:
        st.error(f"❌ Error starting recording: {e}")
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

        st.success("🛑 Recording stopped and data saved!")

    except Exception as e:
        st.error(f"❌ Error stopping recording: {e}")


if __name__ == "__main__":
    main()

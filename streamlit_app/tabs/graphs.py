"""
Graphs Tab Module
================

Real-time graphs and visualization components.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import time
from scipy import signal

from ..utils.data_manager import export_all_data
from ..utils.state_manager import get_session_state


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
        vis_tab1, vis_tab2, vis_tab3, vis_tab4 = st.tabs([
            "📊 Line Charts", "📋 Multi-Channel", "🔄 Latest Values", "🌊 Spectrogram"
        ])

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
            current_time = st.session_state.get('last_refresh', 0)
            if current_time > 0:
                refresh_rate = 1.0 / max((st.session_state.get('current_time', time.time()) - current_time), 0.1)
                st.metric("Refresh Rate", f"{refresh_rate:.1f} Hz")

        with col2:
            total_samples = sum(len(samples) for samples in st.session_state.realtime_data.values())
            st.metric("Buffered Samples", f"{total_samples:,}")

        with col3:
            if st.session_state.get('last_data_update', 0) > 0:
                data_update_rate = 1.0 / max((st.session_state.get('current_time', time.time()) - st.session_state.last_data_update), 0.1)
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


def display_realtime_charts():
    """Display real-time line charts for all streams."""
    if not st.session_state.realtime_data:
        st.info("No data available for plotting")
        return

    # Get the maximum number of plot points from session state
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

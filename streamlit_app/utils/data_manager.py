"""
Data Manager Module
==================

Data processing, export, and management utilities.
"""

import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime
import io


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


def get_stream_info():
    """Get information about connected streams."""
    if not st.session_state.manager:
        return {}

    return st.session_state.manager.get_stream_info()

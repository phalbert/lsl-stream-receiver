"""
Data Tab Module
===============

Data logging, quality information, and export functionality.
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from ..utils.data_manager import export_all_data


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

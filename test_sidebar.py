#!/usr/bin/env python3
"""
Simple test to verify sidebar button visibility
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Sidebar Test",
    page_icon="🔘",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Sidebar Button Visibility Test")

# Simplified sidebar with buttons at the top
with st.sidebar:
    st.header("🎮 Recording Controls")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Start Recording")
        start_clicked = st.button(
            "▶️ START",
            type="primary",
            use_container_width=True,
            disabled=False,  # Always enabled for testing
            help="Begin recording LSL streams"
        )
        if start_clicked:
            st.success("🎬 Starting...")
            st.session_state.recording_started = True

    with col2:
        st.markdown("### Stop Recording")
        stop_clicked = st.button(
            "⏹️ STOP",
            type="secondary",
            use_container_width=True,
            disabled=False,  # Always enabled for testing
            help="Stop recording and save data"
        )
        if stop_clicked:
            st.success("⏹️ Stopping...")
            st.session_state.recording_stopped = True

    # Status indicator
    if st.session_state.get('recording_started', False):
        st.success("🔴 **RECORDING ACTIVE**")
    elif st.session_state.get('recording_stopped', False):
        st.success("⚫ **RECORDING STOPPED**")
    else:
        st.info("⚪ **READY TO RECORD**")

    st.markdown("---")

    st.subheader("📝 Session Settings")
    session_name = st.text_input(
        "Session Name",
        value="test_session",
        help="Name for this recording session"
    )

    st.subheader("📡 Stream Discovery")
    auto_discovery = st.checkbox("Auto-discover streams", value=True)

    st.subheader("⚙️ Recording Settings")
    formats = st.multiselect(
        "Output Formats",
        ["csv", "json", "parquet"],
        default=["csv", "json"]
    )

# Main content
st.header("Main Content Area")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Status", "Ready" if not st.session_state.get('recording_started', False) else "Recording")

with col2:
    st.metric("Session", session_name)

with col3:
    st.metric("Formats", len(formats))

st.info("🎯 **Buttons should be visible at the TOP of the sidebar**")

if st.session_state.get('recording_started', False):
    st.success("✅ Recording was started successfully!")
elif st.session_state.get('recording_stopped', False):
    st.success("✅ Recording was stopped successfully!")

st.markdown("""
### What to check:
1. **Buttons visible?** - Look for "START" and "STOP" buttons at the top of the sidebar
2. **Buttons clickable?** - Try clicking them
3. **Feedback visible?** - Check for success messages when clicked
4. **No scroll needed?** - Buttons should be immediately visible without scrolling
""")

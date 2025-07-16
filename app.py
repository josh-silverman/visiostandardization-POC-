import streamlit as st
import traceback

from extract_xml import run_extract_xml
from parse_visio import run_parse_visio
from ai_standardize import run_ai_standardize
from json_to_xml import run_json_to_xml
from create_vsdx import run_create_vsdx

import os

STEPS = [
    ("Extracting Visio File from secure Azure Blob storage", run_extract_xml),
    ("Parsing original Visio file", run_parse_visio),
    ("Standardizing Visio file using template", run_ai_standardize),
    ("Recreating Visio file", run_json_to_xml),
    ("Copying Visio file to secure Azure Blob storage", run_create_vsdx),
]

def step_key(n):
    return f"step_{n}_done"

def main():
    st.set_page_config(page_title="Visio Network Diagram Processing Pipeline", page_icon="🗂️", layout="wide")
    st.title("🗂️ Visio Network Diagram Processing Pipeline")

    # Add the logo to the sidebar
    st.sidebar.image("GlobalLogo_NTTDATA_FutureBlue_RGB.png", use_container_width=True)
    st.sidebar.header("Pipeline Steps")
    run_all = st.sidebar.button("🚦 Run All Steps", use_container_width=True)
    st.sidebar.markdown("---")

    completed = {}
    for idx, (desc, _) in enumerate(STEPS):
        completed[idx] = st.session_state.get(step_key(idx), False)
        st.sidebar.checkbox(
            f"{'✅' if completed[idx] else '⬜️'} {desc}",
            value=completed[idx],
            key=f"sidebar_{idx}",
            disabled=True
        )

    st.markdown("### Pipeline Progress")
    for idx, (desc, _) in enumerate(STEPS):
        if completed[idx]:
            st.success(f"Step {idx+1}: {desc}")
        else:
            st.info(f"Step {idx+1}: {desc}")

    st.markdown("---")

    log_placeholder = st.empty()
    error_placeholder = st.empty()

    def run_step(idx):
        desc, func = STEPS[idx]
        log_placeholder.info(f"Running step {idx+1}: {desc} ...")
        try:
            func()
            st.session_state[step_key(idx)] = True
            log_placeholder.success(f"Step {idx+1}: {desc} completed.")
            error_placeholder.empty()
        except Exception as e:
            st.session_state[step_key(idx)] = False
            log_placeholder.error(f"Step {idx+1}: {desc} failed.")
            error_placeholder.error(f"Error: {e}\n\n{traceback.format_exc()}")

    # --- This block is the only change for progressive checking! ---
    if "run_all_progress" not in st.session_state:
        st.session_state.run_all_progress = 0

    if run_all:
        st.session_state.run_all_progress = 0  # Start from the beginning

    # Progressively run steps, one per rerun
    if st.session_state.run_all_progress < len(STEPS):
        if run_all or st.session_state.run_all_progress > 0:
            idx = st.session_state.run_all_progress
            if not st.session_state.get(step_key(idx), False):
                run_step(idx)
            st.session_state.run_all_progress += 1
            st.rerun()  # Streamlit v1.25+ rerun
    # Reset progress tracker after all done
    elif st.session_state.run_all_progress >= len(STEPS):
        st.session_state.run_all_progress = 0

    st.markdown("---")

    # Optionally offer download of the created vsdx
    output_vsdx = "output.vsdx"
    if os.path.isfile(output_vsdx) and all(st.session_state.get(step_key(idx), False) for idx in range(len(STEPS))):
        with open(output_vsdx, "rb") as f:
            st.download_button("⬇️ Download Output VSDX", f, file_name="output.vsdx", mime="application/zip")

if __name__ == "__main__":
    main()

# visio_streamlit_app.py

import streamlit as st
import traceback
import os

# --- Import your backend functions ---
from extract_xml import main as run_extract_xml
from first_step import standardize_text_connectors_and_fill as run_standardize
from footer import main as run_footer
from create_vsdx import main as run_create_vsdx

# Pipeline steps with descriptions and function references
STEPS = [
    ("Inserting Visio (.vsdx) file", None),  # Special: handled by uploader
    ("Parsing original Visio file", run_extract_xml),
    ("Standardize diagram XML", lambda: run_standardize("output_xml/visio/pages/page1.xml")),  # or correct path
    ("Apply standardized footer", run_footer),
    ("Re-zip into new .vsdx", run_create_vsdx),
]

def step_key(n):
    return f"step_{n}_done"

def main():
    st.set_page_config(page_title="Visio Network Diagram Standardizer", page_icon="🗂️", layout="wide")
    st.title("🗂️ Visio Network Diagram Standardizer")

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

    # ---- Step 1: Upload ----
    st.markdown("#### Step 1: Upload your Visio (.vsdx) file")
    uploaded_file = st.file_uploader("Upload .vsdx file", type=["vsdx"])
    if uploaded_file is not None:
        with open("input.vsdx", "wb") as f:
            f.write(uploaded_file.read())
        st.session_state[step_key(0)] = True
        st.success("Visio file uploaded!")
    else:
        st.session_state[step_key(0)] = False

    # ---- Optional: Footer Customization ----
    st.sidebar.markdown("#### Footer Customization (TO BE ADDED LATER)")
    # (Customization code removed by request)

    # ---- Step running logic ----
    def run_step(idx):
        desc, func = STEPS[idx]
        log_placeholder.info(f"Running step {idx+1}: {desc} ...")
        try:
            if func is not None:
                func()
            st.session_state[step_key(idx)] = True
            log_placeholder.success(f"Step {idx+1}: {desc} completed.")
            error_placeholder.empty()
        except Exception as e:
            st.session_state[step_key(idx)] = False
            log_placeholder.error(f"Step {idx+1}: {desc} failed.")
            error_placeholder.error(f"Error: {e}\n\n{traceback.format_exc()}")

    # ---- Orchestrate pipeline with progressive running ----
    if "run_all_progress" not in st.session_state:
        st.session_state.run_all_progress = 0

    if run_all:
        st.session_state.run_all_progress = 1 if st.session_state.get(step_key(0), False) else 0

    if st.session_state.run_all_progress < len(STEPS):
        if run_all or st.session_state.run_all_progress > 0:
            idx = st.session_state.run_all_progress
            # Only run if previous step is done (except for the upload step)
            if (idx == 0 or st.session_state.get(step_key(idx-1), False)) and not st.session_state.get(step_key(idx), False):
                run_step(idx)
            st.session_state.run_all_progress += 1
            st.rerun()
    elif st.session_state.run_all_progress >= len(STEPS):
        st.session_state.run_all_progress = 0

    st.markdown("---")

    # ---- Step 6: Download output ----
    output_vsdx = "output.vsdx"
    if os.path.isfile(output_vsdx) and all(st.session_state.get(step_key(idx), False) for idx in range(len(STEPS))):
        with open(output_vsdx, "rb") as f:
            st.download_button("⬇️ Download Output VSDX", f, file_name="output.vsdx", mime="application/zip")

    # ---- (Optional) Preview standardized XML ----
    st.markdown("---")
    st.markdown("#### (Optional) Preview Standardized XML")
    standardized_xml_path = "output_xml/visio/pages/page1.xml"
    if os.path.isfile(standardized_xml_path):
        with open(standardized_xml_path, "r", encoding="utf-8") as f:
            xml_content = f.read()
        st.code(xml_content, language="xml")

if __name__ == "__main__":
    main()

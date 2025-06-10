import streamlit as st

st.set_page_config(page_title="Visio Standardization UI", layout="centered")

st.title("AI-Driven Visio Standardization")

# --- File Upload Section ---
st.header("1. Upload Visio File")
uploaded_file = st.file_uploader(
    "Upload a Visio (.vsdx) file",
    type=["vsdx"],
    help="Only .vsdx files are supported"
)
if uploaded_file:
    st.success(f"'{uploaded_file.name}' uploaded (not actually saved in this demo).")
    st.info("Processing will start automatically in the background.")

# --- Show Processing Status ---
st.header("2. Processing Status")

# Example placeholder data:
files = [
    {"name": "Network1.vsdx", "status": "Completed", "output": "Network1_standardized.vsdx"},
    {"name": "Network2.vsdx", "status": "Processing", "output": None},
    {"name": "Network3.vsdx", "status": "Flagged", "output": None},
]

st.subheader("Uploaded Files")
for f in files:
    st.write(f"**{f['name']}**: {f['status']}")
    if f["status"] == "Completed":
        st.markdown(f"[Download Standardized File](/dummy/{f['output']})", unsafe_allow_html=True)
    elif f["status"] == "Flagged":
        st.warning("Manual review required.")

# --- Flagged Files/Manual Review ---
st.header("3. Flagged Files for Manual Review")
flagged_files = [f for f in files if f["status"] == "Flagged"]
if flagged_files:
    for f in flagged_files:
        st.error(f"{f['name']} needs manual review.")
        st.markdown(f"[Download Flagged File](/dummy/{f['name']})", unsafe_allow_html=True)
else:
    st.info("No files currently flagged for review.")

# --- Download Original or Output Files ---
st.header("4. Download Files")
with st.expander("Show all processed files"):
    for f in files:
        if f["status"] == "Completed":
            st.write(f"{f['output']}")
            st.markdown(f"[Download](/dummy/{f['output']})", unsafe_allow_html=True)

# --- Settings/Validation (Optional) ---
with st.expander("Validation Reports / Settings (Demo)"):
    st.write("No validation issues detected in recent runs.")
    st.button("Re-run Validation (demo)")

st.write("---")
st.info("This app is a UI prototype. No backend functionality is connected.")

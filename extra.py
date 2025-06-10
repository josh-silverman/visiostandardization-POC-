# --- Streamlit App ---
st.title("Visio Diagram Analyzer with GPT-4o Vision")

st.markdown("""
Upload a **PNG or JPEG** image of a diagram (such as a Visio export or screenshot).
The app will:
- Use GPT-4o Vision to extract structured shape and connector data from the diagram
- Map the extracted info to a standardized template schema
""")

uploaded_file = st.file_uploader("Upload diagram image (PNG/JPEG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Diagram", use_column_width=True)
    if st.button("Analyze and Standardize with GPT-4o"):
        uploaded_file.seek(0)
        image_bytes = uploaded_file.read()
        with st.spinner("Analyzing diagram with GPT-4o..."):
            try:
                diagram_json = analyze_diagram_with_gpt4o(image_bytes)
            except Exception as e:
                st.error(f"Error from GPT-4o Vision: {e}")
                st.stop()
        st.subheader("Extracted JSON")
        st.code(diagram_json, language="json")
        with st.spinner("Standardizing to template..."):
            try:
                standardized = standardize_diagram_data(diagram_json)
            except Exception as e:
                st.error(f"Standardization error: {e}")
                st.stop()
        st.subheader("Standardized Data")
        st.json(standardized)
        st.download_button(
            "Download Standardized JSON",
            data=json.dumps(standardized, indent=2),
            file_name="standardized_diagram.json",
            mime="application/json"
        )

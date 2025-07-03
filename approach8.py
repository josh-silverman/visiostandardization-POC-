import streamlit as st
import openai
import os
import subprocess
import tempfile
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import cairosvg
import re

# --- Load environment variables ---
load_dotenv()
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")  # GPT-4o deployment
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

# --- Initialize Azure OpenAI client ---
openai.api_type = "azure"
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = "2024-02-15-preview"
openai.api_key = AZURE_OPENAI_API_KEY

st.title("Diagram Replicator: From Azure Blob VSDX to AI-Recreated SVG")

st.markdown("""
1. **Enter the base filename (no extension) for a VSDX file in your Azure Blob Storage.**
2. **The app downloads the VSDX, converts it to SVG, and sends it to GPT-4o.**
3. **GPT-4o outputs recreated SVG code, closely replicating the original diagram.**
4. **You can view and download the AI-generated SVG and PNG.**
""")

BASE_BLOB_NAME = st.text_input("Enter base blob name (no extension):", value="Test-image")
SOURCE_CONTAINER = st.text_input("Azure Blob source container", value="initial-vsdx")
TARGET_CONTAINER = st.text_input("Azure Blob target container (optional, for upload)", value="svg-files")

if st.button("Process VSDX from Azure Blob"):
    with st.spinner("Downloading VSDX from Azure Blob Storage..."):
        try:
            blob_service = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
            src_container_client = blob_service.get_container_client(SOURCE_CONTAINER)
            SOURCE_BLOB = f"{BASE_BLOB_NAME}.vsdx"

            with tempfile.TemporaryDirectory() as tmp_dir:
                # --- Download Main VSDX ---
                local_vsdx = os.path.join(tmp_dir, f"{BASE_BLOB_NAME}.vsdx")
                with open(local_vsdx, "wb") as f:
                    download_stream = src_container_client.download_blob(SOURCE_BLOB)
                    f.write(download_stream.readall())
                st.success(f"Downloaded {SOURCE_BLOB}")

                # --- Convert Main VSDX to SVG ---
                st.info("Converting VSDX to SVG using LibreOffice...")
                conversion = subprocess.run(
                    ["libreoffice", "--headless", "--convert-to", "svg", local_vsdx, "--outdir", tmp_dir],
                    capture_output=True
                )
                if conversion.returncode != 0:
                    st.error(f"Conversion failed: {conversion.stderr.decode()}")
                    st.stop()
                st.success("Conversion to SVG done.")

                # --- Find produced SVG(s) ---
                svg_files = [f for f in os.listdir(tmp_dir) if f.lower().endswith('.svg')]
                if not svg_files:
                    st.error("No SVG files found after conversion!")
                    st.stop()
                svg_path = os.path.join(tmp_dir, svg_files[0])
                with open(svg_path, "r", encoding="utf-8") as fsvg:
                    svg_code_original = fsvg.read()

                st.markdown("**Preview of SVG converted from VSDX:**")
                st.image(svg_code_original)
                st.download_button(
                    label="Download original SVG",
                    data=svg_code_original,
                    file_name="original_diagram.svg",
                    mime="image/svg+xml"
                )

                # --- (Optional) Upload SVG to Azure Blob target container ---
                if TARGET_CONTAINER:
                    tgt_container_client = blob_service.get_container_client(TARGET_CONTAINER)
                    with open(svg_path, "rb") as data:
                        tgt_container_client.upload_blob(
                            svg_files[0],
                            data,
                            overwrite=True
                        )
                    st.success(f"Uploaded {svg_files[0]} to {TARGET_CONTAINER}/{svg_files[0]}")

                # --- AI: Faithful SVG Replication ---
                st.info("Sending SVG to GPT-4o for faithful recreation...")
                prompt = '''
You are given an SVG diagram. Faithfully recreate the diagram as SVG, preserving all shapes, their positions and sizes, all text, connectors, and arrows. 
Do not change the style, layout, or structure—just reconstruct the same diagram as closely as possible.
Output only the SVG code.
'''
                try:
                    response = openai.ChatCompletion.create(
                        engine=AZURE_OPENAI_DEPLOYMENT,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant who analyzes diagrams and outputs SVG code."},
                            {"role": "user", "content": prompt + "\n\n" + svg_code_original}
                        ],
                        max_tokens=2000,
                    )
                    answer = response['choices'][0]['message']['content']
                    svg_match = re.search(r'(<svg.*?</svg>)', answer, re.DOTALL | re.IGNORECASE)
                    if not svg_match:
                        st.error("Could not extract SVG code from the model response.")
                        st.code(answer)
                        st.stop()

                    svg_code = svg_match.group(1)

                    st.markdown("**AI-Recreated SVG Diagram:**")
                    st.image(svg_code)
                    st.download_button(
                        label="Download AI-recreated SVG",
                        data=svg_code,
                        file_name="ai_recreated_diagram.svg",
                        mime="image/svg+xml"
                    )

                    # --- Convert SVG to PNG using cairosvg ---
                    try:
                        png_bytes = cairosvg.svg2png(bytestring=svg_code.encode("utf-8"))
                        st.markdown("**PNG Diagram (AI recreation):**")
                        st.image(png_bytes)
                        st.download_button(
                            label="Download PNG (AI recreation)",
                            data=png_bytes,
                            file_name="ai_recreated_diagram.png",
                            mime="image/png"
                        )
                    except Exception as e:
                        st.error(f"Could not convert SVG to PNG: {e}")

                    st.markdown("**Raw SVG code generated by GPT-4o:**")
                    st.code(svg_code, language="svg")

                except Exception as e:
                    st.error(f"Azure OpenAI error: {e}")

        except Exception as e:
            st.error(f"Azure Blob error: {e}")

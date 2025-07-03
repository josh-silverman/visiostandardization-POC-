
import streamlit as st
import openai
import os
import base64
import subprocess
import tempfile
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import cairosvg

import math
from xml.etree import ElementTree as ET

def get_center(rect):
    x = float(rect.attrib.get('x', 0))
    y = float(rect.attrib.get('y', 0))
    w = float(rect.attrib.get('width', 0))
    h = float(rect.attrib.get('height', 0))
    return (x + w/2, y + h/2)

def line_to_square_edge(from_rect, to_rect):
    x1, y1 = get_center(from_rect)
    x2, y2 = get_center(to_rect)
    def edge_point(rect, other_x, other_y):
        rx, ry = get_center(rect)
        w = float(rect.attrib.get('width', 0))
        h = float(rect.attrib.get('height', 0))
        dx = other_x - rx
        dy = other_y - ry
        if dx == 0 and dy == 0:
            return rx, ry
        scale_x = w / 2 / abs(dx) if dx != 0 else float('inf')
        scale_y = h / 2 / abs(dy) if dy != 0 else float('inf')
        scale = min(scale_x, scale_y)
        ex = rx + dx * scale
        ey = ry + dy * scale
        return ex, ey
    start = edge_point(from_rect, x2, y2)
    end = edge_point(to_rect, x1, y1)
    return start, end

def add_arrow_marker(svg_root):
    ns = {'svg': "http://www.w3.org/2000/svg"}
    defs = svg_root.find('svg:defs', ns)
    if defs is None:
        defs = ET.Element('{http://www.w3.org/2000/svg}defs')
        svg_root.insert(0, defs)
    for marker in defs.findall('svg:marker', ns):
        if marker.attrib.get('id') == 'arrowhead':
            return
    marker = ET.fromstring('''
      <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
        <polygon points="0 0, 10 3.5, 0 7" fill="black"/>
      </marker>
    ''')
    defs.append(marker)

def fix_svg_connectors(svg_code):
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    try:
        root = ET.fromstring(svg_code)
    except Exception:
        return svg_code  # fallback if SVG is too complex
    ns = {'svg': "http://www.w3.org/2000/svg"}
    rects = [el for el in root.findall('.//svg:rect', ns)]
    lines = [el for el in root.findall('.//svg:line', ns)]
    if len(rects) < 2:
        return svg_code  # Not enough shapes to connect
    # For each line, snap endpoints to nearest rectangles
    for line in lines:
        x1, y1 = float(line.attrib['x1']), float(line.attrib['y1'])
        x2, y2 = float(line.attrib['x2']), float(line.attrib['y2'])
        def nearest_rect(px, py):
            return min(rects, key=lambda r: math.hypot(get_center(r)[0] - px, get_center(r)[1] - py))
        from_rect = nearest_rect(x1, y1)
        to_rect = nearest_rect(x2, y2)
        (sx, sy), (ex, ey) = line_to_square_edge(from_rect, to_rect)
        line.attrib['x1'] = str(sx)
        line.attrib['y1'] = str(sy)
        line.attrib['x2'] = str(ex)
        line.attrib['y2'] = str(ey)
        line.attrib['marker-end'] = 'url(#arrowhead)'
    add_arrow_marker(root)
    return ET.tostring(root, encoding='unicode')


# # --- Load environment variables ---
# load_dotenv()
# AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
# AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
# AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")  # GPT-4o deployment
# AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

# # --- Initialize Azure OpenAI client ---
# openai.api_type = "azure"
# openai.api_base = AZURE_OPENAI_ENDPOINT
# openai.api_version = "2024-02-15-preview"
# openai.api_key = AZURE_OPENAI_API_KEY

# st.title("Diagram Standardizer: From Azure Blob VSDX to AI-Standardized SVG")

# st.markdown("""
# 1. **Enter the base filename (no extension) for a VSDX file in your Azure Blob Storage.**
# 2. **The app downloads the VSDX, converts it to SVG, and sends it to GPT-4o.**
# 3. **GPT-4o outputs SVG code, with all shapes replaced by squares at their original locations, keeping labels and connectors.**
# 4. **You can view and download the standardized SVG and PNG.**
# """)

# BASE_BLOB_NAME = st.text_input("Enter base blob name (no extension):", value="SLM-DMVOSCI (1)")
# SOURCE_CONTAINER = st.text_input("Azure Blob source container", value="initial-vsdx")
# TARGET_CONTAINER = st.text_input("Azure Blob target container (optional, for upload)", value="svg-files")
# if st.button("Process VSDX from Azure Blob"):
#     with st.spinner("Downloading VSDX from Azure Blob Storage..."):
#         try:
#             blob_service = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
#             src_container_client = blob_service.get_container_client(SOURCE_CONTAINER)
#             SOURCE_BLOB = f"{BASE_BLOB_NAME}.vsdx"

#             with tempfile.TemporaryDirectory() as tmp_dir:
#                 # --- Download user VSDX ---
#                 local_vsdx = os.path.join(tmp_dir, f"{BASE_BLOB_NAME}.vsdx")
#                 with open(local_vsdx, "wb") as f:
#                     download_stream = src_container_client.download_blob(SOURCE_BLOB)
#                     f.write(download_stream.readall())
#                 st.success(f"Downloaded {SOURCE_BLOB}")

#                 # --- Convert user VSDX to SVG ---
#                 st.info("Converting user VSDX to SVG using LibreOffice...")
#                 conversion = subprocess.run(
#                     ["libreoffice", "--headless", "--convert-to", "svg", local_vsdx, "--outdir", tmp_dir],
#                     capture_output=True
#                 )
#                 if conversion.returncode != 0:
#                     st.error(f"Conversion failed: {conversion.stderr.decode()}")
#                     st.stop()
#                 st.success("Conversion to SVG done.")

#                 svg_files = [f for f in os.listdir(tmp_dir) if f.lower().endswith('.svg')]
#                 if not svg_files:
#                     st.error("No SVG files found after conversion!")
#                     st.stop()
#                 svg_path = os.path.join(tmp_dir, svg_files[0])
#                 with open(svg_path, "r", encoding="utf-8") as fsvg:
#                     svg_code_original = fsvg.read()

#                 st.markdown("**Preview of SVG converted from VSDX:**")
#                 st.image(svg_code_original)
#                 st.download_button(
#                     label="Download original SVG",
#                     data=svg_code_original,
#                     file_name="original_diagram.svg",
#                     mime="image/svg+xml"
#                 )

#                 # (Optional) Upload SVG to Azure Blob target container
#                 if TARGET_CONTAINER:
#                     tgt_container_client = blob_service.get_container_client(TARGET_CONTAINER)
#                     with open(svg_path, "rb") as data:
#                         tgt_container_client.upload_blob(
#                             svg_files[0],
#                             data,
#                             overwrite=True
#                         )
#                     st.success(f"Uploaded {svg_files[0]} to {TARGET_CONTAINER}/{svg_files[0]}")

#                 # --- Download template VSDX from standardized-template container ---
#                 st.info("Downloading template VSDX from Azure Blob Storage...")
#                 template_container_client = blob_service.get_container_client("standardized-template")
#                 TEMPLATE_BLOB = "SLM-DMVOSCI - Converted (1).vsdx"
#                 template_vsdx_path = os.path.join(tmp_dir, "template.vsdx")
#                 with open(template_vsdx_path, "wb") as tf:
#                     template_stream = template_container_client.download_blob(TEMPLATE_BLOB)
#                     tf.write(template_stream.readall())
#                 st.success("Downloaded template VSDX.")

#                 # --- Convert template VSDX to SVG ---
#                 st.info("Converting template VSDX to SVG using LibreOffice...")
#                 template_conversion = subprocess.run(
#                     ["libreoffice", "--headless", "--convert-to", "svg", template_vsdx_path, "--outdir", tmp_dir],
#                     capture_output=True
#                 )
#                 if template_conversion.returncode != 0:
#                     st.error(f"Template conversion failed: {template_conversion.stderr.decode()}")
#                     st.stop()

#                 template_svg_files = [f for f in os.listdir(tmp_dir) 
#                                      if f.lower().endswith('.svg') and f != svg_files[0]]
#                 if not template_svg_files:
#                     st.error("No SVG files found after template conversion!")
#                     st.stop()
#                 template_svg_path = os.path.join(tmp_dir, template_svg_files[0])
#                 with open(template_svg_path, "r", encoding="utf-8") as tsvg:
#                     template_svg_code = tsvg.read()
#                 st.success("Converted template VSDX to SVG.")

#                 st.markdown("**Standardized Template SVG Preview:**")
#                 st.image(template_svg_code)
#                 st.download_button(
#                     label="Download standardized template SVG",
#                     data=template_svg_code,
#                     file_name="standardized_template.svg",
#                     mime="image/svg+xml"
#                 )

#                 # --- AI: Standardize SVG using the template ---
#                 st.info("Sending SVG and template to GPT-4o for square-standardization...")

#                 extraction_prompt = f"""
# Here is an example of how to standardize a diagram:

# Input SVG Example:
# {template_svg_code}

# ---

# Now, using this as a template, convert the following SVG diagram to the same standardized style (all shapes as squares/rects, connectors as lines with arrowheads, and labels preserved):

# {svg_code_original}

# Output only the standardized SVG code.
# """

#                 try:
#                     response = openai.ChatCompletion.create(
#                         engine=AZURE_OPENAI_DEPLOYMENT,
#                         messages=[
#                             {"role": "system", "content": "You are a helpful assistant who analyzes diagrams and outputs SVG code."},
#                             {"role": "user", "content": extraction_prompt}
#                         ],
#                         max_tokens=10000,
#                     )
#                     answer = response['choices'][0]['message']['content']
#                     import re
#                     svg_match = re.search(r'(<svg.*?</svg>)', answer, re.DOTALL | re.IGNORECASE)
#                     if not svg_match:
#                         st.error("Could not extract SVG code from the model response.")
#                         st.code(answer)
#                         st.stop()

#                     svg_code = svg_match.group(1)
#                     svg_code_fixed = fix_svg_connectors(svg_code) 

#                     st.markdown("**Standardized SVG Diagram (with fixed connectors):**")
#                     st.image(svg_code_fixed)
#                     st.download_button(
#                         label="Download standardized SVG (fixed connectors)",
#                         data=svg_code_fixed,
#                         file_name="standardized_diagram_fixed.svg",
#                         mime="image/svg+xml"
#                     )

#                     # Convert fixed SVG to PNG using cairosvg
#                     try:
#                         png_bytes = cairosvg.svg2png(bytestring=svg_code_fixed.encode("utf-8"))
#                         st.markdown("**Standardized PNG Diagram (fixed connectors):**")
#                         st.image(png_bytes)
#                         st.download_button(
#                             label="Download PNG (fixed connectors)",
#                             data=png_bytes,
#                             file_name="standardized_diagram_fixed.png",
#                             mime="image/png"
#                         )
#                     except Exception as e:
#                         st.error(f"Could not convert SVG to PNG: {e}")

#                     st.markdown("**Raw SVG code generated by GPT-4o:**")
#                     st.code(svg_code, language="svg")

#                 except Exception as e:
#                     st.error(f"Azure OpenAI error: {e}")

#         except Exception as e:
#             st.error(f"Azure Blob error: {e}")


import os
import tempfile
import subprocess
import streamlit as st
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import openai
import cairosvg

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

st.title("Diagram Standardizer: From Azure Blob VSDX to AI-Standardized SVG")

st.markdown("""
This app downloads a VSDX diagram from Azure Blob Storage, converts it to SVG, and standardizes it using an AI template.
""")

# --- Hardcoded blob names and containers ---
DIAGRAM_CONTAINER = "initial-vsdx"
DIAGRAM_BLOB = "SLM-DMVOSCI (1).vsdx"
TEMPLATE_CONTAINER = "standardized-template"
TEMPLATE_BLOB = "SLM-DMVOSCI - Converted (1).vsdx"
TARGET_CONTAINER = "svg-files"  # Optional: where to upload the converted SVG

if st.button("Process VSDX from Azure Blob"):
    with st.spinner("Downloading VSDX from Azure Blob Storage..."):
        try:
            blob_service = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

            with tempfile.TemporaryDirectory() as tmp_dir:
                # --- Download user diagram VSDX ---
                src_container_client = blob_service.get_container_client(DIAGRAM_CONTAINER)
                local_vsdx = os.path.join(tmp_dir, DIAGRAM_BLOB)
                with open(local_vsdx, "wb") as f:
                    download_stream = src_container_client.download_blob(DIAGRAM_BLOB)
                    f.write(download_stream.readall())
                st.success(f"Downloaded {DIAGRAM_BLOB} from {DIAGRAM_CONTAINER}")

                # --- Convert user VSDX to SVG ---
                st.info("Converting user VSDX to SVG using LibreOffice...")
                conversion = subprocess.run(
                    ["libreoffice", "--headless", "--convert-to", "svg", local_vsdx, "--outdir", tmp_dir],
                    capture_output=True
                )
                if conversion.returncode != 0:
                    st.error(f"Conversion failed: {conversion.stderr.decode()}")
                    st.stop()
                st.success("Conversion to SVG done.")

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

                # (Optional) Upload SVG to Azure Blob target container
                if TARGET_CONTAINER:
                    tgt_container_client = blob_service.get_container_client(TARGET_CONTAINER)
                    with open(svg_path, "rb") as data:
                        tgt_container_client.upload_blob(
                            svg_files[0],
                            data,
                            overwrite=True
                        )
                    st.success(f"Uploaded {svg_files[0]} to {TARGET_CONTAINER}/{svg_files[0]}")

                # --- Download template VSDX ---
                st.info("Downloading template VSDX from Azure Blob Storage...")
                template_container_client = blob_service.get_container_client(TEMPLATE_CONTAINER)
                template_vsdx_path = os.path.join(tmp_dir, "template.vsdx")
                with open(template_vsdx_path, "wb") as tf:
                    template_stream = template_container_client.download_blob(TEMPLATE_BLOB)
                    tf.write(template_stream.readall())
                st.success("Downloaded template VSDX.")

                # --- Convert template VSDX to SVG ---
                st.info("Converting template VSDX to SVG using LibreOffice...")
                template_conversion = subprocess.run(
                    ["libreoffice", "--headless", "--convert-to", "svg", template_vsdx_path, "--outdir", tmp_dir],
                    capture_output=True
                )
                if template_conversion.returncode != 0:
                    st.error(f"Template conversion failed: {template_conversion.stderr.decode()}")
                    st.stop()

                template_svg_files = [f for f in os.listdir(tmp_dir) 
                                     if f.lower().endswith('.svg') and f != svg_files[0]]
                if not template_svg_files:
                    st.error("No SVG files found after template conversion!")
                    st.stop()
                template_svg_path = os.path.join(tmp_dir, template_svg_files[0])
                with open(template_svg_path, "r", encoding="utf-8") as tsvg:
                    template_svg_code = tsvg.read()
                st.success("Converted template VSDX to SVG.")

                st.markdown("**Standardized Template SVG Preview:**")
                st.image(template_svg_code)
                st.download_button(
                    label="Download standardized template SVG",
                    data=template_svg_code,
                    file_name="standardized_template.svg",
                    mime="image/svg+xml"
                )

                # --- AI: Standardize SVG using the template ---
                st.info("Sending SVG and template to GPT-4o for square-standardization...")

                extraction_prompt = f"""
Here is an example of how to standardize a diagram:

Input SVG Example:
{template_svg_code}

---

Now, using this as a template, convert the following SVG diagram to the same standardized style (all shapes as squares/rects, connectors as lines with arrowheads, and labels preserved):

{svg_code_original}

Output only the standardized SVG code.
"""

                try:
                    response = openai.ChatCompletion.create(
                        engine=AZURE_OPENAI_DEPLOYMENT,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant who analyzes diagrams and outputs SVG code."},
                            {"role": "user", "content": extraction_prompt}
                        ]
                        # max_tokens omitted to use model default
                    )
                    answer = response['choices'][0]['message']['content']
                    import re
                    svg_match = re.search(r'(<svg.*?</svg>)', answer, re.DOTALL | re.IGNORECASE)
                    if not svg_match:
                        st.error("Could not extract SVG code from the model response.")
                        st.code(answer)
                        st.stop()

                    svg_code = svg_match.group(1)

                    # If you have a fix_svg_connectors function, use it. Otherwise, skip or add yours here.
                    def fix_svg_connectors(svg_code):
                        # Dummy passthrough; replace with your logic if needed
                        return svg_code

                    svg_code_fixed = fix_svg_connectors(svg_code) 

                    st.markdown("**Standardized SVG Diagram (with fixed connectors):**")
                    st.image(svg_code_fixed)
                    st.download_button(
                        label="Download standardized SVG (fixed connectors)",
                        data=svg_code_fixed,
                        file_name="standardized_diagram_fixed.svg",
                        mime="image/svg+xml"
                    )

                    # Convert fixed SVG to PNG using cairosvg
                    try:
                        png_bytes = cairosvg.svg2png(bytestring=svg_code_fixed.encode("utf-8"))
                        st.markdown("**Standardized PNG Diagram (fixed connectors):**")
                        st.image(png_bytes)
                        st.download_button(
                            label="Download PNG (fixed connectors)",
                            data=png_bytes,
                            file_name="standardized_diagram_fixed.png",
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

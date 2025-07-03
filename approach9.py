import streamlit as st
import tempfile
import subprocess
import os
from azure.storage.blob import BlobServiceClient
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

st.title("Visio Diagram Shape Replacer (VSDX from Azure, VSSX stencil upload)")

st.markdown("""
**How this app works:**

1. Downloads `Test-image.vsdx` from your Azure Blob container `initial-vsdx`.
2. Converts it to SVG using LibreOffice.
3. You upload a Visio stencil file (VSSX).
4. The app extracts shapes from the VSSX file using <a href="https://github.com/nbelyh/vsdx2svg" target="_blank" rel="noopener noreferrer">vsdx2svg</a>.
5. You choose a shape from the extracted shapes.
6. All `<rect>` shapes in the diagram SVG are replaced with the chosen stencil shape.
""")

if st.button("Download and Convert VSDX from Azure Blob"):
    with st.spinner("Downloading and converting..."):
        try:
            # Download from Azure Blob
            blob_service = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
            src_container = blob_service.get_container_client("initial-vsdx")
            blob_name = "Test-image.vsdx"
            with tempfile.TemporaryDirectory() as tmpdir:
                local_vsdx = os.path.join(tmpdir, blob_name)
                with open(local_vsdx, "wb") as f:
                    download_stream = src_container.download_blob(blob_name)
                    f.write(download_stream.readall())
                st.success(f"Downloaded `{blob_name}` from Azure.")

                # Convert VSDX to SVG using LibreOffice
                st.info("Converting VSDX to SVG with LibreOffice...")
                conversion = subprocess.run(
                    ["libreoffice", "--headless", "--convert-to", "svg", local_vsdx, "--outdir", tmpdir],
                    capture_output=True
                )
                if conversion.returncode != 0:
                    st.error(f"LibreOffice conversion failed: {conversion.stderr.decode()}")
                    st.stop()

                # Get first SVG file
                svg_files = [f for f in os.listdir(tmpdir) if f.lower().endswith('.svg')]
                if not svg_files:
                    st.error("No SVG file was generated from VSDX.")
                    st.stop()
                svg_path = os.path.join(tmpdir, svg_files[0])
                with open(svg_path, "r", encoding="utf-8") as fsvg:
                    main_svg = fsvg.read()
                st.session_state["main_svg"] = main_svg  # Keep for later
                st.success("VSDX converted to SVG!")
                st.markdown("**Preview of diagram SVG:**")
                st.image(main_svg)
        except Exception as e:
            st.error(f"Azure Blob or conversion error: {e}")

# Step 2: User uploads VSSX stencil file
vssx_file = st.file_uploader("Upload your stencil VSSX file", type=['vssx'])

if "main_svg" in st.session_state and vssx_file:
    # Save the VSSX to a temp file
    with tempfile.TemporaryDirectory() as tmpdir:
        vssx_path = os.path.join(tmpdir, "stencil.vssx")
        with open(vssx_path, "wb") as f:
            f.write(vssx_file.read())
        st.info("Extracting shapes from VSSX using vsdx2svg...")

        # Make output directory for SVGs
        shapes_dir = os.path.join(tmpdir, "shapes")
        os.makedirs(shapes_dir, exist_ok=True)

        # Call vsdx2svg to extract shapes as SVGs
        # This will create SVG files for each master shape in the VSSX
        vsdx2svg_cmd = ["vsdx2svg", vssx_path, "--output", shapes_dir, "--split-pages"]
        result = subprocess.run(vsdx2svg_cmd, capture_output=True)
        if result.returncode != 0:
            st.error(f"vsdx2svg failed: {result.stderr.decode()}")
            st.stop()

        # List all SVGs extracted from VSSX
        shape_svgs = [f for f in os.listdir(shapes_dir) if f.lower().endswith('.svg')]
        if not shape_svgs:
            st.error("No shapes were extracted from the VSSX. Ensure your VSSX contains master shapes.")
            st.stop()

        st.markdown("### Select a shape from your VSSX stencil:")

        # Let user pick a shape by filename
        selected_shape = st.selectbox("Select master shape SVG", shape_svgs)
        with open(os.path.join(shapes_dir, selected_shape), "r", encoding="utf-8") as f:
            stencil_svg = f.read()

        # Show a preview of the selected shape
        st.markdown(f"#### Preview of shape: {selected_shape}")
        st.image(stencil_svg)

        # Parse the stencil SVG's first <g> as the shape group (adjust if needed)
        ET.register_namespace('', "http://www.w3.org/2000/svg")
        try:
            stencil_root = ET.fromstring(stencil_svg)
            # Try to find a <g> or use the whole SVG if not found
            stencil_group = stencil_root.find('.//{http://www.w3.org/2000/svg}g')
            if stencil_group is None:
                stencil_group = stencil_root
        except Exception as e:
            st.error(f"Could not parse stencil SVG: {e}")
            st.stop()

        # Now, replace all <rect> in the main SVG with this stencil group
        main_svg = st.session_state["main_svg"]
        main_root = ET.fromstring(main_svg)
        ns = {'svg': "http://www.w3.org/2000/svg"}
        count = 0
        for rect in main_root.findall('.//svg:rect', ns):
            x = float(rect.attrib.get('x', 0))
            y = float(rect.attrib.get('y', 0))
            width = float(rect.attrib.get('width', 40))
            height = float(rect.attrib.get('height', 40))

            # Clone the stencil group
            new_shape = ET.fromstring(ET.tostring(stencil_group, encoding='unicode'))
            transform = f"translate({x},{y}) scale({width/40},{height/40})"
            prev_transform = new_shape.attrib.get('transform', '')
            new_shape.attrib['transform'] = f"{prev_transform} {transform}".strip()

            parent = rect.getparent() if hasattr(rect, 'getparent') else main_root
            parent.insert(list(parent).index(rect), new_shape)
            parent.remove(rect)
            count += 1

        new_svg = ET.tostring(main_root, encoding='unicode')
        st.success(f"Replaced {count} <rect> shapes with the selected stencil shape.")

        st.markdown("### Resulting SVG Diagram:")
        st.image(new_svg)
        st.download_button(
            "Download new SVG",
            data=new_svg,
            file_name="diagram_with_replaced_shapes.svg",
            mime="image/svg+xml"
        )
        with st.expander("Show SVG code"):
            st.code(new_svg, language='xml')

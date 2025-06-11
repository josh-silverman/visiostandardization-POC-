# # app.py

# import os
# import json
# import shutil
# import logging
# from config import (
#     BLOB_CONTAINER_RAW, BLOB_CONTAINER_STD, TEMPLATE_VSTX_PATH, TEMPLATE_SCHEMA, TEMP_DIR
# )
# from storage import get_container_client, download_blob, upload_blob, list_blobs
# from visio_convert import visio_to_pngs, extract_visio_xml
# from gpt_analysis import gpt4o_analyze_image, gpt4o_analyze_xml
# from standardize import map_to_template_schema, create_visio_diagram
# from validation import validate_standardized_file
# from utils import clean_dir

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s %(levelname)s %(message)s"
# )

# def process_visio_file(blob_name):
#     """Process a single Visio file from Azure Blob Storage."""
#     raw_container = get_container_client(BLOB_CONTAINER_RAW)
#     std_container = get_container_client(BLOB_CONTAINER_STD)
#     base_name = os.path.splitext(os.path.basename(blob_name))[0]
#     local_dir = os.path.join(TEMP_DIR, base_name)
#     clean_dir(local_dir)
#     local_vsdx = os.path.join(local_dir, f"{base_name}.vsdx")

#     # Download from blob storage
#     logging.info(f"Downloading {blob_name}...")
#     download_blob(raw_container.get_blob_client(blob_name), local_vsdx)

#     # Step 1: Convert to PNG(s)
#     logging.info("Converting Visio to PNG...")
#     png_paths = visio_to_pngs(local_vsdx, local_dir)
#     png_path = png_paths[0]  # Process only first page for demo

#     # Step 2: Analyze with GPT-4o Vision
#     logging.info("Analyzing image with GPT-4o...")
#     diagram_json = gpt4o_analyze_image(png_path)
#     diagram_data = json.loads(diagram_json)

#     # Step 3: Map to template
#     logging.info("Mapping extracted data to standardized schema...")
#     standardized_data = map_to_template_schema(diagram_data.get("shapes", []), TEMPLATE_SCHEMA)

#     # Step 4: Recreate standardized Visio
#     standardized_vsdx = os.path.join(local_dir, f"{base_name}_standardized.vsdx")
#     logging.info("Recreating standardized Visio diagram...")
#     create_visio_diagram(standardized_data, TEMPLATE_VSTX_PATH, standardized_vsdx)

#     # Step 5: Validate
#     valid, msg = validate_standardized_file(standardized_vsdx)
#     if not valid:
#         logging.error(f"Validation failed: {msg}")
#         raise Exception(f"Validation failed: {msg}")

#     # Step 6: Upload to standardized blob container
#     out_blob_name = f"{base_name}_standardized.vsdx"
#     upload_blob(std_container, standardized_vsdx, out_blob_name)
#     logging.info(f"Processed and uploaded: {out_blob_name}")

#     # Cleanup temp files
#     shutil.rmtree(local_dir, ignore_errors=True)

#     return out_blob_name

# def batch_process():
#     """Batch process all .vsdx files in the source blob container."""
#     raw_container = get_container_client(BLOB_CONTAINER_RAW)
#     blobs = list_blobs(raw_container, suffix='.vsdx')
#     logging.info(f"Found {len(blobs)} files to process.")

#     for blob in blobs:
#         try:
#             logging.info(f"Processing {blob.name}...")
#             process_visio_file(blob.name)
#             logging.info(f"Successfully processed {blob.name}")
#         except Exception as e:
#             logging.error(f"Error processing {blob.name}: {e}")

# def process_single_file(vsdx_path):
#     """
#     Process a single .vsdx file from local path.
#     Returns the path to the standardized .vsdx file.
#     """
#     import uuid
#     # Prepare temp dirs
#     unique_id = str(uuid.uuid4())
#     output_dir = os.path.join(TEMP_DIR, unique_id)
#     clean_dir(output_dir)

#     # Step 1: Convert to PNG (image-based)
#     png_paths = visio_to_pngs(vsdx_path, output_dir)
#     png_path = png_paths[0]

#     # Step 2: Analyze with GPT-4o Vision
#     diagram_json = gpt4o_analyze_image(png_path)
#     diagram_data = json.loads(diagram_json)

#     # Step 3: Map to template
#     standardized_data = map_to_template_schema(diagram_data.get("shapes", []), TEMPLATE_SCHEMA)

#     # Step 4: Recreate standardized Visio file
#     output_vsdx = os.path.join(output_dir, "standardized.vsdx")
#     create_visio_diagram(standardized_data, TEMPLATE_VSTX_PATH, output_vsdx)

#     # Step 5: Validate
#     valid, msg = validate_standardized_file(output_vsdx)
#     if not valid:
#         raise Exception(f"Validation failed: {msg}")

#     return output_vsdx

# if __name__ == "__main__":
#     import argparse
#     parser = argparse.ArgumentParser(description="Visio Standardization Pipeline")
#     parser.add_argument("--batch", action="store_true", help="Run batch processing from Azure Blob Storage")
#     parser.add_argument("--single", type=str, help="Process a single .vsdx file (local path)")

#     args = parser.parse_args()
#     if args.batch:
#         batch_process()
#     elif args.single:
#         result = process_single_file(args.single)
#         print(f"Standardized file saved at: {result}")
#     else:
#         parser.print_help()







# import streamlit as st

# st.title("Visio Standardization Demo")

# uploaded_file = st.file_uploader("Upload a Visio (.vsdx) file", type=["vsdx"])
# if uploaded_file is not None:
#     st.success("File uploaded successfully!")



import streamlit as st
import os

# Title and instructions
st.title("Visio Standardization: PNG or XML Upload")
st.write("""
Upload either a PNG image or an XML file. The app will display the file type and basic info.
""")

# File uploader, restrict to PNG and XML
uploaded_file = st.file_uploader(
    "Choose a PNG or XML file",
    type=["png", "xml"]
)

if uploaded_file is not None:
    # Get file extension
    file_details = {
        "filename": uploaded_file.name,
        "filetype": uploaded_file.type,
        "filesize": uploaded_file.size
    }
    st.write("**File Details:**", file_details)

    # Process PNG
    if uploaded_file.type == "image/png" or uploaded_file.name.lower().endswith(".png"):
        st.image(uploaded_file, caption="Uploaded PNG", use_column_width=True)
        st.success("PNG image uploaded successfully!")
        # Add your PNG processing code here
        # result = process_png(uploaded_file)
        # st.write("Processing result:", result)

    # Process XML
    elif uploaded_file.type == "text/xml" or uploaded_file.name.lower().endswith(".xml"):
        xml_content = uploaded_file.read().decode("utf-8")
        st.code(xml_content[:1000], language="xml")  # Show first 1000 chars
        st.success("XML file uploaded successfully!")
        # Add your XML processing code here
        # result = process_xml(xml_content)
        # st.write("Processing result:", result)

    else:
        st.error("Unsupported file type!")

else:
    st.info("Please upload a PNG or XML file to get started.")

# Optional: Add a button to trigger processing
# if st.button("Process File"):
#     if uploaded_file is not None:
#         # Run your processing here
#         pass

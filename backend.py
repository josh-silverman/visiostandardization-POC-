# import os
# import zipfile
# import tempfile
# import shutil
# import subprocess
# from xml.etree import ElementTree as ET
# from azure.storage.blob import BlobServiceClient
# import openai
# from dotenv import load_dotenv

# # --- Load Azure and OpenAI config ---
# load_dotenv()

# # Azure Blob Storage config
# AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
# INPUT_CONTAINER_NAME = "initial-vsdx"
# INPUT_BLOB_NAME = "Test-image.vsdx"
# OUTPUT_CONTAINER_NAME = "result-vsdx"
# OUTPUT_BLOB_NAME = "result-test-image.vsdx"

# # Azure OpenAI config
# AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
# openai.api_type = "azure"
# openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
# openai.api_version = "2024-02-15-preview"
# openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")

# def download_blob_to_file(container_name, blob_name, destination_file):
#     blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
#     blob_client = blob_service_client.get_container_client(container_name).get_blob_client(blob_name)
#     with open(destination_file, "wb") as f:
#         f.write(blob_client.download_blob().readall())
#     print(f"Downloaded {blob_name} from {container_name} to {destination_file}")

# def upload_file_to_blob(container_name, blob_name, local_file):
#     blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
#     blob_client = blob_service_client.get_container_client(container_name).get_blob_client(blob_name)
#     with open(local_file, "rb") as f:
#         blob_client.upload_blob(f, overwrite=True)
#     print(f"Uploaded {local_file} to {blob_name} in {container_name}")

# def unzip_vsdx(vsdx_path, extract_dir):
#     with zipfile.ZipFile(vsdx_path, "r") as zip_ref:
#         zip_ref.extractall(extract_dir)

# def rezip_to_vsdx(folder, output_vsdx_path):
#     base = output_vsdx_path.replace('.vsdx', '')
#     shutil.make_archive(base, 'zip', folder)
#     if os.path.exists(output_vsdx_path):
#         os.remove(output_vsdx_path)
#     os.rename(base + '.zip', output_vsdx_path)

# def convert_vsdx_to_svg(vsdx_path, svg_output_dir):
#     os.makedirs(svg_output_dir, exist_ok=True)
#     result = subprocess.run([
#         "soffice", "--headless", "--convert-to", "svg", "--outdir", svg_output_dir, vsdx_path
#     ], capture_output=True)
#     if result.returncode != 0:
#         print("LibreOffice SVG export failed:", result.stderr.decode())
#     # Return list of SVG file paths
#     return [os.path.join(svg_output_dir, f) for f in os.listdir(svg_output_dir) if f.lower().endswith('.svg')]

# def ai_update_xml_with_svg(xml_text, svg_text):
#     prompt = (
#         "Here is the Visio XML for a diagram page:\n"
#         f"{xml_text}\n\n"
#         "Here is the SVG export for the same page:\n"
#         f"{svg_text}\n\n"
#         "Please standardize all shapes to squares of similar size and position, "
#         "but preserve all connectors/arrows and text labels as shown in the SVG. "
#         "Make sure that every shape, connector, and label present in the SVG is also present in the XML output, "
#         "with accurate positions and relationships. Return only valid Visio XML for this page."
#     )
#     response = openai.ChatCompletion.create(
#         engine=AZURE_OPENAI_DEPLOYMENT,
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.0,
#         max_tokens=4000
#     )
#     content = response['choices'][0]['message']['content']
#     # Extract XML part only (in case LLM adds explanation)
#     start = content.find("<")
#     end = content.rfind(">")
#     if start != -1 and end != -1:
#         xml_only = content[start:end+1]
#     else:
#         xml_only = content
#     return xml_only

# def main():
#     with tempfile.TemporaryDirectory() as tempdir:
#         # Step 1: Download Test-image.vsdx from initial-vsdx container
#         local_input = os.path.join(tempdir, "input.vsdx")
#         download_blob_to_file(INPUT_CONTAINER_NAME, INPUT_BLOB_NAME, local_input)

#         # Step 2: Unzip vsdx
#         unzip_dir = os.path.join(tempdir, "unzipped")
#         unzip_vsdx(local_input, unzip_dir)

#         # Step 3: Export SVG(s)
#         svg_dir = os.path.join(tempdir, "svg")
#         svg_files = convert_vsdx_to_svg(local_input, svg_dir)
#         svg_files.sort()  # Ensure order

#         # Step 4: For each page XML, use corresponding SVG
#         pages_dir = os.path.join(unzip_dir, "visio", "pages")
#         page_xml_files = sorted([f for f in os.listdir(pages_dir) if f.endswith('.xml')])
#         for i, page_xml in enumerate(page_xml_files):
#             xml_path = os.path.join(pages_dir, page_xml)
#             with open(xml_path, "r", encoding="utf-8") as f:
#                 xml_text = f.read()
#             # Get corresponding SVG (if available)
#             svg_text = ""
#             if i < len(svg_files):
#                 with open(svg_files[i], "r", encoding="utf-8") as f:
#                     svg_text = f.read()
#             else:
#                 print(f"No SVG found for {page_xml}, skipping SVG context.")
#             # AI update
#             updated_xml = ai_update_xml_with_svg(xml_text, svg_text)
#             # Optional: Validate XML
#             try:
#                 ET.fromstring(updated_xml)
#                 with open(xml_path, "w", encoding="utf-8") as f:
#                     f.write(updated_xml)
#                 print(f"Updated {page_xml} using AI and SVG context.")
#             except ET.ParseError as e:
#                 print(f"AI returned invalid XML for {page_xml}: {e}. Skipping.")

#         # Step 5: Re-zip to new vsdx
#         local_output = os.path.join(tempdir, "output.vsdx")
#         rezip_to_vsdx(unzip_dir, local_output)
#         print(f"Written updated file to {local_output}")

#         # Step 6: Upload Test-image.vsdx to result-vsdx container
#         upload_file_to_blob(OUTPUT_CONTAINER_NAME, OUTPUT_BLOB_NAME, local_output)

# if __name__ == "__main__":
#     main()








########################################################################################################################################################33
########################################################################################################################################################33
########################################################################################################################################################33
########################################################################################################################################################33
########################################################################################################################################################33
########################################################################################################################################################33
########################################################################################################################################################33
########################################################################################################################################################33
########################################################################################################################################################33
########################################################################################################################################################33
########################################################################################################################################################33
########################################################################################################################################################33

########################################################################################################################################################33
# MOST RECENT 6/24
########################################################################################################################################################33

# import os
# import zipfile
# import tempfile
# import shutil
# import subprocess
# from xml.etree import ElementTree as ET
# from azure.storage.blob import BlobServiceClient
# import openai
# from dotenv import load_dotenv

# # Load Azure and OpenAI config
# load_dotenv()

# # Azure Blob Storage config
# AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
# INPUT_CONTAINER_NAME = "initial-vsdx"
# INPUT_BLOB_NAME = "Test-image.vsdx"
# OUTPUT_CONTAINER_NAME = "result-vsdx"
# OUTPUT_BLOB_NAME = "result-test-image.vsdx"

# # Azure OpenAI config
# AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
# openai.api_type = "azure"
# openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
# openai.api_version = "2024-02-15-preview"
# openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")

# def download_blob_to_file(container_name, blob_name, destination_file):
#     blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
#     blob_client = blob_service_client.get_container_client(container_name).get_blob_client(blob_name)
#     with open(destination_file, "wb") as f:
#         f.write(blob_client.download_blob().readall())
#     print(f"Downloaded {blob_name} from {container_name} to {destination_file}")

# def upload_file_to_blob(container_name, blob_name, local_file):
#     blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
#     blob_client = blob_service_client.get_container_client(container_name).get_blob_client(blob_name)
#     with open(local_file, "rb") as f:
#         blob_client.upload_blob(f, overwrite=True)
#     print(f"Uploaded {local_file} to {blob_name} in {container_name}")

# def unzip_vsdx(vsdx_path, extract_dir):
#     with zipfile.ZipFile(vsdx_path, "r") as zip_ref:
#         zip_ref.extractall(extract_dir)

# def rezip_to_vsdx(folder, output_vsdx_path):
#     base = output_vsdx_path.replace('.vsdx', '')
#     shutil.make_archive(base, 'zip', folder)
#     if os.path.exists(output_vsdx_path):
#         os.remove(output_vsdx_path)
#     os.rename(base + '.zip', output_vsdx_path)

# def convert_vsdx_to_svg(vsdx_path, svg_output_dir):
#     os.makedirs(svg_output_dir, exist_ok=True)
#     result = subprocess.run([
#         "soffice", "--headless", "--convert-to", "svg", "--outdir", svg_output_dir, vsdx_path
#     ], capture_output=True)
#     if result.returncode != 0:
#         print("LibreOffice SVG export failed:", result.stderr.decode())
#     # Return list of SVG file paths
#     return [os.path.join(svg_output_dir, f) for f in os.listdir(svg_output_dir) if f.lower().endswith('.svg')]

# def ai_update_xml_with_svg(xml_text, svg_text):
#     prompt = f"""
# You are an expert in both Microsoft Visio XML and SVG diagram formats.

# Below is the original Visio XML markup for a diagram page:
# ---
# {xml_text}
# ---

# Below is the SVG export of the same diagram page, which accurately shows the positions, connectors, and text labels:
# ---
# {svg_text}
# ---

# **Your task:**
# - Recreate the Visio XML so that the resulting diagram, when opened in Visio, matches the SVG diagram exactly in terms of:
#     - Position and arrangement of all shapes
#     - All connectors/arrows (preserve their routing and connections between shapes)
#     - All text labels (preserve their content and ensure the text is perfectly centered both horizontally and vertically within each shape)
# - **Change:** For all shapes (boxes, circles, etc.), replace them with squares of approximately the same size for all, but keep their positions/layout as in the SVG.
# - **Do NOT** add, remove, or relabel any connectors, text labels, or shapes. The only change is that all shapes become squares of the same size.
# - ***IMPORTANT*** All connectors/arrows should connect the same shapes as in the SVG, and all text labels should be attached as in the SVG.
# - If a shape in the SVG has a text label, it should remain associated with the corresponding square in the Visio XML.
# - Only output valid Visio XML for a single diagram page—do not explain, do not output SVG, do not include anything else.

# **Instructions for Output:**
# - Only output valid Visio XML content for this page.
# - Do not include explanations or commentary.
# - Ensure the output is well-formed XML and ready to replace the original page XML in a .vsdx file.

# **Original Visio XML and SVG inputs are above. Please begin your output below.**
# """


#     response = openai.ChatCompletion.create(
#         engine=AZURE_OPENAI_DEPLOYMENT,
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.0,
#         max_tokens=4000
#     )
#     content = response['choices'][0]['message']['content']
#     # Extract XML part only (in case LLM adds explanation)
#     start = content.find("<")
#     end = content.rfind(">")
#     if start != -1 and end != -1:
#         xml_only = content[start:end+1]
#     else:
#         xml_only = content
#     return xml_only

# def main():
#     with tempfile.TemporaryDirectory() as tempdir:
#         # Step 1: Download Test-image.vsdx from initial-vsdx container
#         local_input = os.path.join(tempdir, "input.vsdx")
#         download_blob_to_file(INPUT_CONTAINER_NAME, INPUT_BLOB_NAME, local_input)

#         # Step 2: Unzip vsdx
#         unzip_dir = os.path.join(tempdir, "unzipped")
#         unzip_vsdx(local_input, unzip_dir)

#         # Step 3: Export SVG(s)
#         svg_dir = os.path.join(tempdir, "svg")
#         svg_files = convert_vsdx_to_svg(local_input, svg_dir)
#         svg_files.sort()  # Ensure order

#         # Step 4: For each page XML, use corresponding SVG
#         pages_dir = os.path.join(unzip_dir, "visio", "pages")
#         page_xml_files = sorted([f for f in os.listdir(pages_dir) if f.endswith('.xml')])
#         for i, page_xml in enumerate(page_xml_files):
#             xml_path = os.path.join(pages_dir, page_xml)
#             with open(xml_path, "r", encoding="utf-8") as f:
#                 xml_text = f.read()
#             # Get corresponding SVG (if available)
#             svg_text = ""
#             svg_file = None
#             if i < len(svg_files):
#                 svg_file = svg_files[i]
#                 with open(svg_file, "r", encoding="utf-8") as f:
#                     svg_text = f.read()
#             else:
#                 print(f"No SVG found for {page_xml}, skipping SVG context.")

#             # --- PRINT OUT WHAT AI IS GETTING ---
#             print(f"\n---- AI INPUT FOR PAGE: {page_xml} ----")
#             print(f"XML file: {xml_path}")
#             print(f"XML content (first 500 chars):\n{xml_text[:500]}\n")
#             if svg_file:
#                 print(f"SVG file: {svg_file}")
#                 print(f"SVG content (first 500 chars):\n{svg_text[:500]}\n")
#             else:
#                 print("No SVG paired with this page.")
#             print("---- END AI INPUT PREVIEW ----\n")

#             # AI update
#             updated_xml = ai_update_xml_with_svg(xml_text, svg_text)
#             # Optional: Validate XML
#             try:
#                 ET.fromstring(updated_xml)
#                 with open(xml_path, "w", encoding="utf-8") as f:
#                     f.write(updated_xml)
#                 print(f"Updated {page_xml} using AI and SVG context.")
#             except ET.ParseError as e:
#                 print(f"AI returned invalid XML for {page_xml}: {e}. Skipping.")

#         # Step 5: Re-zip to new vsdx
#         local_output = os.path.join(tempdir, "output.vsdx")
#         rezip_to_vsdx(unzip_dir, local_output)
#         print(f"Written updated file to {local_output}")

#         # Step 6: Upload Test-image.vsdx to result-vsdx container
#         upload_file_to_blob(OUTPUT_CONTAINER_NAME, OUTPUT_BLOB_NAME, local_output)

# if __name__ == "__main__":
#     main()



########################################################################################################################################################33


import os
import zipfile
import tempfile
import shutil
import subprocess
from xml.etree import ElementTree as ET
from azure.storage.blob import BlobServiceClient
import openai
from dotenv import load_dotenv

# Load Azure and OpenAI config
load_dotenv()

# Azure Blob Storage config
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
INPUT_CONTAINER_NAME = "initial-vsdx"
INPUT_BLOB_NAME = "Test-image.vsdx"
OUTPUT_CONTAINER_NAME = "result-vsdx"
OUTPUT_BLOB_NAME = "result-test-image.vsdx"

# Azure OpenAI config
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2024-02-15-preview"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")

def download_blob_to_file(container_name, blob_name, destination_file):
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_container_client(container_name).get_blob_client(blob_name)
    with open(destination_file, "wb") as f:
        f.write(blob_client.download_blob().readall())
    print(f"Downloaded {blob_name} from {container_name} to {destination_file}")

def upload_file_to_blob(container_name, blob_name, local_file):
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_container_client(container_name).get_blob_client(blob_name)
    with open(local_file, "rb") as f:
        blob_client.upload_blob(f, overwrite=True)
    print(f"Uploaded {local_file} to {blob_name} in {container_name}")

def unzip_vsdx(vsdx_path, extract_dir):
    with zipfile.ZipFile(vsdx_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

def rezip_to_vsdx(folder, output_vsdx_path):
    base = output_vsdx_path.replace('.vsdx', '')
    shutil.make_archive(base, 'zip', folder)
    if os.path.exists(output_vsdx_path):
        os.remove(output_vsdx_path)
    os.rename(base + '.zip', output_vsdx_path)

def convert_vsdx_to_svg_and_png(vsdx_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    # Convert to SVG
    subprocess.run([
        "soffice", "--headless", "--convert-to", "svg", "--outdir", output_dir, vsdx_path
    ], check=True)
    # Convert to PNG
    subprocess.run([
        "soffice", "--headless", "--convert-to", "png", "--outdir", output_dir, vsdx_path
    ], check=True)
    svg_files = sorted([os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.lower().endswith('.svg')])
    png_files = sorted([os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.lower().endswith('.png')])
    return svg_files, png_files

import base64
def ai_update_xml_with_svg_and_png(xml_text, svg_text, png_path):
    prompt = f"""
You are an expert in both Microsoft Visio XML and SVG diagram formats.

Below is the original Visio XML markup for a diagram page:
---
{xml_text}
---

Below is the SVG export of the same diagram page, which accurately shows the positions, connectors, and text labels:
---
{svg_text}
---

Below is a PNG image of the correct visual appearance of the diagram page.

**Your task:**
- Recreate the Visio XML so that the resulting diagram, when opened in Visio, matches the SVG diagram and PNG image exactly in terms of:
    - Position and arrangement of all shapes
    - All connectors/arrows (preserve their routing and connections between shapes)
    - All text labels (preserve their content and ensure the text is perfectly centered both horizontally and vertically within each shape)
- **Change:** For all shapes (boxes, circles, etc.), replace them with squares of approximately the same size for all, but keep their positions/layout as in the SVG/PNG.
- **Do NOT** add, remove, or relabel any connectors, text labels, or shapes. The only change is that all shapes become squares of the same size.
- ***IMPORTANT*** All connectors/arrows should connect the same shapes as in the SVG/PNG, and all text labels should be attached as in the SVG/PNG.
- If a shape in the SVG/PNG has a text label, it should remain associated with the corresponding square in the Visio XML.
- Only output valid Visio XML for a single diagram page—do not explain, do not output SVG, do not include anything else.

**Instructions for Output:**
- Only output valid Visio XML content for this page.
- Do not include explanations or commentary.
- Ensure the output is well-formed XML and ready to replace the original page XML in a .vsdx file.

**Original Visio XML, SVG, and PNG inputs are above. Please begin your output below.**
"""

    # This example assumes OpenAI API supports image input in messages (as of GPT-4o and some preview models).
    # Adjust the API call as needed for your LLM provider.
    with open(png_path, "rb") as img_file:
        image_bytes = img_file.read()

    image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    messages = [
        {"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
        ]}
    ]

    # If Azure OpenAI doesn't yet support vision, you may need to use OpenAI's own GPT-4o endpoint.
    response = openai.ChatCompletion.create(
        engine=AZURE_OPENAI_DEPLOYMENT,
        messages=messages,
        temperature=0.0,
        max_tokens=4000
    )
    content = response['choices'][0]['message']['content']
    # Extract XML part only (in case LLM adds explanation)
    start = content.find("<")
    end = content.rfind(">")
    if start != -1 and end != -1:
        xml_only = content[start:end+1]
    else:
        xml_only = content
    return xml_only

def main():
    with tempfile.TemporaryDirectory() as tempdir:
        try:
            # Step 1: Download Test-image.vsdx from initial-vsdx container
            local_input = os.path.join(tempdir, "input.vsdx")
            download_blob_to_file(INPUT_CONTAINER_NAME, INPUT_BLOB_NAME, local_input)

            # Step 2: Unzip vsdx
            unzip_dir = os.path.join(tempdir, "unzipped")
            unzip_vsdx(local_input, unzip_dir)

            # Step 3: Export SVG(s) and PNG(s)
            export_dir = os.path.join(tempdir, "exports")
            svg_files, png_files = convert_vsdx_to_svg_and_png(local_input, export_dir)

            # Step 4: For each page XML, use corresponding SVG and PNG
            pages_dir = os.path.join(unzip_dir, "visio", "pages")
            page_xml_files = sorted([f for f in os.listdir(pages_dir) if f.startswith('page') and f.endswith('.xml')])
            for i, page_xml in enumerate(page_xml_files):
                xml_path = os.path.join(pages_dir, page_xml)
                with open(xml_path, "r", encoding="utf-8") as f:
                    xml_text = f.read()
                svg_text = ""
                png_path = None
                if i < len(svg_files):
                    with open(svg_files[i], "r", encoding="utf-8") as f:
                        svg_text = f.read()
                if i < len(png_files):
                    png_path = png_files[i]
                if not svg_text or not png_path:
                    print(f"SVG or PNG missing for {page_xml}, skipping.")
                    continue

                print(f"\n---- AI INPUT FOR PAGE: {page_xml} ----")
                print(f"XML file: {xml_path}")
                print(f"SVG file: {svg_files[i]}")
                print(f"PNG file: {png_path}")
                print("---- END AI INPUT PREVIEW ----\n")

                # AI Step: Update XML
                print(f"Calling AI for page: {page_xml}")
                               # AI Step: Update XML
                print(f"Calling AI for page: {page_xml}")
                try:
                    updated_xml = ai_update_xml_with_svg_and_png(xml_text, svg_text, png_path)
                except Exception as e:
                    print(f"AI call failed for {page_xml}: {e}")
                    continue
                print(f"AI call finished for page: {page_xml}")

                # Overwrite the XML file with AI-updated content
                with open(xml_path, "w", encoding="utf-8") as f:
                    f.write(updated_xml)
                print(f"Updated XML written to {xml_path}")

            # Step 5: Re-zip the folder to create updated VSDX
            output_vsdx = os.path.join(tempdir, "updated.vsdx")
            rezip_to_vsdx(unzip_dir, output_vsdx)
            print(f"Re-zipped updated files to {output_vsdx}")

            # Step 6: Upload the updated VSDX to Azure Blob Storage
            upload_file_to_blob(OUTPUT_CONTAINER_NAME, OUTPUT_BLOB_NAME, output_vsdx)
            print("Processing complete.")

        except Exception as e:
            print(f"Pipeline failed: {e}")


if __name__ == "__main__":
    main()

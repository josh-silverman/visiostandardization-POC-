import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from lxml import etree
import subprocess

# 1. Load environment and config
load_dotenv()
connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
source_container_name = "initial-vsdx"
destination_container_name = "visio-files"
specific_vsdx_file = "Initial-SLM-DMVOSCI.vsdx"
output_directory = "output_xml"
os.makedirs(output_directory, exist_ok=True)

local_vsdx_path = os.path.join(output_directory, specific_vsdx_file)
local_svg_path = os.path.join(output_directory, "converted.svg")
cleaned_svg_path = os.path.join(output_directory, "cleaned.svg")
prepped_vsdx_filename = "Prepped-SLM-DMVOSCI.vsdx"
prepped_vsdx_path = os.path.join(output_directory, prepped_vsdx_filename)
group_id_to_remove = "group58-238"

# 2. Download VSDX from Azure
def download_vsdx():
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=source_container_name, blob=specific_vsdx_file)
    with open(local_vsdx_path, "wb") as f:
        f.write(blob_client.download_blob().readall())
    print(f"Downloaded {specific_vsdx_file}")

# 3. Convert VSDX to SVG (requires LibreOffice installed and in PATH)
def convert_vsdx_to_svg():
    subprocess.run([
        "soffice",
        "--headless",
        "--convert-to", "svg",
        local_vsdx_path,
        "--outdir", output_directory
    ], check=True)
    # Find the SVG produced
    svg_candidates = [fname for fname in os.listdir(output_directory) if fname.lower().endswith(".svg")]
    if not svg_candidates:
        raise Exception("SVG file not found after conversion.")
    # If there's more than one, pick the first; adapt if needed
    svg_path = os.path.join(output_directory, svg_candidates[0])
    os.rename(svg_path, local_svg_path)
    print(f"SVG output: {local_svg_path}")

# 4. Remove group from SVG
def remove_group_from_svg():
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(local_svg_path, parser)
    root = tree.getroot()
    for elem in root.xpath(f'.//*[@id="{group_id_to_remove}"]'):
        parent = elem.getparent()
        if parent is not None:
            parent.remove(elem)
    tree.write(cleaned_svg_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    print(f"Removed group '{group_id_to_remove}'. Cleaned SVG saved: {cleaned_svg_path}")

# 5. (Placeholder) Convert cleaned SVG back to VSDX
def convert_svg_to_vsdx():
    # This is a placeholder! You need to implement or automate this step.
    # For now, raise an error to remind the user.
    print("SVG to VSDX conversion not supported directly in open source.")
    print("Please convert cleaned.svg to Prepped-SLM-DMVOSCI.vsdx manually or with a commercial tool/API.")
    raise NotImplementedError("SVG to VSDX conversion not implemented.")

# 6. Upload the prepped VSDX to destination container
def upload_to_blob_vsdx():
    if not os.path.exists(prepped_vsdx_path):
        raise FileNotFoundError(f"{prepped_vsdx_path} not found. You must create this file before uploading.")
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=destination_container_name, blob=prepped_vsdx_filename)
    with open(prepped_vsdx_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    print(f"Uploaded '{prepped_vsdx_filename}' to container '{destination_container_name}'.")

if __name__ == "__main__":
    download_vsdx()
    convert_vsdx_to_svg()
    remove_group_from_svg()
    # --- SVG to VSDX step ---
    try:
        convert_svg_to_vsdx()  # Implement this step as needed!
    except NotImplementedError:
        print("SVG to VSDX step not implemented. Please complete this step before uploading.")
    # --- Upload if VSDX exists ---
    if os.path.exists(prepped_vsdx_path):
        upload_to_blob_vsdx()
        print("Pipeline complete.")
    else:
        print(f"Prepped VSDX '{prepped_vsdx_filename}' does not exist. Upload skipped.")

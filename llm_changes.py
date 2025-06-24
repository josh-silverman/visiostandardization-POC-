import os
import zipfile
import tempfile
import requests
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Load sensitive config from .env
load_dotenv()
STORAGE_CONNECTION_STRING = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_KEY = os.environ["AZURE_OPENAI_API_KEY"]

# Set container and blob names here (not in .env)
INPUT_CONTAINER = "initial-vsdx"
OUTPUT_CONTAINER = "result-vsdx"
BLOB_NAME = "Test-image.vsdx"
OUTPUT_BLOB_NAME = "updated_test-image.vsdx"

def download_blob_to_file(container, blob_name, output_path):
    blob_service = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    blob_client = blob_service.get_blob_client(container=container, blob=blob_name)
    with open(output_path, "wb") as file:
        file.write(blob_client.download_blob().readall())

def upload_file_to_blob(container, blob_name, file_path):
    blob_service = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    blob_client = blob_service.get_blob_client(container=container, blob=blob_name)
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

def extract_xml_from_vsdx(vsdx_path, xml_relative_path):
    with zipfile.ZipFile(vsdx_path, 'r') as zip_ref:
        with zip_ref.open(xml_relative_path) as f:
            return f.read().decode('utf-8')

def replace_xml_in_vsdx(vsdx_path, xml_relative_path, new_xml, output_path):
    with zipfile.ZipFile(vsdx_path, 'r') as zin:
        with zipfile.ZipFile(output_path, 'w') as zout:
            for item in zin.infolist():
                if item.filename != xml_relative_path:
                    zout.writestr(item, zin.read(item.filename))
                else:
                    zout.writestr(item, new_xml.encode('utf-8'))

def call_azure_gpt(xml_content, instructions):
    prompt = (
        "Here is a Visio XML page. "
        "Replace all shapes with squares (use appropriate Visio XML for a square shape). "
        "Preserve the rest of the document structure. "
        "Return only the complete updated XML for the page.\n\n"
        f"{xml_content}\n\n"
        f"Instructions: {instructions}\n"
    )
    headers = {
        "api-key": AZURE_OPENAI_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "messages": [
            {"role": "system", "content": "You are an expert Visio XML editor."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 4096,
        "temperature": 0,
        "top_p": 1
    }
    resp = requests.post(AZURE_OPENAI_ENDPOINT, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def main():
    with tempfile.TemporaryDirectory() as tmpdir:
        vsdx_path = os.path.join(tmpdir, "input.vsdx")
        # 1. Download input .vsdx
        print("Downloading input .vsdx from Azure Blob Storage...")
        download_blob_to_file(INPUT_CONTAINER, BLOB_NAME, vsdx_path)

        # 2. Locate Visio page XML(s)
        with zipfile.ZipFile(vsdx_path, 'r') as z:
            page_files = [f for f in z.namelist() if f.startswith("visio/pages/") and f.endswith(".xml")]
            if not page_files:
                raise Exception("No Visio page XML files found in the .vsdx!")
            page_xml_path = page_files[0]  # Only the first page for now

        # 3. Extract page XML
        print(f"Extracting {page_xml_path} from .vsdx...")
        page_xml = extract_xml_from_vsdx(vsdx_path, page_xml_path)

        # 4. Call Azure OpenAI to update shapes to squares
        print("Sending XML to Azure OpenAI for transformation...")
        new_page_xml = call_azure_gpt(
            page_xml,
            "Replace all shapes with squares. Tell the user which file is being changed and the steps"
        )

        # 5. Replace XML in the vsdx archive
        vsdx_updated_path = os.path.join(tmpdir, "output.vsdx")
        print("Replacing page XML in .vsdx archive...")
        replace_xml_in_vsdx(vsdx_path, page_xml_path, new_page_xml, vsdx_updated_path)

        # 6. Upload the updated vsdx to output blob container
        print("Uploading updated .vsdx to Azure Blob Storage...")
        upload_file_to_blob(OUTPUT_CONTAINER, OUTPUT_BLOB_NAME, vsdx_updated_path)

        print(f"Updated .vsdx uploaded as {OUTPUT_BLOB_NAME} to {OUTPUT_CONTAINER}.")

if __name__ == "__main__":
    main()

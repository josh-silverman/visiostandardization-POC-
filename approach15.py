import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import openai

# Load .env
load_dotenv()

# Check required variables
required_vars = [
    "AZURE_STORAGE_CONNECTION_STRING",
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_API_BASE",
    "AZURE_OPENAI_DEPLOYMENT",
    "AZURE_OPENAI_API_VERSION"
]
for var in required_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")

# Assign variables
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_BASE = os.getenv("AZURE_OPENAI_API_BASE")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

CONTAINER_NAME = "svg-files"
SVG1_BLOB_NAME = "DP-Image-SVG.svg"
SVG2_BLOB_NAME = "footer.svg"
OUTPUT_BLOB_NAME = "combined-svg.svg"
LOCAL_RAW_OUTPUT_FILE = "combined_svg_llm_output.txt"

# Set up OpenAI for Azure
openai.api_type = "azure"
openai.api_key = AZURE_OPENAI_API_KEY
openai.api_base = AZURE_OPENAI_API_BASE
openai.api_version = AZURE_OPENAI_API_VERSION

def download_blob_to_string(container_name, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    return blob_client.download_blob().readall().decode("utf-8")

def upload_string_to_blob(container_name, blob_name, content):
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(content, overwrite=True)
    print(f"Uploaded blob: {blob_name}")

def combine_svgs_with_llm(svg1: str, svg2: str) -> str:
    prompt = (
        '''
Change the color of all text to bold dark blue and thicken lines
'''
    )
    response = openai.ChatCompletion.create(
        engine=AZURE_OPENAI_DEPLOYMENT,  # For Azure, use 'engine' (deployment name), not 'model'
        messages=[
            {"role": "system", "content": "You are an expert SVG editor."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=2048
    )
    return response["choices"][0]["message"]["content"]

def main():
    print("Downloading SVG files...")
    svg1 = download_blob_to_string(CONTAINER_NAME, SVG1_BLOB_NAME)
    svg2 = download_blob_to_string(CONTAINER_NAME, SVG2_BLOB_NAME)

    print("Combining SVGs using LLM...")
    combined_svg = combine_svgs_with_llm(svg1, svg2)

    with open(LOCAL_RAW_OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(combined_svg)
    print(f"Raw LLM output saved to {LOCAL_RAW_OUTPUT_FILE}")

    upload_string_to_blob(CONTAINER_NAME, OUTPUT_BLOB_NAME, combined_svg)
    print("Done.")

if __name__ == "__main__":
    main()

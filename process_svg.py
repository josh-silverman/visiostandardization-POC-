# from dotenv import load_dotenv
# load_dotenv()
# import os
# from azure.storage.blob import BlobServiceClient
# import openai


# # Config
# openai.api_key = os.environ['AZURE_OPENAI_API_KEY']
# AZURE_CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']
# SVG_BLOB_NAME = 'Test-image.svg'
# SRC_CONTAINER = 'svg-files'
# DST_CONTAINER = 'result-vsdx'
# OUTPUT_BLOB_NAME = 'output.svg'

# # Download SVG from Azure Blob Storage
# blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
# src_container = blob_service.get_container_client(SRC_CONTAINER)
# svg_bytes = src_container.download_blob(SVG_BLOB_NAME).readall()
# svg_text = svg_bytes.decode('utf-8')

# # Prompt the AI to rewrite the SVG code
# prompt = (
#     "Here is an SVG file:\n\n"
#     f"{svg_text}\n\n"
#     "Please rewrite the SVG so that all shapes (circles, ellipses, rectangles, polygons, and paths) are replaced by squares of the same approximate size and position. "
#     "Do not make any other changes to the diagram and replicate it entirely aside from replacing all the shapes"
#     "Return only valid SVG code."
# )

# response = openai.ChatCompletion.create(
#     model="gpt-4o",  # or any model you have access to
#     messages=[
#         {"role": "user", "content": prompt}
#     ],
#     temperature=0.0,
#     max_tokens=4000
# )

# ai_svg = response['choices'][0]['message']['content']

# # Upload the AI-modified SVG to Azure Blob Storage
# dst_container = blob_service.get_container_client(DST_CONTAINER)
# dst_container.upload_blob(OUTPUT_BLOB_NAME, ai_svg.encode('utf-8'), overwrite=True)

# print(f"AI-updated SVG uploaded to '{DST_CONTAINER}/{OUTPUT_BLOB_NAME}'.")



# from dotenv import load_dotenv
# import os
# import openai

# # Load environment variables from .env
# load_dotenv()
# AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
# AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
# AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")  # Your GPT-4o deployment name

# # Configure OpenAI client for Azure
# openai.api_type = "azure"
# openai.api_base = AZURE_OPENAI_ENDPOINT
# openai.api_version = "2024-02-15-preview"
# openai.api_key = AZURE_OPENAI_API_KEY

# # Sample SVG transformation prompt
# with open("Test-image.svg", "r", encoding="utf-8") as f:
#     svg_text = f.read()

# prompt = (
#     "Here is an SVG file:\n\n"
#     f"{svg_text}\n\n"
#     "Please rewrite the SVG so that all shapes (circles, ellipses, rectangles, polygons, and paths) "
#     "are replaced by squares of the same approximate size and position. Return only valid SVG code."
# )

# response = openai.ChatCompletion.create(
#     engine=AZURE_OPENAI_DEPLOYMENT,  # Use 'engine' for Azure, not 'model'
#     messages=[
#         {"role": "user", "content": prompt}
#     ],
#     temperature=0.0,
#     max_tokens=4000
# )

# ai_svg = response['choices'][0]['message']['content']

# # Optional: Extract <svg>...</svg> block, if necessary
# import re
# svg_match = re.search(r'(<svg.*?</svg>)', ai_svg, re.DOTALL | re.IGNORECASE)
# if svg_match:
#     ai_svg = svg_match.group(1)

# with open("output.svg", "w", encoding="utf-8") as f:
#     f.write(ai_svg)

# print("AI-updated SVG saved to output.svg")




from dotenv import load_dotenv
import os
import openai
import re
from azure.storage.blob import BlobServiceClient

# --- Load environment variables ---
load_dotenv()
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
BLOB_CONTAINER_NAME = "svg-files"

# --- Configure OpenAI for Azure ---
openai.api_type = "azure"
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = "2024-02-15-preview"
openai.api_key = AZURE_OPENAI_API_KEY

# --- Read input SVG filename ---
input_svg_path = "Test-image.svg"
with open(input_svg_path, "r", encoding="utf-8") as f:
    svg_text = f.read()

# --- Prepare prompt ---
prompt = (
    "Here is an SVG file:\n\n"
    f"{svg_text}\n\n"
    "Please rewrite the SVG so that all shapes (circles, ellipses, rectangles, polygons, and paths) are replaced by squares of the same approximate size and position. "
    "Keep all connectors, arrows, and lines exactly as they are in the original diagram, preserving their positions and connections. "
    "Return only valid SVG code."
)

# --- Call Azure OpenAI ---
response = openai.ChatCompletion.create(
    engine=AZURE_OPENAI_DEPLOYMENT,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.0,
    max_tokens=4000
)
ai_svg = response['choices'][0]['message']['content']

# --- Extract SVG code (if necessary) ---
svg_match = re.search(r'(<svg.*?</svg>)', ai_svg, re.DOTALL | re.IGNORECASE)
if svg_match:
    ai_svg = svg_match.group(1)

# --- Prepare output filename ---
input_svg_name = os.path.basename(input_svg_path)
output_svg_name = f"updated-{input_svg_name}"

# --- Save locally (optional) ---
with open(output_svg_name, "w", encoding="utf-8") as f:
    f.write(ai_svg)
print(f"AI-updated SVG saved locally as {output_svg_name}")

# --- Upload to Azure Blob Storage ---
try:
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)
    # Create the container if it doesn't exist
    try:
        container_client.create_container()
    except Exception:
        pass  # Container may already exist

    blob_client = container_client.get_blob_client(output_svg_name)
    blob_client.upload_blob(ai_svg, overwrite=True)
    print(f"SVG uploaded to Azure Blob Storage container '{BLOB_CONTAINER_NAME}' as '{output_svg_name}'")
except Exception as e:
    print("Failed to upload SVG to Azure Blob Storage:", e)

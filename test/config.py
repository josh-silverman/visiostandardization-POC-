# config.py
import os
from dotenv import load_dotenv

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
TEMPLATE_VSTX_PATH = os.getenv("TEMPLATE_VSTX_PATH", "template.vstx")
BLOB_CONTAINER_RAW = os.getenv("BLOB_CONTAINER_RAW", "visio-files")
BLOB_CONTAINER_STD = os.getenv("BLOB_CONTAINER_STD", "standardized-visio")
GPT_ENGINE_NAME = os.getenv("GPT_ENGINE_NAME", "gpt-4o")
TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Example template schema (customize as needed)
TEMPLATE_SCHEMA = {
    "shapes": {
        "rectangle": {"color": "blue", "font": "Arial", "size": 10},
        "ellipse": {"color": "green", "font": "Arial", "size": 10}
    },
    "connectors": {
        "type": "straight", "color": "black"
    },
    "layout": "vertical"
}

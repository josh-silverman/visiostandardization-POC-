import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    config = {
        "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
        "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION"),
        "AZURE_OPENAI_DEPLOYMENT": os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        "AZURE_STORAGE_CONNECTION_STRING": os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
        "BLOB_CONTAINER": os.getenv("BLOB_CONTAINER", "visio-files"),
        "STANDARDIZED_CONTAINER": os.getenv("STANDARDIZED_CONTAINER", "standardized-visio"),
    }
    return config

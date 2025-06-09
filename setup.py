import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access variables using os.getenv
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_storage_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

print("Azure OpenAI Endpoint:", azure_openai_endpoint)
print("Azure OpenAI API Key:", azure_openai_api_key)
print("Azure Storage Connection String:", azure_storage_connection_string)

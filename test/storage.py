# storage.py
import os
from azure.storage.blob import BlobServiceClient
from config import AZURE_STORAGE_CONNECTION_STRING, TEMP_DIR

blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

def get_container_client(container_name):
    return blob_service_client.get_container_client(container_name)

def download_blob(blob_client, dest_path):
    with open(dest_path, "wb") as file:
        file.write(blob_client.download_blob().readall())

def upload_blob(container_client, src_path, dest_name):
    with open(src_path, "rb") as data:
        container_client.upload_blob(name=dest_name, data=data, overwrite=True)

def list_blobs(container_client, suffix=None):
    return [b for b in container_client.list_blobs() if not suffix or b.name.endswith(suffix)]

import os
from azure.storage.blob import BlobServiceClient

def get_blob_service_client(connection_string):
    return BlobServiceClient.from_connection_string(connection_string)

def upload_file_to_blob(blob_service_client, container, local_path, blob_name=None):
    if blob_name is None:
        blob_name = os.path.basename(local_path)
    container_client = blob_service_client.get_container_client(container)
    with open(local_path, "rb") as data:
        container_client.upload_blob(name=blob_name, data=data, overwrite=True)
    return blob_name

def download_blob_to_file(blob_service_client, container, blob_name, local_path):
    container_client = blob_service_client.get_container_client(container)
    blob_client = container_client.get_blob_client(blob_name)
    with open(local_path, "wb") as f:
        f.write(blob_client.download_blob().readall())
    return local_path

def list_blobs(blob_service_client, container, suffix=None):
    container_client = blob_service_client.get_container_client(container)
    blobs = container_client.list_blobs()
    if suffix:
        return [b.name for b in blobs if b.name.endswith(suffix)]
    else:
        return [b.name for b in blobs]


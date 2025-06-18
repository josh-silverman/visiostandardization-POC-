import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

# Specify containers and file names
source_container = "initial-vsdx"
dest_container = "zipped-files"
vsdx_file_name = "SDCDMZ Basic Architecture.vsdx"  # <-- Change this to your file name
output_zip_name = vsdx_file_name.rsplit('.', 1)[0] + ".zip"

def main():
    # Create blob service client
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Download the VSDX file
    blob_client = blob_service_client.get_blob_client(container=source_container, blob=vsdx_file_name)
    print(f"Downloading {vsdx_file_name} from container {source_container} ...")
    with open(output_zip_name, "wb") as f:
        f.write(blob_client.download_blob().readall())
    print(f"Saved as {output_zip_name}")

    # Upload the ZIP file to the destination container
    dest_blob_client = blob_service_client.get_blob_client(container=dest_container, blob=output_zip_name)
    print(f"Uploading {output_zip_name} to container {dest_container} ...")
    with open(output_zip_name, "rb") as data:
        dest_blob_client.upload_blob(data, overwrite=True)
    print(f"Uploaded {output_zip_name} to {dest_container}")

if __name__ == "__main__":
    main()
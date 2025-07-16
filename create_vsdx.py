# import os
# import zipfile

# def zipdir(path, ziph):
#     # Zip the directory, keeping the folder structure
#     for root, dirs, files in os.walk(path):
#         for file in files:
#             full_path = os.path.join(root, file)
#             arcname = os.path.relpath(full_path, path)
#             ziph.write(full_path, arcname)

# def run_create_vsdx():
#     output_folder = 'output_xml'
#     output_vsdx = 'output.vsdx'
#     with zipfile.ZipFile(output_vsdx, 'w', zipfile.ZIP_DEFLATED) as zipf:
#         zipdir(output_folder, zipf)
#     print(f"Created {output_vsdx}")

# if __name__ == "__main__":
#     run_create_vsdx()




import os
import zipfile
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

def zipdir(path, ziph):
    # Zip the directory, keeping the folder structure
    for root, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, path)
            ziph.write(full_path, arcname)

def upload_to_blob_storage(file_path, blob_name, container_name):
    # Load connection string from environment
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    if not connect_str:
        raise ValueError("AZURE_STORAGE_CONNECTION_STRING not set in environment variables")

    # Create a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Get the container client for the specified container
    container_client = blob_service_client.get_container_client(container_name)

    # Upload the file
    blob_client = container_client.get_blob_client(blob_name)
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    print(f"Uploaded {file_path} to Azure Blob Storage as {blob_name}")

def run_create_vsdx():
    # Load environment variables from a .env file
    load_dotenv()

    output_folder = 'output_xml'
    local_vsdx = 'output.vsdx'
    renamed_vsdx = 'automated-output.vsdx'

    # Create the vsdx file
    with zipfile.ZipFile(local_vsdx, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(output_folder, zipf)
    print(f"Created {local_vsdx}")

    # Rename the local file
    os.rename(local_vsdx, renamed_vsdx)
    print(f"Renamed file to {renamed_vsdx}")

    # Upload to Azure Blob Storage
    upload_to_blob_storage(renamed_vsdx, 'automated-output.vsdx', 'result-vsdx')

if __name__ == "__main__":
    run_create_vsdx()

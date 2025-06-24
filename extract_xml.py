import os
import zipfile
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the connection string from environment variables
connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
source_container_name = "visio-files"
destination_container_name = "xml-container"  # Change this to your target container

# Specify the exact VSDX file you want to process
specific_vsdx_file = "sample process.vsdx"  # <-- Change to your exact file name

# Local directory to save the extracted files
output_directory = "output_xml"
os.makedirs(output_directory, exist_ok=True)

# Function to extract ALL files from VSDX, preserving structure
def extract_all_from_vsdx(vsdx_path, output_dir):
    with zipfile.ZipFile(vsdx_path, 'r') as vsdx_zip:
        vsdx_zip.extractall(output_dir)

def upload_files_to_azure(blob_service_client, local_dir, container_name):
    container_client = blob_service_client.get_container_client(container_name)
    
    # Ensure the destination container exists
    try:
        container_client.create_container()
    except Exception as e:
        print(f"Container {container_name} already exists or couldn't be created: {e}")

    for root, dirs, files in os.walk(local_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            # Preserve folder structure in blob name
            rel_path = os.path.relpath(file_path, local_dir).replace("\\", "/")
            blob_client = container_client.get_blob_client(rel_path)
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
                print(f"Uploaded {rel_path} to {container_name}")

def main():
    # Initialize a BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_client = blob_service_client.get_container_client(source_container_name)

    blob_client = blob_service_client.get_blob_client(
        container=source_container_name, 
        blob=specific_vsdx_file
    )
    download_file_path = os.path.join(output_directory, specific_vsdx_file)
    
    # Download the specified VSDX file
    print(f"Downloading {specific_vsdx_file} from {source_container_name} ...")
    with open(download_file_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())
    print(f"Downloaded {specific_vsdx_file} to {download_file_path}")

    # Extract ALL contents from VSDX (not just XML files)
    extract_all_from_vsdx(download_file_path, output_directory)
    print(f"Extracted all files from {specific_vsdx_file}")

    # Upload extracted files to the destination container
    upload_files_to_azure(blob_service_client, output_directory, destination_container_name)

if __name__ == "__main__":
    main()

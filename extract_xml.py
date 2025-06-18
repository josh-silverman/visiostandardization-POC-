# import os
# import zipfile
# from azure.storage.blob import BlobServiceClient
# from dotenv import load_dotenv

# # Load environment variables from the .env file
# load_dotenv()

# # Retrieve the connection string from environment variables
# connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
# source_container_name = "visio-files"
# destination_container_name = "xml-container"  # Change this to your target container

# # Local directory to save the XML files
# output_directory = "output_xml"
# os.makedirs(output_directory, exist_ok=True)

# # Function to extract XML from VSDX
# def extract_xml_from_vsdx(vsdx_path, output_dir):
#     with zipfile.ZipFile(vsdx_path, 'r') as vsdx_zip:
#         for file_info in vsdx_zip.infolist():
#             if file_info.filename.endswith('.xml'):
#                 vsdx_zip.extract(file_info, output_dir)

# def upload_files_to_azure(blob_service_client, local_dir, container_name):
#     container_client = blob_service_client.get_container_client(container_name)
    
#     # Ensure the destination container exists
#     try:
#         container_client.create_container()
#     except Exception as e:
#         print(f"Container {container_name} already exists or couldn't be created: {e}")

#     for root, dirs, files in os.walk(local_dir):
#         for file_name in files:
#             file_path = os.path.join(root, file_name)
#             blob_client = container_client.get_blob_client(file_name)
#             with open(file_path, "rb") as data:
#                 blob_client.upload_blob(data, overwrite=True)
#                 print(f"Uploaded {file_name} to {container_name}")

# def main():
#     # Initialize a BlobServiceClient
#     blob_service_client = BlobServiceClient.from_connection_string(connect_str)
#     container_client = blob_service_client.get_container_client(source_container_name)

#     # List all blobs in the source container
#     blobs = container_client.list_blobs()

#     for blob in blobs:
#         blob_name = blob.name
#         if blob_name.endswith('.vsdx'):
#             # Download the VSDX file
#             blob_client = blob_service_client.get_blob_client(container=source_container_name, blob=blob_name)
#             download_file_path = os.path.join(output_directory, blob_name)
            
#             with open(download_file_path, "wb") as download_file:
#                 download_file.write(blob_client.download_blob().readall())

#             # Extract XML content
#             extract_xml_from_vsdx(download_file_path, output_directory)
#             print(f"Extracted XML files from {blob_name}")

#     # Upload extracted XML files to the destination container
#     upload_files_to_azure(blob_service_client, output_directory, destination_container_name)

# if __name__ == "__main__":
#     main()


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
specific_vsdx_file = "SDCDMZ Basic Architecture.vsdx"  # <-- Change to your exact file name

# Local directory to save the XML files
output_directory = "output_xml"
os.makedirs(output_directory, exist_ok=True)

# Function to extract XML from VSDX
def extract_xml_from_vsdx(vsdx_path, output_dir):
    with zipfile.ZipFile(vsdx_path, 'r') as vsdx_zip:
        for file_info in vsdx_zip.infolist():
            if file_info.filename.endswith('.xml'):
                vsdx_zip.extract(file_info, output_dir)

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
            blob_client = container_client.get_blob_client(file_name)
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
                print(f"Uploaded {file_name} to {container_name}")

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

    # Extract XML content
    extract_xml_from_vsdx(download_file_path, output_directory)
    print(f"Extracted XML files from {specific_vsdx_file}")

    # Upload extracted XML files to the destination container
    upload_files_to_azure(blob_service_client, output_directory, destination_container_name)

if __name__ == "__main__":
    main()

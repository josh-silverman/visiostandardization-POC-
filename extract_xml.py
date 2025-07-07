import os
import zipfile
import logging
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

def extract_all_from_vsdx(vsdx_path, output_dir):
    """Extract ALL files from a VSDX file, preserving folder structure."""
    with zipfile.ZipFile(vsdx_path, 'r') as vsdx_zip:
        vsdx_zip.extractall(output_dir)
    logging.info(f"Extracted all files from {vsdx_path}")

def upload_files_to_azure(blob_service_client, local_dir, container_name):
    """Upload all files in local_dir (recursively) to Azure Blob Storage container."""
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container()
        logging.info(f"Created container: {container_name}")
    except Exception as e:
        # Only log warning if container already exists
        if "ContainerAlreadyExists" in str(e):
            logging.info(f"Container {container_name} already exists.")
        else:
            logging.warning(f"Could not create container: {e}")

    for root, _, files in os.walk(local_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            # Skip the original VSDX file
            if file_name.lower().endswith('.vsdx'):
                continue
            rel_path = os.path.relpath(file_path, local_dir).replace("\\", "/")
            blob_client = container_client.get_blob_client(rel_path)
            try:
                with open(file_path, "rb") as data:
                    blob_client.upload_blob(data, overwrite=True)
                logging.info(f"Uploaded {rel_path} to {container_name}")
            except Exception as e:
                logging.error(f"Failed to upload {rel_path}: {e}")

def main():
    setup_logging()
    load_dotenv()
    connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    source_container_name = "visio-files"
    destination_container_name = "xml-container"
    specific_vsdx_file = "SLM-DMVOSCI.vsdx"
    output_directory = "output_xml"
    os.makedirs(output_directory, exist_ok=True)

    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(
        container=source_container_name,
        blob=specific_vsdx_file
    )
    download_file_path = os.path.join(output_directory, specific_vsdx_file)

    # Download VSDX file
    logging.info(f"Downloading {specific_vsdx_file} from {source_container_name} ...")
    with open(download_file_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())
    logging.info(f"Downloaded {specific_vsdx_file} to {download_file_path}")

    # Extract contents
    extract_all_from_vsdx(download_file_path, output_directory)

    # Optionally remove the VSDX to save space
    try:
        os.remove(download_file_path)
        logging.info(f"Removed local copy of {download_file_path}")
    except Exception as e:
        logging.warning(f"Could not remove {download_file_path}: {e}")

    # Upload extracted files
    upload_files_to_azure(blob_service_client, output_directory, destination_container_name)

if __name__ == "__main__":
    main()
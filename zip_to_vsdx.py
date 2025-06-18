# import os
# import zipfile
# from azure.storage.blob import BlobServiceClient
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # --- CONFIGURE THESE ---
# STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
# CONTAINER_NAME = "zipped-process"
# BLOB_NAME = "Drawing 5.zip"
# LOCAL_ZIP = "Drawing_5.zip"
# UNZIP_DIR = "unzipped"
# VSDX_FILE = "Drawing5.vsdx"
# UPLOAD_VSDX = True  # set to False if you don't want to upload back
# # -----------------------

# def download_blob(blob_service_client, container, blob_name, download_path):
#     print(f"Downloading {blob_name} to {download_path} ...")
#     blob_client = blob_service_client.get_blob_client(container=container, blob=blob_name)
#     with open(download_path, "wb") as f:
#         f.write(blob_client.download_blob().readall())
#     print("Downloaded.")

# def unzip_file(zip_path, extract_dir):
#     print(f"Unzipping {zip_path} to {extract_dir} ...")
#     if not os.path.exists(extract_dir):
#         os.makedirs(extract_dir)
#     with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#         zip_ref.extractall(extract_dir)
#     print("Unzipped.")

# def zip_as_vsdx(src_dir, vsdx_path):
#     print(f"Zipping {src_dir} as {vsdx_path} ...")
#     with zipfile.ZipFile(vsdx_path, 'w', zipfile.ZIP_DEFLATED) as vsdx_zip:
#         for foldername, subfolders, filenames in os.walk(src_dir):
#             for filename in filenames:
#                 file_path = os.path.join(foldername, filename)
#                 arcname = os.path.relpath(file_path, src_dir)
#                 vsdx_zip.write(file_path, arcname)
#     print("Packaged as .vsdx.")

# def upload_blob(blob_service_client, container, blob_name, file_path):
#     print(f"Uploading {file_path} as {blob_name} ...")
#     blob_client = blob_service_client.get_blob_client(container=container, blob=blob_name)
#     with open(file_path, "rb") as data:
#         blob_client.upload_blob(data, overwrite=True)
#     print("Uploaded.")

# def main():
#     if not STORAGE_CONNECTION_STRING:
#         raise Exception("AZURE_STORAGE_CONNECTION_STRING not found in environment variables.")

#     blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)

#     # Step 1: Download Drawing 5.zip
#     download_blob(blob_service_client, CONTAINER_NAME, BLOB_NAME, LOCAL_ZIP)

#     # Step 2: Unzip
#     unzip_file(LOCAL_ZIP, UNZIP_DIR)

#     # Step 3: Re-zip as .vsdx
#     zip_as_vsdx(UNZIP_DIR, VSDX_FILE)

#     # Step 4: (Optional) Upload .vsdx back
#     if UPLOAD_VSDX:
#         upload_blob(blob_service_client, CONTAINER_NAME, VSDX_FILE, VSDX_FILE)

#     print("All done. Local .vsdx file is at:", VSDX_FILE)

# if __name__ == "__main__":
#     main()


import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

# Specify containers and file names
source_container = "zipped-files"
dest_container = "result-vsdx"
zip_file_name = "SDCDMZ Basic Architecture.zip"  # <-- Change this to your file name

# Compute output name: updated-{filename}.vsdx
base_name = os.path.splitext(os.path.basename(zip_file_name))[0]
output_vsdx_name = f"updated-{base_name}.vsdx"

def main():
    # Create blob service client
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Download the ZIP file
    blob_client = blob_service_client.get_blob_client(container=source_container, blob=zip_file_name)
    print(f"Downloading {zip_file_name} from container {source_container} ...")
    with open(output_vsdx_name, "wb") as f:
        f.write(blob_client.download_blob().readall())
    print(f"Saved as {output_vsdx_name}")

    # Upload the VSDX file to the destination container
    dest_blob_client = blob_service_client.get_blob_client(container=dest_container, blob=output_vsdx_name)
    print(f"Uploading {output_vsdx_name} to container {dest_container} ...")
    with open(output_vsdx_name, "rb") as data:
        dest_blob_client.upload_blob(data, overwrite=True)
    print(f"Uploaded {output_vsdx_name} to {dest_container}")

if __name__ == "__main__":
    main()

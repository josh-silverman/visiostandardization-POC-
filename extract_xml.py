# import os
# import xml.etree.ElementTree as ET

# def parse_pages_xml(pages_dir):
#     """Parse shapes, text, connectors from all XMLs in pages_dir."""
#     diagrams = []
#     for file in os.listdir(pages_dir):
#         if file.endswith(".xml"):
#             path = os.path.join(pages_dir, file)
#             tree = ET.parse(path)
#             root = tree.getroot()
#             ns = {'visio': 'http://schemas.microsoft.com/office/visio/2012/main'}
#             shapes = []
#             connectors = []
#             for shape in root.findall(".//visio:Shape", ns):
#                 shape_id = shape.get('ID')
#                 shape_type = shape.get('Type', 'unknown')
#                 text = ''
#                 text_elem = shape.find(".//visio:Text", ns)
#                 if text_elem is not None and text_elem.text:
#                     text = text_elem.text.strip()
#                 shapes.append({
#                     "id": shape_id,
#                     "type": shape_type,
#                     "text": text
#                 })
#             # Connector parsing logic (simplified, extend as needed)
#             for connect in root.findall(".//visio:Connect", ns):
#                 from_id = connect.get('FromSheet')
#                 to_id = connect.get('ToSheet')
#                 connectors.append({
#                     "from": from_id,
#                     "to": to_id
#                 })
#             diagrams.append({
#                 "page": file,
#                 "shapes": shapes,
#                 "connectors": connectors
#             })
#     return diagrams

# import zipfile
# import os
# from pathlib import Path
# # Get the Desktop path
# desktop = Path.home() / "Desktop"
# vsdx_path = desktop / "temp folder" / "drawing 5.zip"
# output_path = desktop / "temp folder" / "combined_output.xml"
# # Make sure the file exists
# if not vsdx_path.exists():
#    print(f"File not found: {vsdx_path}")
# else:
#    with zipfile.ZipFile(vsdx_path, 'r') as zip_ref:
#        xml_files = [f for f in zip_ref.namelist() if f.endswith('.xml')]
#        with open(output_path, 'w', encoding='utf-8') as out_file:
#            out_file.write('<VisioCombined>\n')
#            for xml_file in xml_files:
#                out_file.write(f'\n<!-- {xml_file} -->\n')
#                content = zip_ref.read(xml_file).decode('utf-8')
#                out_file.write(content + '\n')
#            out_file.write('</VisioCombined>')
#    print(f"\n✅ Combined XML written to:\n{output_path}")


# import os
# import zipfile
# from azure.storage.blob import BlobServiceClient
# from dotenv import load_dotenv

# # Load environment variables from the .env file
# load_dotenv()

# # Retrieve the connection string from environment variables
# connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
# container_name = "visio-files"

# # Local directory to save the XML files
# output_directory = "output_xml"
# os.makedirs(output_directory, exist_ok=True)

# # Function to extract XML from VSDX
# def extract_xml_from_vsdx(vsdx_path, output_dir):
#     with zipfile.ZipFile(vsdx_path, 'r') as vsdx_zip:
#         for file_info in vsdx_zip.infolist():
#             if file_info.filename.endswith('.xml'):
#                 vsdx_zip.extract(file_info, output_dir)

# def main():
#     # Initialize a BlobServiceClient
#     blob_service_client = BlobServiceClient.from_connection_string(connect_str)
#     container_client = blob_service_client.get_container_client(container_name)

#     # List all blobs in the container
#     blobs = container_client.list_blobs()

#     for blob in blobs:
#         blob_name = blob.name
#         if blob_name.endswith('.vsdx'):
#             # Download the VSDX file
#             blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
#             download_file_path = os.path.join(output_directory, blob_name)
            
#             with open(download_file_path, "wb") as download_file:
#                 download_file.write(blob_client.download_blob().readall())

#             # Extract XML content
#             extract_xml_from_vsdx(download_file_path, output_directory)
#             print(f"Extracted XML files from {blob_name}")

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

    # List all blobs in the source container
    blobs = container_client.list_blobs()

    for blob in blobs:
        blob_name = blob.name
        if blob_name.endswith('.vsdx'):
            # Download the VSDX file
            blob_client = blob_service_client.get_blob_client(container=source_container_name, blob=blob_name)
            download_file_path = os.path.join(output_directory, blob_name)
            
            with open(download_file_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())

            # Extract XML content
            extract_xml_from_vsdx(download_file_path, output_directory)
            print(f"Extracted XML files from {blob_name}")

    # Upload extracted XML files to the destination container
    upload_files_to_azure(blob_service_client, output_directory, destination_container_name)

if __name__ == "__main__":
    main()

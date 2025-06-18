import os
import io
import zipfile
import xml.etree.ElementTree as ET
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

def get_blob_service_client():
    # Load environment variables
    load_dotenv()
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    
    if not connect_str:
        raise ValueError("Azure Storage connection string not found. Please check your .env file.")
    
    return BlobServiceClient.from_connection_string(connect_str)

def download_blob_to_memory(container_name, blob_name):
    blob_service_client = get_blob_service_client()
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    download_stream = blob_client.download_blob()
    return io.BytesIO(download_stream.readall())

def extract_zip_to_memory(zip_bytes):
    extracted_files = {}
    with zipfile.ZipFile(zip_bytes, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            extracted_files[file_name] = zip_ref.read(file_name)
    return extracted_files

def modify_shapes_to_squares(extracted_files):
    for file_name in extracted_files:
        if file_name.startswith('pages/') and file_name.endswith('.xml'):
            xml_content = extracted_files[file_name]
            tree = ET.ElementTree(ET.fromstring(xml_content))
            root = tree.getroot()
            
            for shape in root.iter('Shape'):
                shape.set('Width', '2')
                shape.set('Height', '2')
            
            modified_xml = io.BytesIO()
            tree.write(modified_xml, encoding='utf-8', xml_declaration=True)
            extracted_files[file_name] = modified_xml.getvalue()

def create_zip_from_memory(extracted_files):
    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for file_name, data in extracted_files.items():
            zip_ref.writestr(file_name, data)
    zip_bytes.seek(0)
    return zip_bytes

def upload_blob_from_memory(container_name, blob_name, zip_bytes):
    blob_service_client = get_blob_service_client()
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(zip_bytes, overwrite=True)

def main():
    # Blob info
    zip_blob_name = 'Test-image.zip'
    source_container_name = 'zipped-files'
    destination_container_name = 'result-vsdx'
    modified_blob_name = 'Test-image-modified.vsdx'
    
    # Download the zip file, modify, and upload
    zip_bytes = download_blob_to_memory(source_container_name, zip_blob_name)
    extracted_files = extract_zip_to_memory(zip_bytes)
    modify_shapes_to_squares(extracted_files)
    modified_zip = create_zip_from_memory(extracted_files)
    upload_blob_from_memory(destination_container_name, modified_blob_name, modified_zip)

if __name__ == '__main__':
    main()

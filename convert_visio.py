# import os
# import comtypes.client
# import zipfile

# def visio_to_pngs(visio_file, output_dir):
#     """Converts each page of .vsdx to a PNG in output_dir."""
#     visio = comtypes.client.CreateObject("Visio.Application")
#     visio.Visible = False
#     doc = visio.Documents.Open(visio_file)
#     png_paths = []
#     for i, page in enumerate(doc.Pages):
#         output_path = os.path.join(output_dir, f"page_{i+1}.png")
#         page.Export(output_path)
#         png_paths.append(output_path)
#     doc.Close()
#     visio.Quit()
#     return png_paths

# def extract_vsdx_xml(vsdx_path, extract_dir):
#     """Extracts all XML files from a .vsdx (ZIP) to extract_dir."""
#     with zipfile.ZipFile(vsdx_path, 'r') as zip_ref:
#         zip_ref.extractall(extract_dir)
#     # Returns the path to Pages XML directory
#     return os.path.join(extract_dir, "visio", "pages")






# import os
# import xml.etree.ElementTree as ET
# import matplotlib.pyplot as plt
# import networkx as nx
# from azure.storage.blob import BlobServiceClient
# from io import BytesIO
# from dotenv import load_dotenv

# # Load environment variables from the .env file
# load_dotenv()

# # Retrieve the connection string from environment variables
# connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
# container_name = "xml-container"

# def download_xml_files_from_azure():
#     blob_service_client = BlobServiceClient.from_connection_string(connect_str)
#     container_client = blob_service_client.get_container_client(container_name)
    
#     xml_files = []
#     blobs = container_client.list_blobs()

#     for blob in blobs:
#         blob_name = blob.name
#         if blob_name.endswith('.xml'):
#             blob_client = container_client.get_blob_client(blob_name)
#             xml_content = blob_client.download_blob().readall()
#             xml_files.append((blob_name, xml_content))
    
#     return xml_files

# def parse_diagram_data(xml_files):
#     shapes = []
#     connections = []

#     for file_name, xml_content in xml_files:
#         tree = ET.ElementTree(ET.fromstring(xml_content))
#         root = tree.getroot()
        
#         # Example parsing: Find shapes and connections
#         for shape in root.findall(".//{http://schemas.microsoft.com/office/visio/2012/main}Shape"):
#             shape_id = shape.get('ID')
#             shape_text = shape.find(".//{http://schemas.microsoft.com/office/visio/2012/main}Text")
#             text_value = shape_text.text if shape_text is not None else "No Text"
#             shapes.append((shape_id, text_value))

#         for connect in root.findall(".//{http://schemas.microsoft.com/office/visio/2012/main}Connect"):
#             from_shape = connect.get('FromSheet')
#             to_shape = connect.get('ToSheet')
#             connections.append((from_shape, to_shape))
    
#     return shapes, connections

# def visualize_diagram(shapes, connections):
#     G = nx.DiGraph()

#     # Add nodes with labels
#     for shape_id, text in shapes:
#         G.add_node(shape_id, label=text)

#     # Add edges
#     for from_shape, to_shape in connections:
#         G.add_edge(from_shape, to_shape)

#     # Draw the graph
#     pos = nx.spring_layout(G)
#     labels = nx.get_node_attributes(G, 'label')
#     nx.draw(G, pos, with_labels=True, labels=labels, node_size=3000, node_color='lightblue', font_size=8)
#     plt.show()

# def main():
#     xml_files = download_xml_files_from_azure()
#     shapes, connections = parse_diagram_data(xml_files)
#     visualize_diagram(shapes, connections)

# if __name__ == "__main__":
#     main()


import os
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import networkx as nx
from azure.storage.blob import BlobServiceClient
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the connection string from environment variables
connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
container_name = "xml-container"

def download_xml_files_from_azure():
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_client = blob_service_client.get_container_client(container_name)
    
    xml_files = []
    blobs = container_client.list_blobs()

    for blob in blobs:
        blob_name = blob.name
        if blob_name.endswith('.xml'):
            blob_client = container_client.get_blob_client(blob_name)
            xml_content = blob_client.download_blob().readall()
            xml_files.append((blob_name, xml_content))
    
    return xml_files

def parse_diagram_data(xml_files):
    shapes = []
    connections = []

    for file_name, xml_content in xml_files:
        tree = ET.ElementTree(ET.fromstring(xml_content))
        root = tree.getroot()
        
        # Example parsing: Find shapes and connections
        for shape in root.findall(".//{http://schemas.microsoft.com/office/visio/2012/main}Shape"):
            shape_id = shape.get('ID')
            shape_text = shape.find(".//{http://schemas.microsoft.com/office/visio/2012/main}Text")
            text_value = shape_text.text if shape_text is not None else "No Text"
            shapes.append((shape_id, text_value))

        for connect in root.findall(".//{http://schemas.microsoft.com/office/visio/2012/main}Connect"):
            from_shape = connect.get('FromSheet')
            to_shape = connect.get('ToSheet')
            connections.append((from_shape, to_shape))
    
    return shapes, connections

def visualize_diagram(shapes, connections):
    G = nx.DiGraph()

    # Add nodes with labels
    for shape_id, text in shapes:
        G.add_node(shape_id, label=text)

    # Add edges
    for from_shape, to_shape in connections:
        G.add_edge(from_shape, to_shape)

    # Draw the graph
    pos = nx.spring_layout(G)
    labels = nx.get_node_attributes(G, 'label')
    nx.draw(G, pos, with_labels=True, labels=labels, node_size=3000, node_color='lightblue', font_size=8)
    
    # Save to file instead of showing
    plt.savefig('output_diagram.png')
    print("Diagram saved to output_diagram.png")

def main():
    xml_files = download_xml_files_from_azure()
    shapes, connections = parse_diagram_data(xml_files)
    visualize_diagram(shapes, connections)

if __name__ == "__main__":
    main()

    


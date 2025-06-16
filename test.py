import os
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import networkx as nx
from PIL import Image
from azure.storage.blob import BlobServiceClient
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the connection string from environment variables
connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

def download_blob_from_azure(container_name, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    return blob_client.download_blob().readall()

def parse_xml_files(xml_contents):
    shapes = []
    connections = []

    for xml_content in xml_contents:
        tree = ET.ElementTree(ET.fromstring(xml_content))
        root = tree.getroot()

        # Parse shapes and their text
        for shape in root.findall(".//{http://schemas.microsoft.com/office/visio/2012/main}Shape"):
            shape_id = shape.get('ID')
            shape_text = shape.find(".//{http://schemas.microsoft.com/office/visio/2012/main}Text")
            text_value = shape_text.text if shape_text is not None else "No Text"
            shapes.append((shape_id, text_value))

        # Parse connections between shapes
        for connect in root.findall(".//{http://schemas.microsoft.com/office/visio/2012/main}Connect"):
            from_shape = connect.get('FromSheet')
            to_shape = connect.get('ToSheet')
            connections.append((from_shape, to_shape))

    return shapes, connections

def visualize_diagram(shapes, connections, png_content=None):
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

    # Optionally overlay the PNG image as a background
    if png_content:
        img = Image.open(BytesIO(png_content))
        img.thumbnail((600, 600), Image.LANCZOS)  # Use Image.LANCZOS instead of Image.ANTIALIAS
        plt.imshow(img, extent=[-1, 1, -1, 1], aspect='auto', alpha=0.5, zorder=-1)

    # Save to file instead of showing
    plt.savefig('output_diagram.png')
    print("Diagram saved to output_diagram.png")

def main():
    # Define the Azure Blob Storage containers and files
    xml_container_name = "xml-container"
    xml_blob_names = [
        "app.xml",
        "core.xml",
        "custom.xml", 
        "document.xml",
        "master1.xml",
        "master2.xml",
        "master3.xml",
        "masters.xml",
        "page1.xml",
        "pages.xml",
        "theme1.xml",
         "windows.xml",  # or other relevant pages
        # Add other XML files if necessary
    ]
    png_container_name = "visio-files"
    png_blob_name = "sample-2.png"  # Ensure this name is correctly specified

    # Download XML files
    xml_contents = [download_blob_from_azure(xml_container_name, blob_name) for blob_name in xml_blob_names]

    # Download PNG file
    png_content = download_blob_from_azure(png_container_name, png_blob_name)

    # Parse XML files and visualize the diagram
    shapes, connections = parse_xml_files(xml_contents)
    visualize_diagram(shapes, connections, png_content)

if __name__ == "__main__":
    main()

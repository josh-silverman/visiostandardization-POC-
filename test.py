# import os
# import xml.etree.ElementTree as ET
# import matplotlib.pyplot as plt
# import networkx as nx
# from PIL import Image
# from azure.storage.blob import BlobServiceClient
# from io import BytesIO
# from dotenv import load_dotenv

# # Load environment variables from the .env file
# load_dotenv()

# # Retrieve the connection string from environment variables
# connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

# def download_blob_from_azure(container_name, blob_name):
#     blob_service_client = BlobServiceClient.from_connection_string(connect_str)
#     container_client = blob_service_client.get_container_client(container_name)
#     blob_client = container_client.get_blob_client(blob_name)
#     return blob_client.download_blob().readall()

# def parse_xml_files(xml_contents):
#     shapes = []
#     connections = []

#     for xml_content in xml_contents:
#         tree = ET.ElementTree(ET.fromstring(xml_content))
#         root = tree.getroot()

#         # Parse shapes and their text
#         for shape in root.findall(".//{http://schemas.microsoft.com/office/visio/2012/main}Shape"):
#             shape_id = shape.get('ID')
#             shape_text = shape.find(".//{http://schemas.microsoft.com/office/visio/2012/main}Text")
#             text_value = shape_text.text if shape_text is not None else "No Text"
#             shapes.append((shape_id, text_value))

#         # Parse connections between shapes
#         for connect in root.findall(".//{http://schemas.microsoft.com/office/visio/2012/main}Connect"):
#             from_shape = connect.get('FromSheet')
#             to_shape = connect.get('ToSheet')
#             connections.append((from_shape, to_shape))

#     return shapes, connections

# def visualize_diagram(shapes, connections, png_content=None):
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

#     # Optionally overlay the PNG image as a background
#     if png_content:
#         img = Image.open(BytesIO(png_content))
#         img.thumbnail((600, 600), Image.LANCZOS)  # Use Image.LANCZOS instead of Image.ANTIALIAS
#         plt.imshow(img, extent=[-1, 1, -1, 1], aspect='auto', alpha=0.5, zorder=-1)

#     # Save to file instead of showing
#     plt.savefig('output_diagram.png')
#     print("Diagram saved to output_diagram.png")

# def main():
#     # Define the Azure Blob Storage containers and files
#     xml_container_name = "xml-container"
#     xml_blob_names = [
#         "app.xml",
#         "core.xml",
#         "custom.xml", 
#         "document.xml",
#         "master1.xml",
#         "master2.xml",
#         "master3.xml",
#         "masters.xml",
#         "page1.xml",
#         "pages.xml",
#         "theme1.xml",
#          "windows.xml",  # or other relevant pages
#         # Add other XML files if necessary
#     ]
#     png_container_name = "visio-files"
#     png_blob_name = "sample-2.png"  # Ensure this name is correctly specified

#     # Download XML files
#     xml_contents = [download_blob_from_azure(xml_container_name, blob_name) for blob_name in xml_blob_names]

#     # Download PNG file
#     png_content = download_blob_from_azure(png_container_name, png_blob_name)

#     # Parse XML files and visualize the diagram
#     shapes, connections = parse_xml_files(xml_contents)
#     visualize_diagram(shapes, connections, png_content)

# if __name__ == "__main__":
#     main()


import streamlit as st
import matplotlib.pyplot as plt
from xml.etree import ElementTree as ET

def parse_visio_xml(xml_content):
    # Parse the XML content
    tree = ET.ElementTree(ET.fromstring(xml_content))
    root = tree.getroot()

    # Namespace for Visio XML
    namespace = {'visio': 'http://schemas.microsoft.com/office/visio/2012/main'}
    
    # Prepare figure
    fig, ax = plt.subplots()

    # Extract shapes and plot them
    for shape in root.findall('.//visio:Shape', namespace):
        shape_id = shape.get('ID')
        shape_type = shape.get('Type')
        pin_x = float(shape.find('.//visio:Cell[@N="PinX"]', namespace).get('V'))
        pin_y = float(shape.find('.//visio:Cell[@N="PinY"]', namespace).get('V'))
        width = shape.find('.//visio:Cell[@N="Width"]', namespace)
        height = shape.find('.//visio:Cell[@N="Height"]', namespace)

        # Draw rectangles
        if shape_type == 'Shape':
            if width is not None and height is not None:
                width = float(width.get('V'))
                height = float(height.get('V'))
                ax.add_patch(plt.Rectangle((pin_x - width/2, pin_y - height/2), width, height, fill=False))

            # Attempt to parse and draw other shapes
            # Example: Circles
            text_element = shape.find('.//visio:Text', namespace)
            if text_element is not None and text_element.text is not None:
                if 'circle' in text_element.text.lower():
                    radius = width.get('V') if width is not None else 0.5
                    ax.add_patch(plt.Circle((pin_x, pin_y), float(radius)/2, fill=False))

            # Draw text if available
            if text_element is not None and text_element.text is not None:
                ax.text(pin_x, pin_y, text_element.text.strip(), ha='center', va='center')

    # Extract connections and plot them
    for connect in root.findall('.//visio:Connect', namespace):
        from_sheet = connect.get('FromSheet')
        to_sheet = connect.get('ToSheet')

        # Get coordinates for 'From' and 'To' shapes
        from_shape = root.find(f".//visio:Shape[@ID='{from_sheet}']", namespace)
        to_shape = root.find(f".//visio:Shape[@ID='{to_sheet}']", namespace)

        if from_shape is not None and to_shape is not None:
            from_x = float(from_shape.find('.//visio:Cell[@N="PinX"]', namespace).get('V'))
            from_y = float(from_shape.find('.//visio:Cell[@N="PinY"]', namespace).get('V'))
            to_x = float(to_shape.find('.//visio:Cell[@N="PinX"]', namespace).get('V'))
            to_y = float(to_shape.find('.//visio:Cell[@N="PinY"]', namespace).get('V'))

            ax.plot([from_x, to_x], [from_y, to_y], 'k-', linewidth=1)

    # Set equal aspect ratio
    ax.set_aspect('equal')
    ax.autoscale_view()
    plt.axis('on')  # Show axes
    plt.gca().invert_yaxis()  # Invert Y axis to match typical diagram orientation
    return fig

# Streamlit UI
st.title("Visio XML Diagram Viewer")

uploaded_file = st.file_uploader("Upload an XML file", type="xml")

if uploaded_file is not None:
    # Read file content
    xml_content = uploaded_file.read().decode("utf-8")
    # Parse and visualize the diagram
    fig = parse_visio_xml(xml_content)
    st.pyplot(fig)

# # --- Streamlit App ---
# st.title("Visio Diagram Analyzer with GPT-4o Vision")

# st.markdown("""
# Upload a **PNG or JPEG** image of a diagram (such as a Visio export or screenshot).
# The app will:
# - Use GPT-4o Vision to extract structured shape and connector data from the diagram
# - Map the extracted info to a standardized template schema
# """)

# uploaded_file = st.file_uploader("Upload diagram image (PNG/JPEG)", type=["png", "jpg", "jpeg"])

# if uploaded_file:
#     st.image(uploaded_file, caption="Uploaded Diagram", use_column_width=True)
#     if st.button("Analyze and Standardize with GPT-4o"):
#         uploaded_file.seek(0)
#         image_bytes = uploaded_file.read()
#         with st.spinner("Analyzing diagram with GPT-4o..."):
#             try:
#                 diagram_json = analyze_diagram_with_gpt4o(image_bytes)
#             except Exception as e:
#                 st.error(f"Error from GPT-4o Vision: {e}")
#                 st.stop()
#         st.subheader("Extracted JSON")
#         st.code(diagram_json, language="json")
#         with st.spinner("Standardizing to template..."):
#             try:
#                 standardized = standardize_diagram_data(diagram_json)
#             except Exception as e:
#                 st.error(f"Standardization error: {e}")
#                 st.stop()
#         st.subheader("Standardized Data")
#         st.json(standardized)
#         st.download_button(
#             "Download Standardized JSON",
#             data=json.dumps(standardized, indent=2),
#             file_name="standardized_diagram.json",
#             mime="application/json"
#         )


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

def parse_xml(xml_content):
    tree = ET.ElementTree(ET.fromstring(xml_content))
    root = tree.getroot()
    shapes = []
    connections = []

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

def visualize_diagram(shapes, connections, png_content):
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

    # Overlay the PNG image as a background
    img = Image.open(BytesIO(png_content))
    img.thumbnail((600, 600), Image.ANTIALIAS)
    plt.imshow(img, extent=[-1, 1, -1, 1], aspect='auto', alpha=0.5, zorder=-1)

    # Save to file instead of showing
    plt.savefig('enhanced_output_diagram.png')
    print("Diagram saved to enhanced_output_diagram.png")

def main():
    # Define the Azure Blob Storage containers and files
    xml_container_name = "xml-container"
    xml_blob_name = "app.xml"
    png_container_name = "Visio-files"
    png_blob_name = "sample-2.png"

    # Download XML and PNG files
    xml_content = download_blob_from_azure(xml_container_name, xml_blob_name)
    png_content = download_blob_from_azure(png_container_name, png_blob_name)

    # Parse XML and visualize the diagram
    shapes, connections = parse_xml(xml_content)
    visualize_diagram(shapes, connections, png_content)

if __name__ == "__main__":
    main()

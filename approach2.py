# # import os
# # import subprocess
# # from azure.storage.blob import BlobServiceClient
# # from lxml import etree
# # from IPython.display import SVG, display
# # from dotenv import load_dotenv

# # # Load environment variables from .env file
# # load_dotenv()

# # # Configuration
# # connection_string = os.getenv("AZURE_CONNECTION_STRING")
# # container_name = "standardized-template"
# # footer_blob_name = "footer.vsdx"
# # sample_blob_name = "sample.vsdx"

# # # Initialize BlobServiceClient
# # blob_service_client = BlobServiceClient.from_connection_string(connection_string)
# # container_client = blob_service_client.get_container_client(container_name)

# # # Function to download a blob
# # def download_blob(blob_name, download_path):
# #     blob_client = container_client.get_blob_client(blob_name)
# #     with open(download_path, "wb") as file:
# #         file.write(blob_client.download_blob().readall())

# # # Function to convert VSDX to SVG using LibreOffice
# # def convert_vsdx_to_svg(vsdx_path, output_svg_path):
# #     subprocess.run(['soffice', '--headless', '--convert-to', 'svg', vsdx_path, '--outdir', '.'])
# #     os.rename(vsdx_path.replace('.vsdx', '.svg'), output_svg_path)

# # # Function to append footer SVG to sample SVG
# # def add_footer_to_svg(sample_svg_path, footer_svg_path, output_svg_path):
# #     # Parse the SVG files
# #     sample_svg = etree.parse(sample_svg_path)
# #     footer_svg = etree.parse(footer_svg_path)

# #     # Find the root element of the sample SVG
# #     sample_root = sample_svg.getroot()

# #     # Append the footer content to the sample content
# #     for element in footer_svg.getroot():
# #         sample_root.append(element)

# #     # Write the combined SVG to the output file
# #     sample_svg.write(output_svg_path, pretty_print=True)

# # # Download the sample and footer VSDX files
# # download_blob(sample_blob_name, "sample.vsdx")
# # download_blob(footer_blob_name, "footer.vsdx")

# # # Convert VSDX files to SVG
# # convert_vsdx_to_svg("sample.vsdx", "sample.svg")
# # convert_vsdx_to_svg("footer.vsdx", "footer.svg")

# # # Combine the SVGs
# # add_footer_to_svg("sample.svg", "footer.svg", "output.svg")

# # # Display the output SVG
# # display(SVG(filename="output.svg"))

# # # Clean up temporary files
# # os.remove("sample.vsdx")
# # os.remove("footer.vsdx")
# # os.remove("sample.svg")
# # os.remove("footer.svg")
# # os.remove("output.svg")




# import os
# import subprocess
# import tempfile
# from azure.storage.blob import BlobServiceClient
# from lxml import etree
# import streamlit as st
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Retrieve connection string from environment
# connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
# container_name = "standardized-template"
# footer_blob_name = "footer.vsdx"

# # Initialize BlobServiceClient
# blob_service_client = BlobServiceClient.from_connection_string(connection_string)
# container_client = blob_service_client.get_container_client(container_name)

# def download_blob(blob_name, download_path):
#     """Download a blob from Azure Blob Storage."""
#     blob_client = container_client.get_blob_client(blob_name)
#     with open(download_path, "wb") as file:
#         file.write(blob_client.download_blob().readall())

# def convert_vsdx_to_svg(vsdx_path, output_svg_path):
#     """Convert VSDX to SVG using LibreOffice."""
#     subprocess.run(['soffice', '--headless', '--convert-to', 'svg', vsdx_path, '--outdir', '.'])
#     os.rename(vsdx_path.replace('.vsdx', '.svg'), output_svg_path)

# def add_footer_to_svg(sample_svg_path, footer_svg_path, output_svg_path):
#     """Append footer SVG to sample SVG."""
#     sample_svg = etree.parse(sample_svg_path)
#     footer_svg = etree.parse(footer_svg_path)
#     sample_root = sample_svg.getroot()

#     for element in footer_svg.getroot():
#         sample_root.append(element)

#     sample_svg.write(output_svg_path, pretty_print=True)

# # Streamlit UI
# st.title("VSDX to SVG Converter with Footer")

# uploaded_file = st.file_uploader("Upload a VSDX file", type="vsdx")

# if uploaded_file is not None:
#     with tempfile.TemporaryDirectory() as temp_dir:
#         sample_vsdx_path = os.path.join(temp_dir, "sample.vsdx")
#         footer_vsdx_path = os.path.join(temp_dir, "footer.vsdx")
#         sample_svg_path = os.path.join(temp_dir, "sample.svg")
#         footer_svg_path = os.path.join(temp_dir, "footer.svg")
#         output_svg_path = os.path.join(temp_dir, "output.svg")

#         # Save the uploaded file to a temporary directory
#         with open(sample_vsdx_path, "wb") as file:
#             file.write(uploaded_file.read())

#         # Download the footer VSDX from Azure
#         download_blob(footer_blob_name, footer_vsdx_path)

#         # Convert VSDX files to SVG
#         convert_vsdx_to_svg(sample_vsdx_path, sample_svg_path)
#         convert_vsdx_to_svg(footer_vsdx_path, footer_svg_path)

#         # Combine the SVGs
#         add_footer_to_svg(sample_svg_path, footer_svg_path, output_svg_path)

#         # Display the output SVG
#         st.image(output_svg_path, caption='Processed SVG with Footer')




import streamlit as st
from lxml import etree
import tempfile
import os

def merge_svgs(test_svg_content, footer_svg_content):
    """Merge footer SVG elements into the test diagram SVG."""
    # Parse the SVG content
    test_svg = etree.fromstring(test_svg_content)
    footer_svg = etree.fromstring(footer_svg_content)

    # Append each element from the footer SVG to the test SVG
    for element in footer_svg:
        test_svg.append(element)

    # Return the merged SVG as a string
    return etree.tostring(test_svg, pretty_print=True)

# Streamlit UI
st.title("SVG Merger")

st.write("Upload the test diagram SVG and the footer SVG to merge them.")

# File uploaders for the two SVG files
test_svg_file = st.file_uploader("Upload Test Diagram SVG", type="svg")
footer_svg_file = st.file_uploader("Upload Footer SVG", type="svg")

if test_svg_file and footer_svg_file:
    # Read the contents of the uploaded files
    test_svg_content = test_svg_file.read()
    footer_svg_content = footer_svg_file.read()

    # Merge the SVG files
    merged_svg_content = merge_svgs(test_svg_content, footer_svg_content)

    # Save the result to a temporary file to display it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as temp_file:
        temp_file.write(merged_svg_content)
        temp_file_path = temp_file.name

    # Display the merged SVG
    st.image(temp_file_path, caption='Merged SVG')
    
    # Provide a download link for the merged SVG
    st.download_button(
        label="Download Merged SVG",
        data=merged_svg_content,
        file_name="merged_diagram.svg",
        mime="image/svg+xml"
    )


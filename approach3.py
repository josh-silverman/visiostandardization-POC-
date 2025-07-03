import streamlit as st
from lxml import etree
import tempfile

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
    st.image(temp_file_path, caption='Merged SVG', use_column_width=True)
    
    # Provide a download link for the merged SVG
    st.download_button(
        label="Download Merged SVG",
        data=merged_svg_content,
        file_name="merged_diagram.svg",
        mime="image/svg+xml"
    )

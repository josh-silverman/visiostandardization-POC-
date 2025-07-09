import streamlit as st
from lxml import etree as ET
from io import BytesIO

def normalize_svg_dimensions(root1, root2):
    # Extract viewBox dimensions
    vb1 = list(map(float, root1.get('viewBox').split()))
    vb2 = list(map(float, root2.get('viewBox').split()))

    # Define a common width to normalize both SVGs
    common_width = max(vb1[2], vb2[2])

    # Scale factor for each SVG
    scale1 = common_width / vb1[2]
    scale2 = common_width / vb2[2]

    # Adjust viewBox and scale elements in both SVGs
    vb1[2] *= scale1
    vb1[3] *= scale1
    vb2[2] *= scale2
    vb2[3] *= scale2

    root1.set('viewBox', f'0 0 {vb1[2]} {vb1[3]}')
    root2.set('viewBox', f'0 0 {vb2[2]} {vb2[3]}')

    return vb1, vb2, scale1, scale2

def add_text_backgrounds(root):
    # Iterate over all text elements
    for text_element in root.findall(".//{http://www.w3.org/2000/svg}text"):
        # Get the text's bounding box attributes
        x = float(text_element.get('x', '0'))
        y = float(text_element.get('y', '0'))

        # Create a rectangle element to serve as a background
        rect = ET.Element('rect', {
            'x': str(x - 2), # Adjust x position slightly for padding
            'y': str(y - 12), # Adjust y position to account for text height
            'width': '100', # Placeholder width, adjust as needed
            'height': '16', # Placeholder height, adjust as needed
            'fill': 'lightblue'
        })

        # Insert the rectangle before the text element
        parent = text_element.getparent()
        if parent is not None:
            parent.insert(parent.index(text_element), rect)

def merge_svgs(svg1_content, svg2_content):
    # Parse the SVG strings as bytes
    root1 = ET.fromstring(svg1_content)
    root2 = ET.fromstring(svg2_content)

    # Add light blue backgrounds to text in the first SVG
    add_text_backgrounds(root1)

    # Normalize dimensions
    vb1, vb2, scale1, scale2 = normalize_svg_dimensions(root1, root2)

    # Update the viewBox and height of the merged SVG
    new_height = vb1[3] + vb2[3]
    root1.set('viewBox', f'0 0 {vb1[2]} {new_height}')
    root1.set('height', f'{new_height}')

    # Create a group for the second SVG's content with scaling
    transform_group = f'scale({scale2}) translate(0, {vb1[3] / scale2})'
    group2 = ET.Element('g', attrib={'transform': transform_group})

    # Move all elements from the second SVG into this group
    for element in list(root2):
        group2.append(element)

    # Add the group to the first SVG
    root1.append(group2)

    # Convert modified tree back to bytes
    merged_svg_bytes = ET.tostring(root1, encoding='utf-8', method='xml')

    return merged_svg_bytes

def main():
    st.title("SVG Merger")
    st.write("Upload two SVG files to merge them.")

    uploaded_file1 = st.file_uploader("Choose first SVG file", type="svg")
    uploaded_file2 = st.file_uploader("Choose second SVG file", type="svg")

    if uploaded_file1 is not None and uploaded_file2 is not None:
        # Read files as bytes
        svg1_content = uploaded_file1.read()
        svg2_content = uploaded_file2.read()

        merged_svg_bytes = merge_svgs(svg1_content, svg2_content)

        # Convert bytes to string for display
        merged_svg_str = merged_svg_bytes.decode('utf-8')

        # Display the merged SVG
        st.subheader("Merged SVG")
        st.markdown(f'<div>{merged_svg_str}</div>', unsafe_allow_html=True)

        # Provide download link
        st.download_button("Download Merged SVG", data=merged_svg_bytes, file_name="merged.svg", mime="image/svg+xml")

if __name__ == "__main__":
    main()

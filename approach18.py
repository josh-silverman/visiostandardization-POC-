# # # import streamlit as st
# # # from lxml import etree as ET
# # # from io import BytesIO

# # # def normalize_svg_dimensions(root1, root2):
# # #     # Extract viewBox dimensions
# # #     vb1 = list(map(float, root1.get('viewBox').split()))
# # #     vb2 = list(map(float, root2.get('viewBox').split()))

# # #     # Define a common width to normalize both SVGs
# # #     common_width = max(vb1[2], vb2[2])

# # #     # Scale factor for each SVG
# # #     scale1 = common_width / vb1[2]
# # #     scale2 = common_width / vb2[2]

# # #     # Adjust viewBox and scale elements in both SVGs
# # #     vb1[2] *= scale1
# # #     vb1[3] *= scale1
# # #     vb2[2] *= scale2
# # #     vb2[3] *= scale2

# # #     root1.set('viewBox', f'0 0 {vb1[2]} {vb1[3]}')
# # #     root2.set('viewBox', f'0 0 {vb2[2]} {vb2[3]}')

# # #     return vb1, vb2, scale1, scale2

# # # def add_text_backgrounds(root):
# # #     # Iterate over all text elements
# # #     for text_element in root.findall(".//{http://www.w3.org/2000/svg}text"):
# # #         # Get the text's bounding box attributes
# # #         x = float(text_element.get('x', '0'))
# # #         y = float(text_element.get('y', '0'))

# # #         # Create a rectangle element to serve as a background
# # #         rect = ET.Element('rect', {
# # #             'x': str(x - 2), # Adjust x position slightly for padding
# # #             'y': str(y - 12), # Adjust y position to account for text height
# # #             'width': '100', # Placeholder width, adjust as needed
# # #             'height': '16', # Placeholder height, adjust as needed
# # #             'fill': 'lightblue'
# # #         })

# # #         # Insert the rectangle before the text element
# # #         parent = text_element.getparent()
# # #         if parent is not None:
# # #             parent.insert(parent.index(text_element), rect)

# # # def merge_svgs(svg1_content, svg2_content):
# # #     # Parse the SVG strings as bytes
# # #     root1 = ET.fromstring(svg1_content)
# # #     root2 = ET.fromstring(svg2_content)

# # #     # Add light blue backgrounds to text in the first SVG
# # #     add_text_backgrounds(root1)

# # #     # Normalize dimensions
# # #     vb1, vb2, scale1, scale2 = normalize_svg_dimensions(root1, root2)

# # #     # Update the viewBox and height of the merged SVG
# # #     new_height = vb1[3] + vb2[3]
# # #     root1.set('viewBox', f'0 0 {vb1[2]} {new_height}')
# # #     root1.set('height', f'{new_height}')

# # #     # Create a group for the second SVG's content with scaling
# # #     transform_group = f'scale({scale2}) translate(0, {vb1[3] / scale2})'
# # #     group2 = ET.Element('g', attrib={'transform': transform_group})

# # #     # Move all elements from the second SVG into this group
# # #     for element in list(root2):
# # #         group2.append(element)

# # #     # Add the group to the first SVG
# # #     root1.append(group2)

# # #     # Convert modified tree back to bytes
# # #     merged_svg_bytes = ET.tostring(root1, encoding='utf-8', method='xml')

# # #     return merged_svg_bytes

# # # def main():
# # #     st.title("SVG Merger")
# # #     st.write("Upload two SVG files to merge them.")

# # #     uploaded_file1 = st.file_uploader("Choose first SVG file", type="svg")
# # #     uploaded_file2 = st.file_uploader("Choose second SVG file", type="svg")

# # #     if uploaded_file1 is not None and uploaded_file2 is not None:
# # #         # Read files as bytes
# # #         svg1_content = uploaded_file1.read()
# # #         svg2_content = uploaded_file2.read()

# # #         merged_svg_bytes = merge_svgs(svg1_content, svg2_content)

# # #         # Convert bytes to string for display
# # #         merged_svg_str = merged_svg_bytes.decode('utf-8')

# # #         # Display the merged SVG
# # #         st.subheader("Merged SVG")
# # #         st.markdown(f'<div>{merged_svg_str}</div>', unsafe_allow_html=True)

# # #         # Provide download link
# # #         st.download_button("Download Merged SVG", data=merged_svg_bytes, file_name="merged.svg", mime="image/svg+xml")

# # # if __name__ == "__main__":
# # #     main()























# # import streamlit as st
# # from lxml import etree as ET
# # from io import BytesIO

# # def normalize_svg_dimensions(root1, root2):
# #     # Extract viewBox dimensions
# #     vb1 = list(map(float, root1.get('viewBox').split()))
# #     vb2 = list(map(float, root2.get('viewBox').split()))

# #     # Define a common width to normalize both SVGs
# #     common_width = max(vb1[2], vb2[2])

# #     # Scale factor for each SVG
# #     scale1 = common_width / vb1[2]
# #     scale2 = common_width / vb2[2]

# #     # Adjust viewBox and scale elements in both SVGs
# #     vb1[2] *= scale1
# #     vb1[3] *= scale1
# #     vb2[2] *= scale2
# #     vb2[3] *= scale2

# #     root1.set('viewBox', f'0 0 {vb1[2]} {vb1[3]}')
# #     root2.set('viewBox', f'0 0 {vb2[2]} {vb2[3]}')

# #     return vb1, vb2, scale1, scale2

# # def add_text_backgrounds(root):
# #     # Find all text elements and their positions
# #     text_elements = root.findall(".//{http://www.w3.org/2000/svg}text")
# #     if not text_elements:
# #         return

# #     min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
# #     for text_element in text_elements:
# #         # Get all positions for text spans if present, else just the text element
# #         x = float(text_element.get('x', '0'))
# #         y = float(text_element.get('y', '0'))
# #         min_x = min(min_x, x)
# #         min_y = min(min_y, y - 12)   # Estimate ascent for font
# #         max_x = max(max_x, x + 100)  # Guess width (could be improved if you know the font-size)
# #         max_y = max(max_y, y + 4)    # Guess descent

# #     padding = 4
# #     min_x -= padding
# #     min_y -= padding
# #     max_x += padding
# #     max_y += padding

# #     rect = ET.Element('rect', {
# #         'x': str(min_x),
# #         'y': str(min_y),
# #         'width': str(max_x - min_x),
# #         'height': str(max_y - min_y),
# #         'fill': 'lightblue'
# #     })
# #     root.insert(0, rect)

# # def merge_svgs(svg1_content, svg2_content):
# #     # Parse the SVG strings as bytes
# #     root1 = ET.fromstring(svg1_content)
# #     root2 = ET.fromstring(svg2_content)

# #     # Add light blue background behind all text in the first SVG
# #     add_text_backgrounds(root1)

# #     # Normalize dimensions
# #     vb1, vb2, scale1, scale2 = normalize_svg_dimensions(root1, root2)

# #     # Make the second SVG (footer) bigger
# #     scale2 *= 1.2

# #     # Update the viewBox and height of the merged SVG
# #     new_height = vb1[3] + vb2[3] * scale2
# #     root1.set('viewBox', f'0 0 {vb1[2]} {new_height}')
# #     root1.set('height', f'{new_height}')

# #     # Create a group for the second SVG's content with scaling
# #     transform_group = f'scale({scale2}) translate(0, {vb1[3] / scale2})'
# #     group2 = ET.Element('g', attrib={'transform': transform_group})

# #     # Move all elements from the second SVG into this group
# #     for element in list(root2):
# #         group2.append(element)

# #     # Add the group to the first SVG
# #     root1.append(group2)

# #     # Convert modified tree back to bytes
# #     merged_svg_bytes = ET.tostring(root1, encoding='utf-8', method='xml')

# #     return merged_svg_bytes

# # def main():
# #     st.title("SVG Merger")
# #     st.write("Upload two SVG files to merge them.")

# #     uploaded_file1 = st.file_uploader("Choose first SVG file", type="svg")
# #     uploaded_file2 = st.file_uploader("Choose second SVG file", type="svg")

# #     if uploaded_file1 is not None and uploaded_file2 is not None:
# #         # Read files as bytes
# #         svg1_content = uploaded_file1.read()
# #         svg2_content = uploaded_file2.read()

# #         merged_svg_bytes = merge_svgs(svg1_content, svg2_content)

# #         # Convert bytes to string for display
# #         merged_svg_str = merged_svg_bytes.decode('utf-8')

# #         # Display the merged SVG
# #         st.subheader("Merged SVG")
# #         st.markdown(f'<div>{merged_svg_str}</div>', unsafe_allow_html=True)

# #         # Provide download link
# #         st.download_button("Download Merged SVG", data=merged_svg_bytes, file_name="merged.svg", mime="image/svg+xml")

# # if __name__ == "__main__":
# #     main()













# import streamlit as st
# from lxml import etree as ET
# from io import BytesIO

# def normalize_svg_dimensions(root1, root2):
#     # Extract viewBox dimensions
#     vb1 = list(map(float, root1.get('viewBox').split()))
#     vb2 = list(map(float, root2.get('viewBox').split()))

#     # Define a common width to normalize both SVGs
#     common_width = max(vb1[2], vb2[2])

#     # Scale factor for each SVG
#     scale1 = common_width / vb1[2]
#     scale2 = common_width / vb2[2]

#     # Adjust viewBox and scale elements in both SVGs
#     vb1[2] *= scale1
#     vb1[3] *= scale1
#     vb2[2] *= scale2
#     vb2[3] *= scale2

#     root1.set('viewBox', f'0 0 {vb1[2]} {vb1[3]}')
#     root2.set('viewBox', f'0 0 {vb2[2]} {vb2[3]}')

#     return vb1, vb2, scale1, scale2

# def estimate_text_width(text, font_size=16):
#     # This is a rough estimate: width = 0.6 * font_size * number of characters
#     # You can refine this if you know font metrics
#     return max(20, 0.6 * font_size * len(text))

# def add_text_backgrounds(root):
#     ns = {'svg': "http://www.w3.org/2000/svg"}
#     for text_element in root.findall(".//svg:text", namespaces=ns):
#         x = float(text_element.get('x', '0'))
#         y = float(text_element.get('y', '0'))
#         font_size = float(text_element.get('font-size', '16'))
#         text_content = "".join(text_element.itertext())

#         # Estimate width and height
#         width = estimate_text_width(text_content, font_size)
#         height = font_size * 1.2  # 1.2 is a good line-height for most fonts

#         # Rectangle background parameters
#         padding_x = font_size * 0.3
#         padding_y = font_size * 0.2
#         rect_x = x - padding_x
#         rect_y = y - font_size - padding_y

#         rect = ET.Element('rect', {
#             'x': str(rect_x),
#             'y': str(rect_y),
#             'width': str(width + 2*padding_x),
#             'height': str(height + 2*padding_y),
#             'fill': 'lightblue',
#             'stroke': 'black',
#             'stroke-width': '2'
#         })

#         parent = text_element.getparent()
#         if parent is not None:
#             parent.insert(parent.index(text_element), rect)

# def merge_svgs(svg1_content, svg2_content):
#     # Parse the SVG strings as bytes
#     root1 = ET.fromstring(svg1_content)
#     root2 = ET.fromstring(svg2_content)

#     # Add blue background and black outline to all text in the first SVG
#     add_text_backgrounds(root1)

#     # Normalize dimensions
#     vb1, vb2, scale1, scale2 = normalize_svg_dimensions(root1, root2)

#     # Make the second SVG (footer) bigger
#     scale2 *= 1.2

#     # Update the viewBox and height of the merged SVG
#     new_height = vb1[3] + vb2[3] * scale2
#     root1.set('viewBox', f'0 0 {vb1[2]} {new_height}')
#     root1.set('height', f'{new_height}')

#     # Create a group for the second SVG's content with scaling
#     transform_group = f'scale({scale2}) translate(0, {vb1[3] / scale2})'
#     group2 = ET.Element('g', attrib={'transform': transform_group})

#     # Move all elements from the second SVG into this group
#     for element in list(root2):
#         group2.append(element)

#     # Add the group to the first SVG
#     root1.append(group2)

#     # Convert modified tree back to bytes
#     merged_svg_bytes = ET.tostring(root1, encoding='utf-8', method='xml')

#     return merged_svg_bytes

# def main():
#     st.title("SVG Merger")
#     st.write("Upload two SVG files to merge them.")

#     uploaded_file1 = st.file_uploader("Choose first SVG file", type="svg")
#     uploaded_file2 = st.file_uploader("Choose second SVG file", type="svg")

#     if uploaded_file1 is not None and uploaded_file2 is not None:
#         # Read files as bytes
#         svg1_content = uploaded_file1.read()
#         svg2_content = uploaded_file2.read()

#         merged_svg_bytes = merge_svgs(svg1_content, svg2_content)

#         # Convert bytes to string for display
#         merged_svg_str = merged_svg_bytes.decode('utf-8')

#         # Display the merged SVG
#         st.subheader("Merged SVG")
#         st.markdown(f'<div>{merged_svg_str}</div>', unsafe_allow_html=True)

#         # Provide download link
#         st.download_button("Download Merged SVG", data=merged_svg_bytes, file_name="merged.svg", mime="image/svg+xml")

# if __name__ == "__main__":
#     main()












import streamlit as st
from lxml import etree as ET

def normalize_svg_dimensions(root1, root2):
    vb1 = list(map(float, root1.get('viewBox').split()))
    vb2 = list(map(float, root2.get('viewBox').split()))
    common_width = max(vb1[2], vb2[2])
    scale1 = common_width / vb1[2]
    scale2 = common_width / vb2[2]
    vb1[2] *= scale1
    vb1[3] *= scale1
    vb2[2] *= scale2
    vb2[3] *= scale2
    root1.set('viewBox', f'0 0 {vb1[2]} {vb1[3]}')
    root2.set('viewBox', f'0 0 {vb2[2]} {vb2[3]}')
    return vb1, vb2, scale1, scale2

def estimate_text_width(text, font_size=16):
    # Very rough, but good enough for most cases
    return max(20, 0.6 * font_size * len(text))

def add_text_backgrounds(root):
    # Support for SVGs with or without namespace
    nsmap = root.nsmap
    svg_ns = nsmap.get(None, "http://www.w3.org/2000/svg")
    ns = {'svg': svg_ns}
    text_xpath = ".//svg:text" if svg_ns else ".//text"

    for text_element in root.xpath(text_xpath, namespaces=ns):
        # Get x/y, font-size, and text
        x = float(text_element.get('x', '0'))
        y = float(text_element.get('y', '0'))
        font_size = float(text_element.get('font-size', '16'))
        text_content = "".join(text_element.itertext()).strip()
        if not text_content:
            continue
        width = estimate_text_width(text_content, font_size)
        height = font_size * 1.2  # add some leading
        padding_x = font_size * 0.3
        padding_y = font_size * 0.2
        rect_x = x - padding_x
        rect_y = y - font_size - padding_y

        rect = ET.Element(
            f'{{{svg_ns}}}rect' if svg_ns else 'rect',
            {
                'x': str(rect_x),
                'y': str(rect_y),
                'width': str(width + 2*padding_x),
                'height': str(height + 2*padding_y),
                'fill': 'lightblue',
                'stroke': 'black',
                'stroke-width': '3'
            }
        )
        parent = text_element.getparent()
        if parent is not None:
            parent.insert(parent.index(text_element), rect)

def merge_svgs(svg1_content, svg2_content):
    root1 = ET.fromstring(svg1_content)
    root2 = ET.fromstring(svg2_content)
    add_text_backgrounds(root1)
    vb1, vb2, scale1, scale2 = normalize_svg_dimensions(root1, root2)
    scale2 *= 1.2  # Make footer bigger
    new_height = vb1[3] + vb2[3] * scale2
    root1.set('viewBox', f'0 0 {vb1[2]} {new_height}')
    root1.set('height', f'{new_height}')
    # Namespaces for group creation
    svg_ns = root1.nsmap.get(None, "http://www.w3.org/2000/svg")
    g_tag = f'{{{svg_ns}}}g' if svg_ns else 'g'
    transform_group = f'scale({scale2}) translate(0, {vb1[3] / scale2})'
    group2 = ET.Element(g_tag, attrib={'transform': transform_group})
    for element in list(root2):
        group2.append(element)
    root1.append(group2)
    merged_svg_bytes = ET.tostring(root1, encoding='utf-8', method='xml')
    return merged_svg_bytes

def main():
    st.title("SVG Merger")
    st.write("Upload two SVG files to merge them.")
    uploaded_file1 = st.file_uploader("Choose first SVG file", type="svg")
    uploaded_file2 = st.file_uploader("Choose second SVG file", type="svg")
    if uploaded_file1 is not None and uploaded_file2 is not None:
        svg1_content = uploaded_file1.read()
        svg2_content = uploaded_file2.read()
        merged_svg_bytes = merge_svgs(svg1_content, svg2_content)
        merged_svg_str = merged_svg_bytes.decode('utf-8')
        st.subheader("Merged SVG")
        st.markdown(
            f'<div style="background:#fff;border:1px solid #ddd">'
            f'<svg width="100%" height="auto" viewBox="{ET.fromstring(merged_svg_bytes).get("viewBox")}">'
            f'{merged_svg_str.split("?>")[-1].replace("<svg", "", 1).replace("</svg>", "", 1)}'
            f'</svg></div>',
            unsafe_allow_html=True,
        )
        st.download_button(
            "Download Merged SVG",
            data=merged_svg_bytes,
            file_name="merged.svg",
            mime="image/svg+xml"
        )

if __name__ == "__main__":
    main()

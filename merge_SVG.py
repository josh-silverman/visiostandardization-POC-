# # # import streamlit as st
# # # import xml.etree.ElementTree as ET
# # # import re

# # # def get_vb_wh(root):
# # #     vb = root.get('viewBox')
# # #     if vb:
# # #         vb = list(map(float, vb.split()))
# # #         width = vb[2]
# # #         height = vb[3]
# # #     else:
# # #         width = float(root.get('width', '100'))
# # #         height = float(root.get('height', '100'))
# # #         vb = [0, 0, width, height]
# # #     return vb, width, height

# # # def merge_svgs_no_scale(svg1_content, svg2_content):
# # #     root1 = ET.fromstring(svg1_content)
# # #     root2 = ET.fromstring(svg2_content)

# # #     vb1, width1, height1 = get_vb_wh(root1)
# # #     vb2, width2, height2 = get_vb_wh(root2)

# # #     merged_width = max(width1, width2)
# # #     merged_height = height1 + height2

# # #     svg_ns = "http://www.w3.org/2000/svg"
# # #     ET.register_namespace('', svg_ns)
# # #     merged_svg = ET.Element('svg', {
# # #         'xmlns': svg_ns,
# # #         'width': str(merged_width),
# # #         'height': str(merged_height),
# # #         'viewBox': f"0 0 {merged_width} {merged_height}"
# # #     })

# # #     # First SVG's children at y=0
# # #     g1 = ET.Element('g')
# # #     for elem in list(root1):
# # #         g1.append(elem)
# # #     merged_svg.append(g1)

# # #     # Second SVG's children shifted down by height1
# # #     g2 = ET.Element('g', {'transform': f'translate(0,{height1})'})
# # #     for elem in list(root2):
# # #         g2.append(elem)
# # #     merged_svg.append(g2)

# # # #     return ET.tostring(merged_svg, encoding='unicode', method='xml')

# # # # def remove_inner_xmlns(svg_content):
# # # #     # Remove ONLY the first xmlns attribute in the SVG tag, if present
# # # #     return re.sub(r'<svg[^>]*\s+xmlns="[^"]+"', lambda m: m.group(0).replace(m.group(0)[m.group(0).find('xmlns="'):m.group(0).find('"', m.group(0).find('xmlns="'))+1], ''), svg_content, count=1)

# # # # def main():
# # # #     st.title("SVG Vertical Merger (No Scaling, No Namespace Errors)")
# # # #     st.write("Upload two SVG files to merge them vertically, without scaling.")

# # # #     uploaded_file1 = st.file_uploader("Choose first SVG file", type="svg")
# # # #     uploaded_file2 = st.file_uploader("Choose second SVG file", type="svg")

# # # #     if uploaded_file1 and uploaded_file2:
# # # #         svg1_content = uploaded_file1.read().decode("utf-8")
# # # #         svg2_content = uploaded_file2.read().decode("utf-8")

# # # #         # Remove any inner xmlns attributes to prevent 'xmlns redefined' error
# # # #         svg1_content = re.sub(r'\s+xmlns="[^"]+"', '', svg1_content, count=1)
# # # #         svg2_content = re.sub(r'\s+xmlns="[^"]+"', '', svg2_content, count=1)

# # # #         merged_svg = merge_svgs_no_scale(svg1_content, svg2_content)

# # # #         # Display the merged SVG
# # # #         st.subheader("Merged SVG")
# # # #         st.markdown(
# # # #             f'<div style="background:#fff;border:1px solid #ddd">{merged_svg}</div>',
# # # #             unsafe_allow_html=True
# # # #         )

# # # #         # Provide download link
# # # #         st.download_button(
# # # #             "Download Merged SVG",
# # # #             data=merged_svg,
# # # #             file_name="merged.svg",
# # # #             mime="image/svg+xml"
# # # #         )

# # # # if __name__ == "__main__":
# # # #     main()





# # # import streamlit as st
# # # import xml.etree.ElementTree as ET
# # # import re

# # # def get_vb_wh(root):
# # #     vb = root.get('viewBox')
# # #     if vb:
# # #         vb = list(map(float, vb.split()))
# # #         width = vb[2]
# # #         height = vb[3]
# # #     else:
# # #         width = float(root.get('width', '100'))
# # #         height = float(root.get('height', '100'))
# # #         vb = [0, 0, width, height]
# # #     return vb, width, height

# # # def merge_svgs_scale_first(svg1_content, svg2_content):
# # #     root1 = ET.fromstring(svg1_content)
# # #     root2 = ET.fromstring(svg2_content)

# # #     vb1, width1, height1 = get_vb_wh(root1)
# # #     vb2, width2, height2 = get_vb_wh(root2)

# # #     # Scale factor to match width2
# # #     scale1 = width2 / width1 if width1 > 0 else 1.0
# # #     scaled_height1 = height1 * scale1

# # #     merged_width = width2
# # #     merged_height = scaled_height1 + height2

# # #     svg_ns = "http://www.w3.org/2000/svg"
# # #     ET.register_namespace('', svg_ns)
# # #     merged_svg = ET.Element('svg', {
# # #         'xmlns': svg_ns,
# # #         'width': str(merged_width),
# # #         'height': str(merged_height),
# # #         'viewBox': f"0 0 {merged_width} {merged_height}"
# # #     })

# # #     # First SVG's children, scaled to match width2
# # #     g1 = ET.Element('g', {'transform': f'scale({scale1})'})
# # #     for elem in list(root1):
# # #         g1.append(elem)
# # #     merged_svg.append(g1)

# # #     # Second SVG's children, shifted down by scaled height1
# # #     g2 = ET.Element('g', {'transform': f'translate(0,{scaled_height1})'})
# # #     for elem in list(root2):
# # #         g2.append(elem)
# # #     merged_svg.append(g2)

# # #     return ET.tostring(merged_svg, encoding='unicode', method='xml')

# # # def main():
# # #     st.title("SVG Merger (First SVG Scaled to Match Second's Width)")
# # #     st.write("First SVG will be scaled to match the width of the second SVG.")

# # #     uploaded_file1 = st.file_uploader("Choose first SVG file", type="svg")
# # #     uploaded_file2 = st.file_uploader("Choose second SVG file", type="svg")

# # #     if uploaded_file1 and uploaded_file2:
# # #         svg1_content = uploaded_file1.read().decode("utf-8")
# # #         svg2_content = uploaded_file2.read().decode("utf-8")

# # #         # Remove any inner xmlns attributes to prevent 'xmlns redefined' error
# # #         svg1_content = re.sub(r'\s+xmlns="[^"]+"', '', svg1_content, count=1)
# # #         svg2_content = re.sub(r'\s+xmlns="[^"]+"', '', svg2_content, count=1)

# # #         merged_svg = merge_svgs_scale_first(svg1_content, svg2_content)

# # #         # Display the merged SVG
# # #         st.subheader("Merged SVG")
# # #         st.markdown(
# # #             f'<div style="background:#fff;border:1px solid #ddd">{merged_svg}</div>',
# # #             unsafe_allow_html=True
# # #         )

# # #         # Provide download link
# # #         st.download_button(
# # #             "Download Merged SVG",
# # #             data=merged_svg,
# # #             file_name="merged.svg",
# # #             mime="image/svg+xml"
# # #         )

# # # if __name__ == "__main__":
# # #     main()


# # import streamlit as st
# # import xml.etree.ElementTree as ET
# # import re

# # def get_vb_wh(root):
# #     vb = root.get('viewBox')
# #     if vb:
# #         vb = list(map(float, vb.split()))
# #         width = vb[2]
# #         height = vb[3]
# #     else:
# #         width = float(root.get('width', '100'))
# #         height = float(root.get('height', '100'))
# #         vb = [0, 0, width, height]
# #     return vb, width, height

# # def scale_text_fontsize(elem, scale):
# #     # Recursively scale font-size attributes in all text nodes
# #     for child in elem.iter():
# #         if child.tag.endswith('text'):
# #             # font-size can be in attribute or style
# #             if 'font-size' in child.attrib:
# #                 try:
# #                     fs = float(child.attrib['font-size'])
# #                     child.attrib['font-size'] = str(fs * scale)
# #                 except Exception:
# #                     pass
# #             # handle style attribute
# #             if 'style' in child.attrib:
# #                 # Look for font-size: ...px or font-size: ...;
# #                 style = child.attrib['style']
# #                 new_style = re.sub(
# #                     r'(font-size\s*:\s*)([0-9.]+)(px)?',
# #                     lambda m: f"{m.group(1)}{float(m.group(2)) * scale}{m.group(3) or ''}",
# #                     style
# #                 )
# #                 child.attrib['style'] = new_style

# # def merge_svgs_scale_first(svg1_content, svg2_content):
# #     root1 = ET.fromstring(svg1_content)
# #     root2 = ET.fromstring(svg2_content)

# #     vb1, width1, height1 = get_vb_wh(root1)
# #     vb2, width2, height2 = get_vb_wh(root2)

# #     scale1 = width2 / width1 if width1 > 0 else 1.0
# #     scaled_height1 = height1 * scale1

# #     merged_width = width2
# #     merged_height = scaled_height1 + height2

# #     svg_ns = "http://www.w3.org/2000/svg"
# #     ET.register_namespace('', svg_ns)
# #     merged_svg = ET.Element('svg', {
# #         'xmlns': svg_ns,
# #         'width': str(merged_width),
# #         'height': str(merged_height),
# #         'viewBox': f"0 0 {merged_width} {merged_height}"
# #     })

# #     # Scale all text font-sizes in the first SVG
# #     scale_text_fontsize(root1, scale1)

# #     # First SVG's children, scaled to match width2
# #     g1 = ET.Element('g', {'transform': f'scale({scale1})'})
# #     for elem in list(root1):
# #         g1.append(elem)
# #     merged_svg.append(g1)

# #     # Second SVG's children, shifted down by scaled height1
# #     g2 = ET.Element('g', {'transform': f'translate(0,{scaled_height1})'})
# #     for elem in list(root2):
# #         g2.append(elem)
# #     merged_svg.append(g2)

# #     return ET.tostring(merged_svg, encoding='unicode', method='xml')

# # def main():
# #     st.title("SVG Merger (First SVG Scaled to Match Second's Width, Text Fixed)")
# #     st.write("First SVG will be scaled to match the width of the second SVG, including text sizes.")

# #     uploaded_file1 = st.file_uploader("Choose first SVG file", type="svg")
# #     uploaded_file2 = st.file_uploader("Choose second SVG file", type="svg")

# #     if uploaded_file1 and uploaded_file2:
# #         svg1_content = uploaded_file1.read().decode("utf-8")
# #         svg2_content = uploaded_file2.read().decode("utf-8")

# #         # Remove any inner xmlns attributes to prevent 'xmlns redefined' error
# #         svg1_content = re.sub(r'\s+xmlns="[^"]+"', '', svg1_content, count=1)
# #         svg2_content = re.sub(r'\s+xmlns="[^"]+"', '', svg2_content, count=1)

# #         merged_svg = merge_svgs_scale_first(svg1_content, svg2_content)

# #         # Display the merged SVG
# #         st.subheader("Merged SVG")
# #         st.markdown(
# #             f'<div style="background:#fff;border:1px solid #ddd">{merged_svg}</div>',
# #             unsafe_allow_html=True
# #         )

# #         # Provide download link
# #         st.download_button(
# #             "Download Merged SVG",
# #             data=merged_svg,
# #             file_name="merged.svg",
# #             mime="image/svg+xml"
# #         )

# # if __name__ == "__main__":
# #     main()



# import streamlit as st
# import xml.etree.ElementTree as ET
# import re

# TARGET_PAGE_WIDTH = 800
# TARGET_PAGE_HEIGHT = 1000

# def get_vb_wh(root):
#     vb = root.get('viewBox')
#     if vb:
#         vb = list(map(float, vb.split()))
#         width = vb[2]
#         height = vb[3]
#     else:
#         width = float(root.get('width', '100'))
#         height = float(root.get('height', '100'))
#         vb = [0, 0, width, height]
#     return vb, width, height

# def scale_text_fontsize(elem, scale):
#     # Recursively scale font-size attributes in all text nodes
#     for child in elem.iter():
#         if child.tag.endswith('text'):
#             # font-size in attribute
#             if 'font-size' in child.attrib:
#                 try:
#                     fs = float(child.attrib['font-size'])
#                     child.attrib['font-size'] = str(fs * scale)
#                 except Exception:
#                     pass
#             # handle style attribute
#             if 'style' in child.attrib:
#                 style = child.attrib['style']
#                 new_style = re.sub(
#                     r'(font-size\s*:\s*)([0-9.]+)(px)?',
#                     lambda m: f"{m.group(1)}{float(m.group(2)) * scale}{m.group(3) or ''}",
#                     style
#                 )
#                 child.attrib['style'] = new_style

# def merge_and_fit_svgs(svg1_content, svg2_content, target_width, target_height):
#     root1 = ET.fromstring(svg1_content)
#     root2 = ET.fromstring(svg2_content)

#     vb1, width1, height1 = get_vb_wh(root1)
#     vb2, width2, height2 = get_vb_wh(root2)

#     # Scale factor to match width2
#     scale1 = width2 / width1 if width1 > 0 else 1.0
#     scaled_height1 = height1 * scale1

#     merged_width = width2
#     merged_height = scaled_height1 + height2

#     # Scale all text font-sizes in the first SVG
#     scale_text_fontsize(root1, scale1)

#     svg_ns = "http://www.w3.org/2000/svg"
#     ET.register_namespace('', svg_ns)

#     # The merged SVG, with viewBox covering the merged content
#     merged_group = ET.Element('g')

#     # First SVG's children, scaled to match width2
#     g1 = ET.Element('g', {'transform': f'scale({scale1})'})
#     for elem in list(root1):
#         g1.append(elem)
#     merged_group.append(g1)

#     # Second SVG's children, shifted down by scaled height1
#     g2 = ET.Element('g', {'transform': f'translate(0,{scaled_height1})'})
#     for elem in list(root2):
#         g2.append(elem)
#     merged_group.append(g2)

#     # Calculate scale to fit merged content inside target "page"
#     scale_to_fit = min(target_width / merged_width, target_height / merged_height)

#     # Outer SVG element with fixed size and viewBox
#     final_svg = ET.Element('svg', {
#         'xmlns': svg_ns,
#         'width': str(target_width),
#         'height': str(target_height),
#         'viewBox': f"0 0 {target_width} {target_height}"
#     })

#     # Center the merged group vertically
#     translate_x = (target_width - merged_width * scale_to_fit) / 2
#     translate_y = (target_height - merged_height * scale_to_fit) / 2

#     outer_g = ET.Element('g', {'transform': f'translate({translate_x},{translate_y}) scale({scale_to_fit})'})
#     outer_g.append(merged_group)
#     final_svg.append(outer_g)

#     return ET.tostring(final_svg, encoding='unicode', method='xml')

# def main():
#     st.title("SVG Merger (Fit Both SVGs on a Single Page!)")
#     st.write(f"Both SVGs will be merged and scaled to fit within {TARGET_PAGE_WIDTH}x{TARGET_PAGE_HEIGHT} px.")

#     uploaded_file1 = st.file_uploader("Choose first SVG file", type="svg")
#     uploaded_file2 = st.file_uploader("Choose second SVG file", type="svg")

#     if uploaded_file1 and uploaded_file2:
#         svg1_content = uploaded_file1.read().decode("utf-8")
#         svg2_content = uploaded_file2.read().decode("utf-8")

#         # Remove any inner xmlns attributes to prevent 'xmlns redefined' error
#         svg1_content = re.sub(r'\s+xmlns="[^"]+"', '', svg1_content, count=1)
#         svg2_content = re.sub(r'\s+xmlns="[^"]+"', '', svg2_content, count=1)

#         merged_svg = merge_and_fit_svgs(svg1_content, svg2_content, TARGET_PAGE_WIDTH, TARGET_PAGE_HEIGHT)

#         # Display the merged SVG
#         st.subheader("Merged SVG (Fitted to Page)")
#         st.markdown(
#             f'<div style="background:#fff;border:1px solid #ddd">{merged_svg}</div>',
#             unsafe_allow_html=True
#         )

#         # Provide download link
#         st.download_button(
#             "Download Merged SVG",
#             data=merged_svg,
#             file_name="merged.svg",
#             mime="image/svg+xml"
#         )

# if __name__ == "__main__":
#     main()

























































# import streamlit as st
# import xml.etree.ElementTree as ET
# import re

# TARGET_PAGE_WIDTH = 800
# TARGET_PAGE_HEIGHT = 1000

# def get_vb_wh(root):
#     vb = root.get('viewBox')
#     if vb:
#         vb = list(map(float, vb.split()))
#         width = vb[2]
#         height = vb[3]
#     else:
#         width = float(root.get('width', '100'))
#         height = float(root.get('height', '100'))
#         vb = [0, 0, width, height]
#     return vb, width, height

# def scale_text_fontsize(elem, scale):
#     # Recursively scale font-size attributes in all text nodes
#     for child in elem.iter():
#         if child.tag.endswith('text'):
#             # font-size in attribute
#             if 'font-size' in child.attrib:
#                 try:
#                     fs = float(child.attrib['font-size'])
#                     child.attrib['font-size'] = str(fs * scale)
#                 except Exception:
#                     pass
#             # handle style attribute
#             if 'style' in child.attrib:
#                 style = child.attrib['style']
#                 new_style = re.sub(
#                     r'(font-size\s*:\s*)([0-9.]+)(px)?',
#                     lambda m: f"{m.group(1)}{float(m.group(2)) * scale}{m.group(3) or ''}",
#                     style
#                 )
#                 child.attrib['style'] = new_style

# def merge_and_fit_svgs(svg1_content, svg2_content, target_width, target_height, text_scale=1.0):
#     root1 = ET.fromstring(svg1_content)
#     root2 = ET.fromstring(svg2_content)

#     vb1, width1, height1 = get_vb_wh(root1)
#     vb2, width2, height2 = get_vb_wh(root2)

#     # Scale factor to match width2
#     scale1 = width2 / width1 if width1 > 0 else 1.0
#     scaled_height1 = height1 * scale1

#     merged_width = width2
#     merged_height = scaled_height1 + height2

#     # Scale all text font-sizes in the first SVG to match width2
#     scale_text_fontsize(root1, scale1)

#     svg_ns = "http://www.w3.org/2000/svg"
#     ET.register_namespace('', svg_ns)

#     # The merged SVG, with viewBox covering the merged content
#     merged_group = ET.Element('g')

#     # First SVG's children, scaled to match width2
#     g1 = ET.Element('g', {'transform': f'scale({scale1})'})
#     for elem in list(root1):
#         g1.append(elem)
#     merged_group.append(g1)

#     # Second SVG's children, shifted down by scaled height1
#     g2 = ET.Element('g', {'transform': f'translate(0,{scaled_height1})'})
#     for elem in list(root2):
#         g2.append(elem)
#     merged_group.append(g2)

#     # Calculate scale to fit merged content inside target "page"
#     scale_to_fit = min(target_width / merged_width, target_height / merged_height)

#     # Outer SVG element with fixed size and viewBox
#     final_svg = ET.Element('svg', {
#         'xmlns': svg_ns,
#         'width': str(target_width),
#         'height': str(target_height),
#         'viewBox': f"0 0 {target_width} {target_height}"
#     })

#     # Center the merged group
#     translate_x = (target_width - merged_width * scale_to_fit) / 2
#     translate_y = (target_height - merged_height * scale_to_fit) / 2

#     outer_g = ET.Element('g', {'transform': f'translate({translate_x},{translate_y}) scale({scale_to_fit})'})
#     outer_g.append(merged_group)
#     final_svg.append(outer_g)

#     # === NEW: Shrink all text font-sizes by text_scale (0.5 for half) ===
#     scale_text_fontsize(final_svg, text_scale)

#     return ET.tostring(final_svg, encoding='unicode', method='xml')

# def main():
#     st.title("SVG Merger (Fit Both SVGs on a Single Page, Text Shrunk)")
#     st.write(f"Both SVGs will be merged and scaled to fit within {TARGET_PAGE_WIDTH}x{TARGET_PAGE_HEIGHT} px. All text will be half size.")

#     uploaded_file1 = st.file_uploader("Choose first SVG file", type="svg")
#     uploaded_file2 = st.file_uploader("Choose second SVG file", type="svg")

#     if uploaded_file1 and uploaded_file2:
#         svg1_content = uploaded_file1.read().decode("utf-8")
#         svg2_content = uploaded_file2.read().decode("utf-8")

#         # Remove any inner xmlns attributes to prevent 'xmlns redefined' error
#         svg1_content = re.sub(r'\s+xmlns="[^"]+"', '', svg1_content, count=1)
#         svg2_content = re.sub(r'\s+xmlns="[^"]+"', '', svg2_content, count=1)

#         merged_svg = merge_and_fit_svgs(svg1_content, svg2_content, TARGET_PAGE_WIDTH, TARGET_PAGE_HEIGHT, text_scale=0.5)

#         # Display the merged SVG
#         st.subheader("Merged SVG (Fitted, Text Shrunk)")
#         st.markdown(
#             f'<div style="background:#fff;border:1px solid #ddd">{merged_svg}</div>',
#             unsafe_allow_html=True
#         )

#         # Provide download link
#         st.download_button(
#             "Download Merged SVG",
#             data=merged_svg,
#             file_name="merged.svg",
#             mime="image/svg+xml"
#         )

# if __name__ == "__main__":
#     main()





































# import streamlit as st
# import xml.etree.ElementTree as ET
# import re

# TARGET_PAGE_WIDTH = 800
# TARGET_PAGE_HEIGHT = 1000

# def get_vb_wh(root):
#     vb = root.get('viewBox')
#     if vb:
#         vb = list(map(float, vb.split()))
#         width = vb[2]
#         height = vb[3]
#     else:
#         width = float(root.get('width', '100'))
#         height = float(root.get('height', '100'))
#         vb = [0, 0, width, height]
#     return vb, width, height

# def scale_text_fontsize(elem, scale):
#     # Recursively scale font-size attributes in all text nodes
#     for child in elem.iter():
#         tag = child.tag.split('}')[-1]
#         if tag in {'text', 'tspan', 'desc', 'title'}:
#             # font-size in attribute
#             if 'font-size' in child.attrib:
#                 try:
#                     fs = float(child.attrib['font-size'])
#                     child.attrib['font-size'] = str(fs * scale)
#                 except Exception:
#                     pass
#             # handle style attribute
#             if 'style' in child.attrib:
#                 style = child.attrib['style']
#                 new_style = re.sub(
#                     r'(font-size\s*:\s*)([0-9.]+)(px)?',
#                     lambda m: f"{m.group(1)}{float(m.group(2)) * scale}{m.group(3) or ''}",
#                     style
#                 )
#                 child.attrib['style'] = new_style

# def replace_text_with_updated(elem):
#     # Replace text for these tags (add more if needed)
#     text_tags = {'text', 'tspan', 'desc', 'title'}
#     for child in elem.iter():
#         tag = child.tag.split('}')[-1]  # Handle namespaces
#         if tag in text_tags:
#             child.text = 'updated'

# def merge_and_fit_svgs(svg1_content, svg2_content, target_width, target_height, text_scale=1.0):
#     root1 = ET.fromstring(svg1_content)
#     root2 = ET.fromstring(svg2_content)

#     # Replace all text in the second SVG with 'updated'
#     replace_text_with_updated(root2)

#     vb1, width1, height1 = get_vb_wh(root1)
#     vb2, width2, height2 = get_vb_wh(root2)

#     # Scale factor to match width2
#     scale1 = width2 / width1 if width1 > 0 else 1.0
#     scaled_height1 = height1 * scale1

#     merged_width = width2
#     merged_height = scaled_height1 + height2

#     # Scale all text font-sizes in the first SVG to match width2
#     scale_text_fontsize(root1, scale1)

#     svg_ns = "http://www.w3.org/2000/svg"
#     ET.register_namespace('', svg_ns)

#     # The merged SVG, with viewBox covering the merged content
#     merged_group = ET.Element('g')

#     # First SVG's children, scaled to match width2
#     g1 = ET.Element('g', {'transform': f'scale({scale1})'})
#     for elem in list(root1):
#         g1.append(elem)
#     merged_group.append(g1)

#     # Second SVG's children, shifted down by scaled height1
#     g2 = ET.Element('g', {'transform': f'translate(0,{scaled_height1})'})
#     for elem in list(root2):
#         g2.append(elem)
#     merged_group.append(g2)

#     # Calculate scale to fit merged content inside target "page"
#     scale_to_fit = min(target_width / merged_width, target_height / merged_height)

#     # Outer SVG element with fixed size and viewBox
#     final_svg = ET.Element('svg', {
#         'xmlns': svg_ns,
#         'width': str(target_width),
#         'height': str(target_height),
#         'viewBox': f"0 0 {target_width} {target_height}"
#     })

#     # Center the merged group
#     translate_x = (target_width - merged_width * scale_to_fit) / 2
#     translate_y = (target_height - merged_height * scale_to_fit) / 2

#     outer_g = ET.Element('g', {'transform': f'translate({translate_x},{translate_y}) scale({scale_to_fit})'})
#     outer_g.append(merged_group)
#     final_svg.append(outer_g)

#     # Shrink all text font-sizes by text_scale (0.5 for half)
#     scale_text_fontsize(final_svg, text_scale)

#     return ET.tostring(final_svg, encoding='unicode', method='xml')

# def main():
#     st.title("SVG Merger (Fit Both SVGs, Text Shrunk, Replace Second SVG Text)")
#     st.write(
#         f"Both SVGs will be merged and scaled to fit within {TARGET_PAGE_WIDTH}x{TARGET_PAGE_HEIGHT} px.\n"
#         f"All text will be shrunk to half size, and all text in the second SVG will be replaced with 'updated'."
#     )

#     uploaded_file1 = st.file_uploader("Choose first SVG file", type="svg")
#     uploaded_file2 = st.file_uploader("Choose second SVG file", type="svg")

#     if uploaded_file1 and uploaded_file2:
#         svg1_content = uploaded_file1.read().decode("utf-8")
#         svg2_content = uploaded_file2.read().decode("utf-8")

#         # Remove any inner xmlns attributes to prevent 'xmlns redefined' error
#         svg1_content = re.sub(r'\s+xmlns="[^"]+"', '', svg1_content, count=1)
#         svg2_content = re.sub(r'\s+xmlns="[^"]+"', '', svg2_content, count=1)

#         merged_svg = merge_and_fit_svgs(
#             svg1_content, svg2_content,
#             TARGET_PAGE_WIDTH, TARGET_PAGE_HEIGHT,
#             text_scale=0.5
#         )

#         # Display the merged SVG
#         st.subheader("Merged SVG (Fitted, Text Shrunk, Second Text Replaced)")
#         st.markdown(
#             f'<div style="background:#fff;border:1px solid #ddd">{merged_svg}</div>',
#             unsafe_allow_html=True
#         )

#         # Provide download link
#         st.download_button(
#             "Download Merged SVG",
#             data=merged_svg,
#             file_name="merged.svg",
#             mime="image/svg+xml"
#         )

# if __name__ == "__main__":
#     main()









######## Removing green table ###############


import streamlit as st
from lxml import etree
from io import BytesIO

def remove_ids_from_svg(svg_bytes, ids_to_remove):
    tree = etree.parse(BytesIO(svg_bytes))
    root = tree.getroot()

    for element_id in ids_to_remove:
        # Find element with that id anywhere in the SVG
        for elem in root.xpath('.//*[@id="%s"]' % element_id):
            parent = elem.getparent()
            if parent is not None:
                parent.remove(elem)
    # Save to BytesIO
    output = BytesIO()
    tree.write(output, xml_declaration=True, encoding="UTF-8")
    return output.getvalue()

st.title("SVG Cleaner")

uploaded_file = st.file_uploader("Upload your SVG file", type=["svg"])

default_ids = "id76,id77,id67,id68,id69,id70,id71,id72,id73,id74,id75,id78,id79,id80,id81,id82,id83"
ids_str = st.text_input("IDs to remove (comma-separated)", value=default_ids)
ids_to_remove = [i.strip() for i in ids_str.split(",") if i.strip()]

if uploaded_file is not None:
    svg_bytes = uploaded_file.read()
    cleaned_svg = remove_ids_from_svg(svg_bytes, ids_to_remove)
    st.success("SVG cleaned! Download below.")
    st.download_button(
        label="Download cleaned SVG",
        data=cleaned_svg,
        file_name="cleaned.svg",
        mime="image/svg+xml"
    )
















# import streamlit as st
# from lxml import etree
# from io import BytesIO
# import xml.etree.ElementTree as ET
# import re

# TARGET_PAGE_WIDTH = 800
# TARGET_PAGE_HEIGHT = 1000

# def remove_ids_from_svg(svg_bytes, ids_to_remove):
#     tree = etree.parse(BytesIO(svg_bytes))
#     root = tree.getroot()
#     for element_id in ids_to_remove:
#         for elem in root.xpath('.//*[@id="%s"]' % element_id):
#             parent = elem.getparent()
#             if parent is not None:
#                 parent.remove(elem)
#     output = BytesIO()
#     tree.write(output, xml_declaration=True, encoding="UTF-8")
#     return output.getvalue()

# def get_vb_wh(root):
#     vb = root.get('viewBox')
#     if vb:
#         vb = list(map(float, vb.split()))
#         width = vb[2]
#         height = vb[3]
#     else:
#         width = float(root.get('width', '100'))
#         height = float(root.get('height', '100'))
#         vb = [0, 0, width, height]
#     return vb, width, height

# def scale_text_fontsize(elem, scale):
#     # Recursively scale font-size attributes in all text nodes
#     for child in elem.iter():
#         tag = child.tag.split('}')[-1]
#         if tag in {'text', 'tspan', 'desc', 'title'}:
#             if 'font-size' in child.attrib:
#                 try:
#                     fs = float(child.attrib['font-size'])
#                     child.attrib['font-size'] = str(fs * scale)
#                 except Exception:
#                     pass
#             if 'style' in child.attrib:
#                 style = child.attrib['style']
#                 new_style = re.sub(
#                     r'(font-size\s*:\s*)([0-9.]+)(px)?',
#                     lambda m: f"{m.group(1)}{float(m.group(2)) * scale}{m.group(3) or ''}",
#                     style
#                 )
#                 child.attrib['style'] = new_style

# def replace_text_with_updated(elem):
#     text_tags = {'text', 'tspan', 'desc', 'title'}
#     for child in elem.iter():
#         tag = child.tag.split('}')[-1]
#         if tag in text_tags:
#             child.text = 'updated'

# def merge_and_fit_svgs(svg1_content, svg2_content, target_width, target_height, text_scale=1.0):
#     root1 = ET.fromstring(svg1_content)
#     root2 = ET.fromstring(svg2_content)
#     replace_text_with_updated(root2)
#     vb1, width1, height1 = get_vb_wh(root1)
#     vb2, width2, height2 = get_vb_wh(root2)
#     scale1 = width2 / width1 if width1 > 0 else 1.0
#     scaled_height1 = height1 * scale1
#     merged_width = width2
#     merged_height = scaled_height1 + height2
#     scale_text_fontsize(root1, scale1)
#     svg_ns = "http://www.w3.org/2000/svg"
#     ET.register_namespace('', svg_ns)
#     merged_group = ET.Element('g')
#     g1 = ET.Element('g', {'transform': f'scale({scale1})'})
#     for elem in list(root1):
#         g1.append(elem)
#     merged_group.append(g1)
#     g2 = ET.Element('g', {'transform': f'translate(0,{scaled_height1})'})
#     for elem in list(root2):
#         g2.append(elem)
#     merged_group.append(g2)
#     scale_to_fit = min(target_width / merged_width, target_height / merged_height)
#     final_svg = ET.Element('svg', {
#         'xmlns': svg_ns,
#         'width': str(target_width),
#         'height': str(target_height),
#         'viewBox': f"0 0 {target_width} {target_height}"
#     })
#     translate_x = (target_width - merged_width * scale_to_fit) / 2
#     translate_y = (target_height - merged_height * scale_to_fit) / 2
#     outer_g = ET.Element('g', {'transform': f'translate({translate_x},{translate_y}) scale({scale_to_fit})'})
#     outer_g.append(merged_group)
#     final_svg.append(outer_g)
#     scale_text_fontsize(final_svg, text_scale)
#     return ET.tostring(final_svg, encoding='unicode', method='xml')

# # Streamlit UI
# st.title("SVG Cleaner & Merger")

# st.write(
#     f"Upload two SVGs. The first will be cleaned (remove elements by id), "
#     f"then both will be merged and fitted into {TARGET_PAGE_WIDTH}x{TARGET_PAGE_HEIGHT} px. "
#     "All text will be shrunk to half size, and all text in the second SVG will be replaced with 'updated'."
# )

# uploaded_file1 = st.file_uploader("Upload first SVG (will be cleaned)", type="svg", key="svg1")
# uploaded_file2 = st.file_uploader("Upload second SVG", type="svg", key="svg2")

# default_ids = "group58-238"
# ids_str = st.text_input("IDs to remove from first SVG (comma-separated)", value=default_ids)
# ids_to_remove = [i.strip() for i in ids_str.split(",") if i.strip()]

# if uploaded_file1 and uploaded_file2:
#     svg1_bytes = uploaded_file1.read()
#     svg2_bytes = uploaded_file2.read()
#     # Clean first SVG
#     cleaned_svg1_bytes = remove_ids_from_svg(svg1_bytes, ids_to_remove)
#     svg1_content = cleaned_svg1_bytes.decode("utf-8")
#     svg2_content = svg2_bytes.decode("utf-8")
#     # Remove any inner xmlns attributes to prevent 'xmlns redefined' error
#     svg1_content = re.sub(r'\s+xmlns="[^"]+"', '', svg1_content, count=1)
#     svg2_content = re.sub(r'\s+xmlns="[^"]+"', '', svg2_content, count=1)
#     # Merge
#     merged_svg = merge_and_fit_svgs(
#         svg1_content, svg2_content,
#         TARGET_PAGE_WIDTH, TARGET_PAGE_HEIGHT,
#         text_scale=0.5
#     )
#     st.subheader("Merged SVG (Cleaned, Fitted, Text Shrunk, Second Text Replaced)")
#     st.markdown(
#         f'<div style="background:#fff;border:1px solid #ddd">{merged_svg}</div>',
#         unsafe_allow_html=True
#     )
#     st.download_button(
#         "Download Merged SVG",
#         data=merged_svg,
#         file_name="merged.svg",
#         mime="image/svg+xml"
#     )



















# import streamlit as st
# from lxml import etree
# from io import BytesIO

# def remove_ids_from_svg(svg_bytes, ids_to_remove):
#     tree = etree.parse(BytesIO(svg_bytes))
#     root = tree.getroot()

#     for element_id in ids_to_remove:
#         # Find element with that id anywhere in the SVG
#         for elem in root.xpath('.//*[@id="%s"]' % element_id):
#             parent = elem.getparent()
#             if parent is not None:
#                 parent.remove(elem)
#     # Save to BytesIO
#     output = BytesIO()
#     tree.write(output, xml_declaration=True, encoding="UTF-8")
#     return output.getvalue()

# st.title("SVG Cleaner")

# uploaded_file = st.file_uploader("Upload your SVG file", type=["svg"])

# default_ids = "group58-238"
# ids_str = st.text_input("IDs to remove (comma-separated)", value=default_ids)
# ids_to_remove = [i.strip() for i in ids_str.split(",") if i.strip()]

# if uploaded_file is not None:
#     svg_bytes = uploaded_file.read()
#     cleaned_svg = remove_ids_from_svg(svg_bytes, ids_to_remove)
#     st.success("SVG cleaned! Download below.")
#     st.download_button(
#         label="Download cleaned SVG",
#         data=cleaned_svg,
#         file_name="cleaned.svg",
#         mime="image/svg+xml"
#     )























# import streamlit as st
# from lxml import etree
# from io import BytesIO
# import xml.etree.ElementTree as ET
# import re

# TARGET_PAGE_WIDTH = 800
# TARGET_PAGE_HEIGHT = 1000

# def remove_ids_from_svg(svg_bytes, ids_to_remove):
#     tree = etree.parse(BytesIO(svg_bytes))
#     root = tree.getroot()
#     for element_id in ids_to_remove:
#         for elem in root.xpath('.//*[@id="%s"]' % element_id):
#             parent = elem.getparent()
#             if parent is not None:
#                 parent.remove(elem)
#     output = BytesIO()
#     tree.write(output, xml_declaration=True, encoding="UTF-8")
#     return output.getvalue()

# def get_vb_wh(root):
#     vb = root.get('viewBox')
#     if vb:
#         vb = list(map(float, vb.split()))
#         width = vb[2]
#         height = vb[3]
#     else:
#         width = float(root.get('width', '100'))
#         height = float(root.get('height', '100'))
#         vb = [0, 0, width, height]
#     return vb, width, height

# def scale_text_fontsize(elem, scale):
#     # Recursively scale font-size attributes in all text nodes
#     for child in elem.iter():
#         tag = child.tag.split('}')[-1]
#         if tag in {'text', 'tspan', 'desc', 'title'}:
#             if 'font-size' in child.attrib:
#                 try:
#                     fs = float(child.attrib['font-size'])
#                     child.attrib['font-size'] = str(fs * scale)
#                 except Exception:
#                     pass
#             if 'style' in child.attrib:
#                 style = child.attrib['style']
#                 new_style = re.sub(
#                     r'(font-size\s*:\s*)([0-9.]+)(px)?',
#                     lambda m: f"{m.group(1)}{float(m.group(2)) * scale}{m.group(3) or ''}",
#                     style
#                 )
#                 child.attrib['style'] = new_style

# def merge_and_fit_svgs(svg1_content, svg2_content, target_width, target_height, text_scale=1.0):
#     root1 = ET.fromstring(svg1_content)
#     root2 = ET.fromstring(svg2_content)
#     vb1, width1, height1 = get_vb_wh(root1)
#     vb2, width2, height2 = get_vb_wh(root2)
#     scale1 = width2 / width1 if width1 > 0 else 1.0
#     scaled_height1 = height1 * scale1
#     merged_width = width2
#     merged_height = scaled_height1 + height2

#     # Scale all text font-sizes in the first SVG to match width2
#     scale_text_fontsize(root1, scale1)
#     # Scale all text font-sizes in the second SVG by 1.0 (no change), but shrink both by text_scale after merge

#     svg_ns = "http://www.w3.org/2000/svg"
#     ET.register_namespace('', svg_ns)

#     # The merged SVG, with viewBox covering the merged content
#     merged_group = ET.Element('g')

#     # First SVG's children, scaled to match width2
#     g1 = ET.Element('g', {'transform': f'scale({scale1})'})
#     for elem in list(root1):
#         g1.append(elem)
#     merged_group.append(g1)

#     # Second SVG's children, shifted down by scaled height1
#     g2 = ET.Element('g', {'transform': f'translate(0,{scaled_height1})'})
#     for elem in list(root2):
#         g2.append(elem)
#     merged_group.append(g2)

#     # Calculate scale to fit merged content inside target "page"
#     scale_to_fit = min(target_width / merged_width, target_height / merged_height)

#     # Outer SVG element with fixed size and viewBox
#     final_svg = ET.Element('svg', {
#         'xmlns': svg_ns,
#         'width': str(target_width),
#         'height': str(target_height),
#         'viewBox': f"0 0 {target_width} {target_height}"
#     })

#     # Center the merged group
#     translate_x = (target_width - merged_width * scale_to_fit) / 2
#     translate_y = (target_height - merged_height * scale_to_fit) / 2

#     outer_g = ET.Element('g', {'transform': f'translate({translate_x},{translate_y}) scale({scale_to_fit})'})
#     outer_g.append(merged_group)
#     final_svg.append(outer_g)

#     # Shrink all text font-sizes by text_scale (0.5 for half) **AFTER** everything else (on the final SVG!)
#     scale_text_fontsize(final_svg, text_scale)

#     return ET.tostring(final_svg, encoding='unicode', method='xml')

# # Streamlit UI
# st.title("SVG Cleaner & Merger")

# st.write(
#     f"Upload two SVGs. The first will be cleaned (remove elements by id), "
#     f"then both will be merged and fitted into {TARGET_PAGE_WIDTH}x{TARGET_PAGE_HEIGHT} px. "
#     "All text will be shrunk to half size."
# )

# uploaded_file1 = st.file_uploader("Upload first SVG (will be cleaned)", type="svg", key="svg1")
# uploaded_file2 = st.file_uploader("Upload second SVG", type="svg", key="svg2")

# default_ids = "group58-238"
# ids_str = st.text_input("IDs to remove from first SVG (comma-separated)", value=default_ids)
# ids_to_remove = [i.strip() for i in ids_str.split(",") if i.strip()]

# if uploaded_file1 and uploaded_file2:
#     svg1_bytes = uploaded_file1.read()
#     svg2_bytes = uploaded_file2.read()
#     # Clean first SVG
#     cleaned_svg1_bytes = remove_ids_from_svg(svg1_bytes, ids_to_remove)
#     svg1_content = cleaned_svg1_bytes.decode("utf-8")
#     svg2_content = svg2_bytes.decode("utf-8")
#     # Remove any inner xmlns attributes to prevent 'xmlns redefined' error
#     svg1_content = re.sub(r'\s+xmlns="[^"]+"', '', svg1_content, count=1)
#     svg2_content = re.sub(r'\s+xmlns="[^"]+"', '', svg2_content, count=1)
#     # Merge
#     merged_svg = merge_and_fit_svgs(
#         svg1_content, svg2_content,
#         TARGET_PAGE_WIDTH, TARGET_PAGE_HEIGHT,
#         text_scale=0.5
#     )
#     st.subheader("Merged SVG (Cleaned, Fitted, Text Shrunk)")
#     st.markdown(
#         f'<div style="background:#fff;border:1px solid #ddd">{merged_svg}</div>',
#         unsafe_allow_html=True
#     )
#     st.download_button(
#         "Download Merged SVG",
#         data=merged_svg,
#         file_name="merged.svg",
#         mime="image/svg+xml"
#     )

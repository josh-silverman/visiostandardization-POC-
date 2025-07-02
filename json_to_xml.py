import xml.etree.ElementTree as ET
import json
import os

# --- Namespaces ---
NS = {
    'visio': 'http://schemas.microsoft.com/office/visio/2012/main'
}
ET.register_namespace('', NS['visio'])  # Needed for pretty output

def set_attributes(elem, attr_dict):
    for k in list(elem.attrib.keys()):
        del elem.attrib[k]
    for k, v in attr_dict.items():
        elem.set(k, v)

def recreate_cells(parent_elem, cells):
    for cell in list(parent_elem.findall('visio:Cell', NS)):
        parent_elem.remove(cell)
    for cell in cells:
        cell_elem = ET.Element('{%s}Cell' % NS['visio'])
        for k, v in cell.items():
            cell_elem.set(k, v)
        parent_elem.append(cell_elem)

def recreate_rows(section_elem, rows):
    for row in list(section_elem.findall('visio:Row', NS)):
        section_elem.remove(row)
    for row in rows:
        row_elem = ET.Element('{%s}Row' % NS['visio'])
        if '@attrs' in row:
            for k, v in row['@attrs'].items():
                row_elem.set(k, v)
        if 'Cells' in row:
            recreate_cells(row_elem, row['Cells'])
        section_elem.append(row_elem)

def recreate_sections(shape_elem, sections):
    for section in list(shape_elem.findall('visio:Section', NS)):
        shape_elem.remove(section)
    for sec in sections:
        sec_elem = ET.Element('{%s}Section' % NS['visio'])
        if '@attrs' in sec:
            for k, v in sec['@attrs'].items():
                sec_elem.set(k, v)
        if 'Rows' in sec:
            recreate_rows(sec_elem, sec['Rows'])
        shape_elem.append(sec_elem)

def recreate_text(shape_elem, text_xml):
    for text_elem in list(shape_elem.findall('visio:Text', NS)):
        shape_elem.remove(text_elem)
    if text_xml:
        try:
            text_elem = ET.fromstring(text_xml)
            shape_elem.append(text_elem)
        except Exception:
            text_elem = ET.Element('{%s}Text' % NS['visio'])
            text_elem.text = text_xml
            shape_elem.append(text_elem)

def update_shape_with_theme(shape_elem, jshape):
    set_attributes(shape_elem, jshape['attributes'])
    recreate_cells(shape_elem, jshape['Cells'])
    recreate_sections(shape_elem, jshape['Sections'])
    recreate_text(shape_elem, jshape['Text'])

def update_colors(root, jcolors):
    colors_elem = root.find('visio:Colors', NS)
    if colors_elem is not None:
        for color_entry in list(colors_elem.findall('visio:ColorEntry', NS)):
            colors_elem.remove(color_entry)
        for jcolor in jcolors:
            color_elem = ET.Element('{%s}ColorEntry' % NS['visio'])
            color_elem.set('IX', str(jcolor['IX']))
            color_elem.set('RGB', jcolor['RGB'])
            colors_elem.append(color_elem)

def main():
    # Load edited JSON
    with open("page1_standardized.json", "r", encoding="utf-8") as f:
        edited_json = json.load(f)

    # Update page1.xml
    page1_xml_path = os.path.join("output_xml", "visio", "pages", "page1.xml")
    tree = ET.parse(page1_xml_path)
    root = tree.getroot()

    shapes_elem = root.find('visio:Shapes', NS)
    if shapes_elem is not None:
        for jshape in edited_json['shapes']:
            shape_id = jshape['attributes']['ID']
            xml_shape = shapes_elem.find(f'visio:Shape[@ID="{shape_id}"]', NS)
            if xml_shape is not None:
                update_shape_with_theme(xml_shape, jshape)

    tree.write(page1_xml_path, encoding="utf-8", xml_declaration=True)
    print(f"Updated XML saved to {page1_xml_path}")

    # Update document.xml with color information
    document_xml_path = os.path.join("output_xml", "visio", "document.xml")
    document_tree = ET.parse(document_xml_path)
    document_root = document_tree.getroot()
    update_colors(document_root, edited_json.get('colors', []))

    document_tree.write(document_xml_path, encoding="utf-8", xml_declaration=True)
    print(f"Updated XML saved to {document_xml_path}")

if __name__ == "__main__":
    main()

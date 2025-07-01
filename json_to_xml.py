import xml.etree.ElementTree as ET
import json
import os

# --- Namespaces ---
NS = {
    'visio': 'http://schemas.microsoft.com/office/visio/2012/main'
}
ET.register_namespace('', NS['visio'])  # Needed for pretty output

def set_attributes(elem, attr_dict):
    # Overwrite all attributes
    for k in list(elem.attrib.keys()):
        del elem.attrib[k]
    for k, v in attr_dict.items():
        elem.set(k, v)

def recreate_cells(parent_elem, cells):
    # Remove all existing <Cell> and add new ones
    for cell in list(parent_elem.findall('visio:Cell', NS)):
        parent_elem.remove(cell)
    for cell in cells:
        cell_elem = ET.Element('{%s}Cell' % NS['visio'])
        for k, v in cell.items():
            cell_elem.set(k, v)
        parent_elem.append(cell_elem)

def recreate_rows(section_elem, rows):
    # Remove all existing <Row> and add new ones
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
    # Remove all existing <Section> and add new ones
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
    # Remove all existing <Text>
    for text_elem in list(shape_elem.findall('visio:Text', NS)):
        shape_elem.remove(text_elem)
    if text_xml:
        # text_xml is a string, so parse and append as XML
        try:
            text_elem = ET.fromstring(text_xml)
            shape_elem.append(text_elem)
        except Exception:
            # fallback to plain text if not well-formed XML
            text_elem = ET.Element('{%s}Text' % NS['visio'])
            text_elem.text = text_xml
            shape_elem.append(text_elem)

def update_shape(shape_elem, jshape):
    set_attributes(shape_elem, jshape['attributes'])
    recreate_cells(shape_elem, jshape['Cells'])
    recreate_sections(shape_elem, jshape['Sections'])
    recreate_text(shape_elem, jshape['Text'])

def main():
    # --- Load edited JSON ---
    with open("page1_standardized.json", "r", encoding="utf-8") as f:
        edited_json = json.load(f)

    # --- Load original XML ---
    page1_xml_path = os.path.join("output_xml", "visio", "pages", "page1.xml")
    tree = ET.parse(page1_xml_path)
    root = tree.getroot()

    # --- Update shapes ---
    shapes_elem = root.find('visio:Shapes', NS)
    if shapes_elem is not None:
        # Build a map for quick lookup
        xml_shape_map = {s.get('ID'): s for s in shapes_elem.findall('visio:Shape', NS)}
        for jshape in edited_json['shapes']:
            shape_id = jshape['attributes']['ID']
            xml_shape = xml_shape_map.get(shape_id)
            if xml_shape is not None:
                update_shape(xml_shape, jshape)
            else:
                # Optionally: create new shapes if they exist in JSON but not in XML
                pass

    # --- Update connectors ---
    connects_elem = root.find('visio:Connects', NS)
    if connects_elem is not None:
        # Remove all existing <Connect>
        for conn in list(connects_elem.findall('visio:Connect', NS)):
            connects_elem.remove(conn)
        # Add new ones from JSON
        for jconn in edited_json.get('connectors', []):
            conn_elem = ET.Element('{%s}Connect' % NS['visio'])
            for k, v in jconn.items():
                conn_elem.set(k, v)
            connects_elem.append(conn_elem)

    # --- Save updated XML ---
    out_path = os.path.join("output_xml", "visio", "pages", "page1.xml")
    tree.write(out_path, encoding="utf-8", xml_declaration=True)
    print(f"Updated XML saved to {out_path}")

if __name__ == "__main__":
    main()

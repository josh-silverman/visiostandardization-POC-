import xml.etree.ElementTree as ET
import json
import os

# --- Namespaces ---
NS = {
    'visio': 'http://schemas.microsoft.com/office/visio/2012/main'
}
ET.register_namespace('', NS['visio'])  # Needed for pretty output

POSITION_FIELDS = {'PinX', 'PinY', 'Width', 'Height'}

def set_attributes(elem, attr_dict):
    """Set attributes for an XML element based on a dictionary."""
    for k in list(elem.attrib.keys()):
        del elem.attrib[k]
    for k, v in attr_dict.items():
        elem.set(k, v)

def recreate_cells(parent_elem, cells):
    """Recreate <Cell> elements within a parent XML element."""
    for cell in list(parent_elem.findall('visio:Cell', NS)):
        parent_elem.remove(cell)
    found_fields = set()
    for cell_dict in cells:
        cell_elem = ET.Element('{%s}Cell' % NS['visio'])
        for k, v in cell_dict.items():
            cell_elem.set(k, str(v))
        parent_elem.append(cell_elem)
        n = cell_dict.get("N")
        if n in POSITION_FIELDS:
            found_fields.add(n)
    return found_fields

def recreate_rows(section_elem, rows):
    """Recreate <Row> elements within a <Section> XML element."""
    for row in list(section_elem.findall('visio:Row', NS)):
        section_elem.remove(row)
    for row in rows:
        row_elem = ET.Element('{%s}Row' % NS['visio'])
        if '@attrs' in row:
            for k, v in row['@attrs'].items():
                row_elem.set(k, v)
        if 'attributes' in row:
            for k, v in row['attributes'].items():
                row_elem.set(k, v)
        if 'Cells' in row:
            recreate_cells(row_elem, row['Cells'])
        section_elem.append(row_elem)

def recreate_sections(shape_elem, sections):
    """Recreate <Section> elements within a <Shape> XML element."""
    for section in list(shape_elem.findall('visio:Section', NS)):
        shape_elem.remove(section)
    for sec in sections:
        sec_elem = ET.Element('{%s}Section' % NS['visio'])
        if '@attrs' in sec:
            for k, v in sec['@attrs'].items():
                sec_elem.set(k, v)
        if 'attributes' in sec:
            for k, v in sec['attributes'].items():
                sec_elem.set(k, v)
        if 'Rows' in sec:
            recreate_rows(sec_elem, sec['Rows'])
        shape_elem.append(sec_elem)

def recreate_text(shape_elem, text_xml):
    """Recreate <Text> element within a <Shape> XML element."""
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

def recreate_shapes(parent_elem, shapes_json):
    """Recursively update child <Shapes> elements for nested shapes/groups."""
    # Remove existing <Shapes> element(s)
    for shapes_elem in list(parent_elem.findall('visio:Shapes', NS)):
        parent_elem.remove(shapes_elem)
    if shapes_json:
        shapes_elem = ET.Element('{%s}Shapes' % NS['visio'])
        for jshape in shapes_json:
            # Find existing child <Shape> if present, else create new
            shape_id = jshape.get('attributes', {}).get('ID')
            shape_elem = ET.Element('{%s}Shape' % NS['visio'])
            set_attributes(shape_elem, jshape.get('attributes', {}))
            recreate_cells(shape_elem, jshape.get('Cells', []))
            recreate_sections(shape_elem, jshape.get('Sections', []))
            recreate_text(shape_elem, jshape.get('Text', None))
            # Recursive for further nested Shapes
            if 'Shapes' in jshape:
                recreate_shapes(shape_elem, jshape['Shapes'])
            shapes_elem.append(shape_elem)
        parent_elem.append(shapes_elem)

def update_shape(shape_elem, jshape):
    """Update a <Shape> XML element based on JSON data."""
    attr_dict = jshape.get('attributes', {})
    set_attributes(shape_elem, attr_dict)
    found_fields = recreate_cells(shape_elem, jshape.get('Cells', []))
    recreate_sections(shape_elem, jshape.get('Sections', []))
    recreate_text(shape_elem, jshape.get('Text', None))
    # Recursively update nested shapes/groups if present
    if 'Shapes' in jshape:
        recreate_shapes(shape_elem, jshape['Shapes'])
    # Warn if any position field is missing
    missing = POSITION_FIELDS - found_fields
    if missing:
        print(f"WARNING: Shape ID {attr_dict.get('ID', '?')} is missing position fields: {missing}")

def update_colors(root, jcolors):
    """Update <Colors> in the XML based on JSON data."""
    colors_elem = root.find('visio:Colors', NS)
    if colors_elem is not None:
        for color_entry in list(colors_elem.findall('visio:ColorEntry', NS)):
            colors_elem.remove(color_entry)
        for jcolor in jcolors:
            color_elem = ET.Element('{%s}ColorEntry' % NS['visio'])
            color_elem.set('IX', str(jcolor['IX']))
            color_elem.set('RGB', jcolor['RGB'])
            colors_elem.append(color_elem)

def update_connects(root, connectors):
    """Update <Connects> section in the XML based on JSON data."""
    connects_elem = root.find('visio:Connects', NS)
    if connects_elem is not None:
        root.remove(connects_elem)
    if connectors:
        connects_elem = ET.Element('{%s}Connects' % NS['visio'])
        for conn in connectors:
            connect_elem = ET.Element('{%s}Connect' % NS['visio'])
            for k, v in conn.items():
                connect_elem.set(k, str(v))
            connects_elem.append(connect_elem)
        root.append(connects_elem)

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
            shape_id = jshape.get('attributes', {}).get('ID')
            if not shape_id:
                print("WARNING: Shape in JSON missing ID, skipping.")
                continue
            xml_shape = shapes_elem.find(f'visio:Shape[@ID="{shape_id}"]', NS)
            if xml_shape is not None:
                update_shape(xml_shape, jshape)
            else:
                # Optionally create new Shape if not present
                print(f"WARNING: Shape ID {shape_id} not found in XML, skipping.")

    # Update <Connects> from JSON if present
    if 'connectors' in edited_json:
        update_connects(root, edited_json['connectors'])

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

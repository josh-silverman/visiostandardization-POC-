import xml.etree.ElementTree as ET
import json
import os

NS = {
    'visio': 'http://schemas.microsoft.com/office/visio/2012/main',
    'cp': 'http://schemas.openxmlformats.org/officeDocument/2006/custom-properties',
    'vt': 'http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'
}

def parse_masters(masters_xml_path):
    tree = ET.parse(masters_xml_path)
    root = tree.getroot()
    master_map = {}
    for master in root.findall('visio:Master', NS):
        id_ = master.attrib['ID']
        name = master.attrib.get('NameU', master.attrib.get('Name', 'Unknown'))
        master_map[id_] = name
    return master_map

def extract_cells(cell_elems):
    return [{k: cell.attrib.get(k) for k in cell.attrib} for cell in cell_elems]

def extract_section(section_elem):
    sec = {'@attrs': dict(section_elem.attrib)}
    rows = []
    for row in section_elem.findall('visio:Row', NS):
        row_dict = {'@attrs': dict(row.attrib)}
        cells = extract_cells(row.findall('visio:Cell', NS))
        if cells:
            row_dict['Cells'] = cells
        rows.append(row_dict)
    sec['Rows'] = rows
    return sec

def parse_shape(shape_elem, master_map):
    shape = {
        'attributes': dict(shape_elem.attrib),
        'master_type': master_map.get(shape_elem.attrib.get('Master'), 'Unknown'),
        'Cells': extract_cells(shape_elem.findall('visio:Cell', NS)),
        'Sections': [],
        'Text': None
    }
    for section in shape_elem.findall('visio:Section', NS):
        shape['Sections'].append(extract_section(section))
    text_elem = shape_elem.find('visio:Text', NS)
    if text_elem is not None:
        shape['Text'] = ET.tostring(text_elem, encoding='unicode', method='xml')
    return shape

def parse_page(page_xml_path, master_map):
    tree = ET.parse(page_xml_path)
    root = tree.getroot()
    shapes = []
    shapes_elem = root.find('visio:Shapes', NS)
    if shapes_elem is not None:
        for shape_elem in shapes_elem.findall('visio:Shape', NS):
            shapes.append(parse_shape(shape_elem, master_map))
    connectors = []
    connects_elem = root.find('visio:Connects', NS)
    if connects_elem is not None:
        for conn in connects_elem.findall('visio:Connect', NS):
            connectors.append(dict(conn.attrib))
    return shapes, connectors

def parse_custom(custom_xml_path):
    tree = ET.parse(custom_xml_path)
    root = tree.getroot()
    properties = {}
    for prop in root.findall('cp:property', NS):
        name = prop.attrib.get('name')
        vt_elem = next(iter(prop), None)
        value = vt_elem.text if vt_elem is not None else None
        properties[name] = value
    return properties

def parse_colors(document_xml_path):
    tree = ET.parse(document_xml_path)
    root = tree.getroot()
    colors = []
    colors_elem = root.find('visio:Colors', NS)
    if colors_elem is not None:
        for color_entry in colors_elem.findall('visio:ColorEntry', NS):
            ix = color_entry.attrib['IX']
            rgb = color_entry.attrib['RGB']
            colors.append({'IX': ix, 'RGB': rgb})
    return colors

def main():
    masters_xml = os.path.join("output_xml", "visio", "masters", "masters.xml")
    page1_xml = os.path.join("output_xml", "visio", "pages", "page1.xml")
    custom_xml = os.path.join("output_xml", "docProps", "custom.xml")
    document_xml = os.path.join("output_xml", "visio", "document.xml")

    master_map = parse_masters(masters_xml)
    shapes, connectors = parse_page(page1_xml, master_map)
    custom_props = parse_custom(custom_xml)
    colors = parse_colors(document_xml)

    result = {
        "shapes": shapes,
        "connectors": connectors,
        "document_properties": custom_props,
        "colors": colors
    }

    os.makedirs("parse_visio", exist_ok=True)
    with open("parse_visio/page1_extracted.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

import os
import xml.etree.ElementTree as ET
import json
from collections import defaultdict

def get_text_from_elem(elem):
    """Recursively get all text from an XML element, including tails."""
    if elem is None:
        return ""
    text = elem.text or ""
    for child in elem:
        text += get_text_from_elem(child)
        if child.tail:
            text += child.tail
    return text.strip()

def parse_visio_page_xml(xml_path):
    ns = {'visio': 'http://schemas.microsoft.com/office/visio/2012/main'}
    tree = ET.parse(xml_path)
    root = tree.getroot()
    shapes_data = []

    for shape in root.findall('.//visio:Shape', ns):
        shape_id = shape.get('ID')
        shape_name = shape.get('NameU') or shape.get('Name') or ''
        shape_type = shape.get('Type', 'Shape')
        text_elem = shape.find('visio:Text', ns)
        shape_text = get_text_from_elem(text_elem) if text_elem is not None else ''
        shapes_data.append({
            'id': shape_id,
            'name': shape_name,
            'type': shape_type,
            'text': shape_text,
            'master': shape.get('Master')
        })
    return shapes_data

def get_master_name(master_id, masters_dir):
    if not master_id:
        return ""
    master_filename = f"master{master_id}.xml"
    master_path = os.path.join(masters_dir, master_filename)
    if not os.path.exists(master_path):
        return ""
    ns = {'visio': 'http://schemas.microsoft.com/office/visio/2012/main'}
    tree = ET.parse(master_path)
    root = tree.getroot()
    master_name = root.get('NameU') or root.get('Name') or ''
    shape = root.find('.//visio:Shape', ns)
    if shape is not None:
        master_name = shape.get('NameU') or shape.get('Name') or master_name
    return master_name

def parse_visio_connections(xml_path):
    ns = {'visio': 'http://schemas.microsoft.com/office/visio/2012/main'}
    tree = ET.parse(xml_path)
    root = tree.getroot()
    connects = []
    for connect in root.findall('.//visio:Connect', ns):
        from_sheet = connect.get('FromSheet')
        to_sheet = connect.get('ToSheet')
        from_cell = connect.get('FromCell', '')
        to_cell = connect.get('ToCell', '')
        connects.append({
            'from_sheet': from_sheet,
            'to_sheet': to_sheet,
            'from_cell': from_cell,
            'to_cell': to_cell
        })
    return connects

def main():
    pages_dir = os.path.join("output_xml", "visio", "pages")
    masters_dir = os.path.join("output_xml", "visio", "masters")
    if not os.path.exists(pages_dir):
        print(f"Directory does not exist: {pages_dir}")
        return
    page_xmls = [f for f in os.listdir(pages_dir) if f.startswith('page') and f.endswith('.xml')]
    print("Found page XML files:", page_xmls)
    for page_xml in page_xmls:
        xml_path = os.path.join(pages_dir, page_xml)
        print(f"\n--- Parsing {page_xml} ---")
        # Parse shapes
        shapes = parse_visio_page_xml(xml_path)
        shape_dict = {s['id']: s for s in shapes}
        for s in shapes:
            master_name = get_master_name(s['master'], masters_dir) if s['master'] else ''
            if s['text']:
                print(f"SHAPE: ID={s['id']}, Text='{s['text']}', Master={s['master']}, MasterName={master_name}")
            elif master_name and 'connector' in master_name.lower():
                print(f"CONNECTOR: ID={s['id']}, Master={s['master']}, MasterName={master_name}")
        # Parse connections
        connections = parse_visio_connections(xml_path)
        # Build reverse index: for each connector, which shapes does it connect to?
        connector_to_shapes = defaultdict(list)
        for c in connections:
            from_id = c['from_sheet']
            to_id = c['to_sheet']
            # If from_id is a connector (not a box), map it
            if from_id in shape_dict and shape_dict[from_id].get('text', '') == '':
                connector_to_shapes[from_id].append(to_id)
        # Now, for each connector that connects to two shapes, output the box-to-box connection:
        box_connections = []
        print("\nBox-to-box connections (diagram structure):")
        for conn_id, shape_ids in connector_to_shapes.items():
            if len(shape_ids) == 2:
                label1 = shape_dict[shape_ids[0]].get('text', '') or shape_dict[shape_ids[0]].get('name', '') or shape_ids[0]
                label2 = shape_dict[shape_ids[1]].get('text', '') or shape_dict[shape_ids[1]].get('name', '') or shape_ids[1]
                print(f"  {label2} --> {label1}")
                box_connections.append({'from': label2, 'to': label1})
        # Optionally: Export this structure to JSON for GPT-4o etc.
        json_filename = f"diagram_structure_{page_xml.replace('.xml','')}.json"
        with open(json_filename, "w") as f:
            json.dump(box_connections, f, indent=2)
        print(f"\nExported box-to-box connections to {json_filename}")

if __name__ == "__main__":
    main()

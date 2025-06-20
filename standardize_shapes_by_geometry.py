import os
import xml.etree.ElementTree as ET
import json

VISIO_NS = 'http://schemas.microsoft.com/office/visio/2012/main'

def get_master_geometry_type(master_xml_path):
    if not os.path.exists(master_xml_path):
        return None
    try:
        tree = ET.parse(master_xml_path)
        root = tree.getroot()
        for section in root.findall(f".//{{{VISIO_NS}}}Section"):
            if section.get('N', '').lower() == 'geometry':
                row_types = [row.get('T', '').lower() for row in section.findall(f"{{{VISIO_NS}}}Row")]
                if any(rt == 'ellipticalarcto' for rt in row_types):
                    return 'Ellipse'
                if any(rt == 'lineto' for rt in row_types):
                    return 'Rectangle'
    except Exception as e:
        print(f"Error parsing {master_xml_path}: {e}")
    return None

def build_master_shape_map_from_mastersxml(mastersxml_path):
    mapping = {}
    if not os.path.exists(mastersxml_path):
        print(f"Warning: {mastersxml_path} not found!")
        return mapping
    tree = ET.parse(mastersxml_path)
    root = tree.getroot()
    for master in root.findall(f'{{{VISIO_NS}}}Master'):
        master_id = master.get('ID')
        nameu = master.get('NameU', '').lower()
        if 'connector' in nameu:
            mapping[master_id] = 'Connector'
        elif 'circle' in nameu:
            mapping[master_id] = 'Ellipse'
        elif 'ellipse' in nameu:
            mapping[master_id] = 'Ellipse'
        elif 'rectangle' in nameu:
            mapping[master_id] = 'Rectangle'
        else:
            mapping[master_id] = None
    return mapping

def build_master_shape_map(masters_dir, mastersxml_path):
    mastersxml_map = build_master_shape_map_from_mastersxml(mastersxml_path)
    for fname in os.listdir(masters_dir):
        if fname.startswith('master') and fname.endswith('.xml') and fname != 'masters.xml':
            master_id = fname.replace('master', '').replace('.xml', '')
            shape_type = get_master_geometry_type(os.path.join(masters_dir, fname))
            if shape_type is not None:
                mastersxml_map[master_id] = shape_type
    return mastersxml_map

def parse_shapes_from_page(page_xml_path):
    shapes = []
    tree = ET.parse(page_xml_path)
    root = tree.getroot()
    for shape in root.findall(f'.//{{{VISIO_NS}}}Shape'):
        shape_id = shape.get('ID')
        master_id = shape.get('Master')
        text = ''
        text_elem = shape.find(f'{{{VISIO_NS}}}Text')
        if text_elem is not None:
            text = ''.join(text_elem.itertext()).strip()

        # Helper to extract Cell values
        def get_cell_value(name):
            cell = shape.find(f"{{{VISIO_NS}}}Cell[@N='{name}']")
            return float(cell.get('V')) if cell is not None else None

        pinx = get_cell_value('PinX')
        piny = get_cell_value('PinY')
        width = get_cell_value('Width')
        height = get_cell_value('Height')

        beginx = get_cell_value('BeginX')
        beginy = get_cell_value('BeginY')
        endx = get_cell_value('EndX')
        endy = get_cell_value('EndY')

        shape_data = {
            'id': shape_id,
            'master': master_id,
            'text': text,
            'PinX': pinx,
            'PinY': piny,
            'Width': width,
            'Height': height
        }

        # Only add connector endpoints if they exist (likely only for connectors)
        if beginx is not None and beginy is not None and endx is not None and endy is not None:
            shape_data.update({
                'BeginX': beginx,
                'BeginY': beginy,
                'EndX': endx,
                'EndY': endy
            })

        shapes.append(shape_data)
    return shapes

def main():
    masters_dir = os.path.join('output_xml', 'visio', 'masters')
    mastersxml_path = os.path.join(masters_dir, 'masters.xml')
    page_xml_path = os.path.join('output_xml', 'visio', 'pages', 'page1.xml')
    output_json_path = 'standardized_page1.json'
    unmapped_log_path = 'unmapped_shapes.log'

    # Build master_id -> type map, using both sources
    master_shape_map = build_master_shape_map(masters_dir, mastersxml_path)

    shapes = parse_shapes_from_page(page_xml_path)

    standardized = []
    unmapped = []
    for s in shapes:
        master_id = s.get('master')
        shape_type = master_shape_map.get(master_id, None)
        if shape_type is None:
            s['standard_type'] = 'Unmapped'
            unmapped.append(s)
        else:
            s['standard_type'] = shape_type
        standardized.append(s)

    with open(output_json_path, 'w') as f:
        json.dump(standardized, f, indent=2)
    print(f"Standardized shapes written to {output_json_path}")

    if unmapped:
        with open(unmapped_log_path, 'w') as f:
            for s in unmapped:
                f.write(json.dumps(s) + '\n')
        print(f"Unmapped shapes logged to {unmapped_log_path}")
    else:
        print("All shapes successfully mapped.")

if __name__ == '__main__':
    main()

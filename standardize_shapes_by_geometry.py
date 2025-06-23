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

def get_master_width_height(master_id, masters_dir):
    master_path = os.path.join(masters_dir, f"master{master_id}.xml")
    if not os.path.exists(master_path):
        print(f"Warning: Master XML {master_path} not found for master id {master_id}")
        return None, None
    try:
        tree = ET.parse(master_path)
        root = tree.getroot()
        width = None
        height = None
        # Find the first shape in the master (usually ID=5)
        shape_elem = root.find(f".//{{{VISIO_NS}}}Shape")
        if shape_elem is not None:
            for cell in shape_elem.findall(f"{{{VISIO_NS}}}Cell"):
                n = cell.get('N')
                if n == "Width":
                    width = float(cell.get('V'))
                elif n == "Height":
                    height = float(cell.get('V'))
                if width is not None and height is not None:
                    break
        # Use absolute values to avoid negative height/width
        if width is not None:
            width = abs(width)
        if height is not None:
            height = abs(height)
        return width, height
    except Exception as e:
        print(f"Could not read width/height from master {master_id}: {e}")
        return None, None

def parse_shapes_from_page(page_xml_path, master_shape_map, masters_dir):
    shapes = []
    tree = ET.parse(page_xml_path)
    root = tree.getroot()

    def get_cell_value(shape_elem, name):
        # Try direct child
        cell = shape_elem.find(f"{{{VISIO_NS}}}Cell[@N='{name}']")
        if cell is not None and cell.get('V') is not None:
            return float(cell.get('V'))
        # Try under <XForm> (most boxes, ellipses)
        xform = shape_elem.find(f"{{{VISIO_NS}}}XForm")
        if xform is not None:
            cell = xform.find(f"{{{VISIO_NS}}}Cell[@N='{name}']")
            if cell is not None and cell.get('V') is not None:
                return float(cell.get('V'))
        # Try under <XForm1> (rare, but possible)
        xform1 = shape_elem.find(f"{{{VISIO_NS}}}XForm1")
        if xform1 is not None:
            cell = xform1.find(f"{{{VISIO_NS}}}Cell[@N='{name}']")
            if cell is not None and cell.get('V') is not None:
                return float(cell.get('V'))
        return None

    for shape in root.findall(f'.//{{{VISIO_NS}}}Shape'):
        shape_id = shape.get('ID')
        master_id = shape.get('Master')
        text = ''
        text_elem = shape.find(f'{{{VISIO_NS}}}Text')
        if text_elem is not None:
            text = ''.join(text_elem.itertext()).strip()

        pinx = get_cell_value(shape, 'PinX')
        piny = get_cell_value(shape, 'PinY')
        width = get_cell_value(shape, 'Width')
        height = get_cell_value(shape, 'Height')
        beginx = get_cell_value(shape, 'BeginX')
        beginy = get_cell_value(shape, 'BeginY')
        endx = get_cell_value(shape, 'EndX')
        endy = get_cell_value(shape, 'EndY')

        # Fallback to master if missing and not a connector
        shape_type = master_shape_map.get(master_id, None)
        if (width is None or height is None) and shape_type in ("Rectangle", "Ellipse"):
            width_m, height_m = get_master_width_height(master_id, masters_dir)
            if width is None and width_m is not None:
                width = width_m
            elif width is None:
                width = 1.0  # default width if master is missing
            if height is None and height_m is not None:
                height = height_m
            elif height is None:
                height = 1.0  # default height if master is missing


        shape_data = {
            'id': shape_id,
            'master': master_id,
            'text': text,
            'PinX': pinx,
            'PinY': piny,
            'Width': width,
            'Height': height
        }

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
    pages_dir = os.path.join('output_xml', 'visio', 'pages')

    # Build master_id -> type map, using both sources
    master_shape_map = build_master_shape_map(masters_dir, mastersxml_path)

    # Find all page XML files
    page_files = [f for f in os.listdir(pages_dir)
                  if f.startswith('page') and f.endswith('.xml')]

    if not page_files:
        print("No page XML files found in", pages_dir)
        return

    for page_file in page_files:
        page_xml_path = os.path.join(pages_dir, page_file)
        page_basename = page_file.replace('.xml', '')
        output_json_path = f'standardized_{page_basename}.json'
        unmapped_log_path = f'unmapped_shapes_{page_basename}.log'

        shapes = parse_shapes_from_page(page_xml_path, master_shape_map, masters_dir)
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
            print(f"All shapes successfully mapped for {page_file}")

if __name__ == '__main__':
    main()

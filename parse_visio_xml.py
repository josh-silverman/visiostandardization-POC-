import os
import re
import xml.etree.ElementTree as ET
import json
from collections import defaultdict

def get_text_from_elem(elem):
    if elem is None:
        return ""
    text = elem.text or ""
    for child in elem:
        text += get_text_from_elem(child)
        if child.tail:
            text += child.tail
    return text.strip()

def parse_masters_xml(masters_xml_path):
    ns = {'visio': 'http://schemas.microsoft.com/office/visio/2012/main'}
    master_info = {}
    tree = ET.parse(masters_xml_path)
    root = tree.getroot()
    for master in root.findall('visio:Master', ns):
        master_id = master.get('ID')
        nameU = master.get('NameU', '')
        name = master.get('Name', '')
        prompt = master.get('Prompt', '')
        master_info[master_id] = {
            "nameU": nameU,
            "name": name,
            "prompt": prompt
        }
    return master_info

def parse_master_contents(masters_dir, master_id):
    ns = {'visio': 'http://schemas.microsoft.com/office/visio/2012/main'}
    master_filename = f"master{master_id}.xml"
    master_path = os.path.join(masters_dir, master_filename)
    if not os.path.exists(master_path):
        return {}
    try:
        tree = ET.parse(master_path)
        root = tree.getroot()
        shape_elem = root.find('.//visio:Shape', ns)
        if shape_elem is None:
            return {}
        info = {
            "shape_id": shape_elem.get("ID"),
            "type": shape_elem.get("Type"),
            "line_style": shape_elem.get("LineStyle"),
            "fill_style": shape_elem.get("FillStyle"),
            "text_style": shape_elem.get("TextStyle"),
            "cells": {},
            "sections": []
        }
        for cell in shape_elem.findall('visio:Cell', ns):
            cell_name = cell.get("N")
            cell_val = cell.get("V")
            info["cells"][cell_name] = cell_val
        for section in shape_elem.findall('visio:Section', ns):
            section_name = section.get("N")
            rows = []
            for row in section.findall('visio:Row', ns):
                row_attrs = row.attrib.copy()
                row_cells = {cell.get("N"): cell.get("V") for cell in row.findall('visio:Cell', ns)}
                row_attrs["cells"] = row_cells
                rows.append(row_attrs)
            info["sections"].append({"name": section_name, "rows": rows})
        return info
    except Exception as e:
        print(f"Error parsing {master_filename}: {e}")
        return {}

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
        # Extract geometry and formatting from cells
        cells = {cell.get("N"): cell.get("V") for cell in shape.findall('visio:Cell', ns)}
        geometry = {
            "BeginX": cells.get("BeginX"),
            "BeginY": cells.get("BeginY"),
            "EndX": cells.get("EndX"),
            "EndY": cells.get("EndY"),
        }
        line_format = {
            "LineColor": cells.get("LineColor"),
            "LineWeight": cells.get("LineWeight"),
            "EndArrow": cells.get("EndArrow"),
        }
        shapes_data.append({
            'id': shape_id,
            'name': shape_name,
            'type': shape_type,
            'text': shape_text,
            'master': shape.get('Master'),
            'geometry': geometry,
            'line_format': line_format
        })
    return shapes_data

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
    masters_xml_path = os.path.join(masters_dir, "masters.xml")
    if not os.path.exists(pages_dir):
        print(f"Directory does not exist: {pages_dir}")
        return
    if not os.path.exists(masters_xml_path):
        print(f"masters.xml does not exist: {masters_xml_path}")
        return

    # --- Load all master names for lookup ---
    master_info = parse_masters_xml(masters_xml_path)

    page_xmls = [f for f in os.listdir(pages_dir) if re.match(r'page\d+\.xml$', f)]
    print("Found page XML files:", page_xmls)
    for page_xml in page_xmls:
        xml_path = os.path.join(pages_dir, page_xml)
        print(f"\n--- Parsing {page_xml} ---")

        # --- Parse all <Shape> elements ---
        shapes = parse_visio_page_xml(xml_path)
        shape_dict = {s['id']: s for s in shapes}
        for s in shapes:
            m_id = s['master']
            m_info = master_info.get(m_id, {}) if m_id else {}
            s['master_nameU'] = m_info.get("nameU", "")
            s['master_name'] = m_info.get("name", "")
            s['master_prompt'] = m_info.get("prompt", "")
            # Parse masterN.xml for geometry/style details
            if m_id:
                s['master_contents'] = parse_master_contents(masters_dir, m_id)
            else:
                s['master_contents'] = {}
            # Add is_connector flag for easier processing
            is_connector = False
            if (m_info.get("nameU",'') and 'connector' in m_info.get("nameU",'').lower()) or \
               (m_info.get("name",'') and 'connector' in m_info.get("name",'').lower()):
                is_connector = True
            s['is_connector'] = is_connector

        # --- Parse <Connects> to resolve connector endpoints ---
        connections = parse_visio_connections(xml_path)
        connector_map = defaultdict(dict)
        for c in connections:
            from_id = c['from_sheet']
            to_id = c['to_sheet']
            from_cell = c['from_cell']
            # Map begin/end shape for connectors
            if from_id in shape_dict and shape_dict[from_id].get('is_connector', False):
                if from_cell == 'BeginX':
                    connector_map[from_id]['begin_shape'] = to_id
                elif from_cell == 'EndX':
                    connector_map[from_id]['end_shape'] = to_id

        # --- Separate shapes and connectors ---
        normal_shapes = []
        connectors = []
        for s in shapes:
            if s['is_connector']:
                conn_id = s['id']
                s['begin_shape'] = connector_map[conn_id].get('begin_shape')
                s['end_shape'] = connector_map[conn_id].get('end_shape')
                connectors.append(s)
            else:
                normal_shapes.append(s)

        # --- Output two lists: shapes (non-connectors), connectors (with all info) ---
        combined_json = {
            "shapes": normal_shapes,
            "connectors": connectors
        }
        combined_json_filename = f"diagram_full_{page_xml.replace('.xml','')}.json"
        with open(combined_json_filename, "w") as f:
            json.dump(combined_json, f, indent=2)
        print(f"\nExported shapes and connectors to {combined_json_filename}")

if __name__ == "__main__":
    main()

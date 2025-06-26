import xml.etree.ElementTree as ET
import json
import os

NS = '{http://schemas.microsoft.com/office/visio/2012/main}'

def get_text_from_text_elem(text_elem):
    """
    Extracts all text content from the <Text> element, including text after child tags.
    """
    text_content = []
    if text_elem.text and text_elem.text.strip():
        text_content.append(text_elem.text.strip())
    for child in text_elem:
        if child.tail and child.tail.strip():
            text_content.append(child.tail.strip())
    return " ".join(text_content) if text_content else None

def parse_shape(shape_elem):
    shape = {
        "id": shape_elem.attrib.get("ID"),
        "type": shape_elem.attrib.get("Type"),
        "master": shape_elem.attrib.get("Master"),
        "cells": {},
        "text": None
    }
    # Extract <Cell> values as a dict
    for cell in shape_elem.findall(f'{NS}Cell'):
        shape["cells"][cell.attrib['N']] = cell.attrib.get('V')
    # Extract Text
    text_elem = shape_elem.find(f'{NS}Text')
    if text_elem is not None:
        shape["text"] = get_text_from_text_elem(text_elem)
    return shape

def parse_connect(connect_elem):
    return {
        "from_sheet": connect_elem.attrib.get("FromSheet"),
        "from_cell": connect_elem.attrib.get("FromCell"),
        "to_sheet": connect_elem.attrib.get("ToSheet"),
        "to_cell": connect_elem.attrib.get("ToCell"),
    }

def main():
    xml_file = "output_xml/visio/pages/page1.xml"  # Update path as needed
    output_json = "page1.json"
    if not os.path.exists(xml_file):
        raise FileNotFoundError(f"Could not find {xml_file}")
    tree = ET.parse(xml_file)
    root = tree.getroot()

    shapes = []
    shapes_elem = root.find(f'{NS}Shapes')
    if shapes_elem is not None:
        for shape in shapes_elem:
            shapes.append(parse_shape(shape))

    connects = []
    connects_elem = root.find(f'{NS}Connects')
    if connects_elem is not None:
        for connect in connects_elem:
            connects.append(parse_connect(connect))

    output = {
        "shapes": shapes,
        "connections": connects
    }
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"JSON written to {output_json}")

if __name__ == "__main__":
    main()

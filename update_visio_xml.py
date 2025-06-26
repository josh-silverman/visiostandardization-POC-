import xml.etree.ElementTree as ET
import json
import shutil
import os
from xml.dom import minidom

STD_JSON = "enhanced_diagram_full_page1.json"
PAGE_XML = "output_xml/visio/pages/page1.xml"


with open(STD_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

shapes = data["shapes"]
shape_lookup = {str(shape["id"]): shape for shape in shapes}

VNS = "http://schemas.microsoft.com/office/visio/2012/main"
NS = {'v': VNS}
ET.register_namespace('', VNS)

def pretty_print_xml(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding="utf-8")

tree = ET.parse(PAGE_XML)
root = tree.getroot()

updated_count = 0
missing_shapes = []

for shape_elem in root.findall(".//v:Shape", NS):
    shape_id = shape_elem.attrib.get("ID")
    if shape_id and shape_id in shape_lookup:
        shape_data = shape_lookup[shape_id]

        # --- Update Text ---
        for old_text_elem in shape_elem.findall("v:Text", NS):
            shape_elem.remove(old_text_elem)
        new_text = shape_data.get("text", None)
        if new_text is not None:
            new_text_elem = ET.SubElement(shape_elem, f"{{{VNS}}}Text")
            new_text_elem.text = new_text

        # --- Update Cells ---
        cells = shape_data.get("cells", {})
        # Track which cells are updated/created
        updated_cells = set()
        for cell_name, cell_value in cells.items():
            cell_elem = None
            for c in shape_elem.findall("v:Cell", NS):
                if c.attrib.get("N") == cell_name:
                    cell_elem = c
                    break
            if cell_elem is not None:
                cell_elem.set("V", str(cell_value))
            else:
                ET.SubElement(shape_elem, f"{{{VNS}}}Cell", {"N": cell_name, "V": str(cell_value)})
            updated_cells.add(cell_name)
        # Optionally: remove <Cell> elements not present in JSON (not always desired)
        # for c in list(shape_elem.findall("v:Cell", NS)):
        #     if c.attrib.get("N") not in updated_cells:
        #         shape_elem.remove(c)

        updated_count += 1
    else:
        missing_shapes.append(shape_id)

# Write pretty-printed XML
pretty_xml = pretty_print_xml(root)
with open(PAGE_XML, "wb") as f:
    f.write(pretty_xml)
print(f"Updated {PAGE_XML} with standardized text and cells for {updated_count} shapes.")

if missing_shapes:
    print(f"Warning: {len(missing_shapes)} shapes in XML had no match in standardized JSON (IDs: {missing_shapes})")
else:
    print("All shapes in XML matched and updated from standardized JSON.")

import xml.etree.ElementTree as ET
import json

# Load the enhanced shape lookup from Step 1
with open("enhanced_standardized_page1.json") as f:
    enhanced_shapes = json.load(f)
shape_lookup = {shape["id"]: shape for shape in enhanced_shapes}

# Define paths and namespaces
PAGE_XML = "output_xml/visio/pages/page1.xml"
VNS = "http://schemas.microsoft.com/office/visio/2012/main"
NS = {'v': VNS}
ET.register_namespace('', VNS)  # This prevents namespace prefixes in output

# Parse the XML file
tree = ET.parse(PAGE_XML)
root = tree.getroot()

# Find all Shape elements (with correct namespace)
for shape_elem in root.findall(".//v:Shape", NS):
    shape_id = shape_elem.attrib.get("ID")
    if shape_id in shape_lookup:
        # Find or create the <Text> element
        text_elem = shape_elem.find("v:Text", NS)
        if text_elem is None:
            text_elem = ET.SubElement(shape_elem, f"{{{VNS}}}Text")
        # Update the text
        text_elem.text = shape_lookup[shape_id]["text"]

# Save the updated XML
tree.write(PAGE_XML, encoding="utf-8", xml_declaration=True)

print(f"Updated shape texts in '{PAGE_XML}' from enhanced JSON.")

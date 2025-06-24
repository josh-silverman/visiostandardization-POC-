import xml.etree.ElementTree as ET
import json

# Load the enhanced JSON
with open("enhanced_diagram_full_page1.json") as f:
    enhanced_data = json.load(f)
shapes = enhanced_data["shapes"]
shape_lookup = {shape["id"]: shape for shape in shapes}

# Define paths and namespaces
PAGE_XML = "output_xml/visio/pages/page1.xml"
VNS = "http://schemas.microsoft.com/office/visio/2012/main"
NS = {'v': VNS}
ET.register_namespace('', VNS)  # This prevents namespace prefixes in output

# Parse the XML file
tree = ET.parse(PAGE_XML)
root = tree.getroot()

for shape_elem in root.findall(".//v:Shape", NS):
    shape_id = shape_elem.attrib.get("ID")
    if shape_id and shape_id in shape_lookup:
        shape_data = shape_lookup[shape_id]
        
        # --- Remove and update <Text> ---
        for old_text_elem in shape_elem.findall("v:Text", NS):
            shape_elem.remove(old_text_elem)
        new_text_elem = ET.SubElement(shape_elem, f"{{{VNS}}}Text")
        new_text_elem.text = shape_data.get("text", "")

        # --- Remove and update fill color (for shapes with fill_color) ---
        for cell_elem in list(shape_elem.findall("v:Cell", NS)):
            if cell_elem.get("N") in ("FillForegnd", "FillPattern"):
                shape_elem.remove(cell_elem)
        fill_color = shape_data.get("fill_color")
        if fill_color:
            fill_cell = ET.SubElement(shape_elem, f"{{{VNS}}}Cell")
            fill_cell.set("N", "FillForegnd")
            fill_cell.set("V", fill_color)
            fillpat_cell = ET.SubElement(shape_elem, f"{{{VNS}}}Cell")
            fillpat_cell.set("N", "FillPattern")
            fillpat_cell.set("V", "1")

        # --- Text alignment (if available) ---
        text_align = shape_data.get("text_align")
        if text_align:
            # Remove old alignment cell if present
            for cell_elem in list(shape_elem.findall("v:Cell", NS)):
                if cell_elem.get("N") == "TxtAlign":
                    shape_elem.remove(cell_elem)
            # Visio: 0=left, 1=center, 2=right
            align_map = {"left": "0", "center": "1", "right": "2"}
            align_val = align_map.get(text_align.lower(), "1")
            align_cell = ET.SubElement(shape_elem, f"{{{VNS}}}Cell")
            align_cell.set("N", "TxtAlign")
            align_cell.set("V", align_val)

        # --- Update position if PinX/PinY in master_contents/cells ---
        master_cells = shape_data.get("master_contents", {}).get("cells", {})
        pinx = master_cells.get("PinX")
        piny = master_cells.get("PinY")
        if pinx or piny:
            xform = shape_elem.find("v:XForm", NS)
            if xform is not None:
                pinx_elem = xform.find("v:PinX", NS)
                piny_elem = xform.find("v:PinY", NS)
                if pinx and pinx_elem is not None:
                    pinx_elem.text = str(pinx)
                if piny and piny_elem is not None:
                    piny_elem.text = str(piny)

        # --- Connector styling ---
        master_nameU = shape_data.get("master_nameU", "").lower()
        if "connector" in master_nameU:
            # Remove any existing connector styling
            for cell_elem in list(shape_elem.findall("v:Cell", NS)):
                if cell_elem.get("N") in ("LineColor", "LineWeight", "EndArrow"):
                    shape_elem.remove(cell_elem)
            # Set line color to black
            linecolor_cell = ET.SubElement(shape_elem, f"{{{VNS}}}Cell")
            linecolor_cell.set("N", "LineColor")
            linecolor_cell.set("V", "#000000")
            # Set line weight to bold if specified
            if shape_data.get("line_weight") == "bold":
                lineweight_cell = ET.SubElement(shape_elem, f"{{{VNS}}}Cell")
                lineweight_cell.set("N", "LineWeight")
                lineweight_cell.set("V", "0.0278")  # 2pt in inches
            # Set end arrow (standard arrowhead)
            endarrow_cell = ET.SubElement(shape_elem, f"{{{VNS}}}Cell")
            endarrow_cell.set("N", "EndArrow")
            endarrow_cell.set("V", "4")

# Save the updated XML
tree.write(PAGE_XML, encoding="utf-8", xml_declaration=True)

print(f"Updated shape texts, colors, layout, and connector styles in '{PAGE_XML}' from enhanced_diagram_full_page1.json.")

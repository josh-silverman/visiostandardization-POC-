import xml.etree.ElementTree as ET
import json

# Load the enhanced layout JSON
with open("layout_enhanced_standardized_page1.json") as f:
    enhanced_shapes = json.load(f)
shape_lookup = {shape["id"]: shape for shape in enhanced_shapes}

# Define paths and namespaces
PAGE_XML = "output_xml/visio/pages/page1.xml"
VNS = "http://schemas.microsoft.com/office/visio/2012/main"
NS = {'v': VNS}
ET.register_namespace('', VNS)  # This prevents namespace prefixes in output

# Color settings
RECTANGLE_COLOR = "#5B9BD5"  # Blue
ELLIPSE_COLOR = "#70AD47"    # Green

# Parse the XML file
tree = ET.parse(PAGE_XML)
root = tree.getroot()

for shape_elem in root.findall(".//v:Shape", NS):
    shape_id = shape_elem.attrib.get("ID")
    if shape_id in shape_lookup:
        shape_data = shape_lookup[shape_id]
        stype = shape_data.get("standard_type", "").lower()

        # --- Remove and update <Text> ---
        for old_text_elem in shape_elem.findall("v:Text", NS):
            shape_elem.remove(old_text_elem)
        new_text_elem = ET.SubElement(shape_elem, f"{{{VNS}}}Text")
        new_text_elem.text = shape_data["text"]

        # --- Remove and update fill color ---
        for cell_elem in list(shape_elem.findall("v:Cell", NS)):
            if cell_elem.get("N") in ("FillForegnd", "FillPattern"):
                shape_elem.remove(cell_elem)
        fill_color = None
        if stype == "rectangle":
            fill_color = RECTANGLE_COLOR
        elif stype == "ellipse":
            fill_color = ELLIPSE_COLOR
        if fill_color:
            fill_cell = ET.SubElement(shape_elem, f"{{{VNS}}}Cell")
            fill_cell.set("N", "FillForegnd")
            fill_cell.set("V", fill_color)
            fillpat_cell = ET.SubElement(shape_elem, f"{{{VNS}}}Cell")
            fillpat_cell.set("N", "FillPattern")
            fillpat_cell.set("V", "1")

        # --- Update position for rectangles/ellipses ---
        if stype in ('rectangle', 'ellipse'):
            xform = shape_elem.find("v:XForm", NS)
            if xform is not None:
                pinx_elem = xform.find("v:PinX", NS)
                piny_elem = xform.find("v:PinY", NS)
                if pinx_elem is not None:
                    pinx_elem.text = str(shape_data["PinX"])
                if piny_elem is not None:
                    piny_elem.text = str(shape_data["PinY"])

        # --- Update connector geometry and style ---
        if stype == 'connector':
            # Update XForm (if present)
            xform = shape_elem.find("v:XForm", NS)
            if xform is not None:
                pinx_elem = xform.find("v:PinX", NS)
                piny_elem = xform.find("v:PinY", NS)
                # Optionally update connector's PinX/PinY if needed

            # Update BeginX/BeginY and EndX/EndY if present in Geom
            geom = shape_elem.find("v:Geom", NS)
            if geom is not None:
                beginx_elem = geom.find("v:BeginX", NS)
                beginy_elem = geom.find("v:BeginY", NS)
                endx_elem = geom.find("v:EndX", NS)
                endy_elem = geom.find("v:EndY", NS)
                if beginx_elem is not None and "BeginX" in shape_data:
                    beginx_elem.text = str(shape_data["BeginX"])
                if beginy_elem is not None and "BeginY" in shape_data:
                    beginy_elem.text = str(shape_data["BeginY"])
                if endx_elem is not None and "EndX" in shape_data:
                    endx_elem.text = str(shape_data["EndX"])
                if endy_elem is not None and "EndY" in shape_data:
                    endy_elem.text = str(shape_data["EndY"])

            # --- Enhance connector style ---
            # Remove any existing styling Cells for connectors
            # --- Enhance connector style ---
            for cell_elem in list(shape_elem.findall("v:Cell", NS)):
                if cell_elem.get("N") in ("LineColor", "LineWeight", "EndArrow"):
                    shape_elem.remove(cell_elem)
            # Set line color to black
            linecolor_cell = ET.SubElement(shape_elem, f"{{{VNS}}}Cell")
            linecolor_cell.set("N", "LineColor")
            linecolor_cell.set("V", "#000000")
            # Set line weight to 2pt (0.0278 inches)
            lineweight_cell = ET.SubElement(shape_elem, f"{{{VNS}}}Cell")
            lineweight_cell.set("N", "LineWeight")
            lineweight_cell.set("V", "0.0278")
            # Set end arrow (standard arrowhead)
            endarrow_cell = ET.SubElement(shape_elem, f"{{{VNS}}}Cell")
            endarrow_cell.set("N", "EndArrow")
            endarrow_cell.set("V", "4")


# Save the updated XML
tree.write(PAGE_XML, encoding="utf-8", xml_declaration=True)

print(f"Updated shape texts, colors, layout, and connector styles in '{PAGE_XML}' from layout-enhanced JSON.")

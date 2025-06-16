import os
import xml.etree.ElementTree as ET

def parse_pages_xml(pages_dir):
    """Parse shapes, text, connectors from all XMLs in pages_dir."""
    diagrams = []
    for file in os.listdir(pages_dir):
        if file.endswith(".xml"):
            path = os.path.join(pages_dir, file)
            tree = ET.parse(path)
            root = tree.getroot()
            ns = {'visio': 'http://schemas.microsoft.com/office/visio/2012/main'}
            shapes = []
            connectors = []
            for shape in root.findall(".//visio:Shape", ns):
                shape_id = shape.get('ID')
                shape_type = shape.get('Type', 'unknown')
                text = ''
                text_elem = shape.find(".//visio:Text", ns)
                if text_elem is not None and text_elem.text:
                    text = text_elem.text.strip()
                shapes.append({
                    "id": shape_id,
                    "type": shape_type,
                    "text": text
                })
            # Connector parsing logic (simplified, extend as needed)
            for connect in root.findall(".//visio:Connect", ns):
                from_id = connect.get('FromSheet')
                to_id = connect.get('ToSheet')
                connectors.append({
                    "from": from_id,
                    "to": to_id
                })
            diagrams.append({
                "page": file,
                "shapes": shapes,
                "connectors": connectors
            })
    return diagrams


# standardize.py
import json

try:
    import comtypes.client
except ImportError:
    comtypes = None

def map_to_template_schema(shapes, template_schema):
    standardized = []
    for shape in shapes:
        stype = shape.get("type", "rectangle").lower()
        std_shape = {
            "type": stype,
            "text": shape.get("text", ""),
            "position": shape.get("position", {"x": 1, "y": 1}),
            "style": template_schema["shapes"].get(stype, {"color": "gray", "font": "Arial", "size": 10})
        }
        standardized.append(std_shape)
    return standardized

def create_visio_diagram(data, template_path, output_path):
    if comtypes is None:
        raise RuntimeError("comtypes is not available. Must run on Windows with Visio installed.")
    visio = comtypes.client.CreateObject("Visio.Application")
    visio.Visible = False
    doc = visio.Documents.Add(template_path)
    page = doc.Pages[1]
    for shape in data:
        x = shape["position"].get("x", 1)
        y = shape["position"].get("y", 1)
        width = shape.get("style", {}).get("width", 100)
        height = shape.get("style", {}).get("height", 50)
        shp = page.DrawRectangle(x, y, x + width, y - height)
        shp.Text = shape["text"]
        color = shape["style"].get("color", "RGB(200,200,200)")
        if not color.startswith("RGB"):
            color = "RGB(0,0,255)" if color == "blue" else "RGB(0,128,0)" if color == "green" else "RGB(200,200,200)"
        shp.Cells("FillForegnd").FormulaU = color
    doc.SaveAs(output_path)
    doc.Close()
    visio.Quit()

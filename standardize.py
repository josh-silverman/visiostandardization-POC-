TEMPLATE_SCHEMA = {
    "shapes": {
        "rectangle": {"color": "blue", "font": "Arial", "size": 10},
        "ellipse": {"color": "green", "font": "Arial", "size": 10}
    },
    "connectors": {"type": "straight", "color": "black"},
    "layout": "vertical"
}

def standardize_diagram_data(diagram_data):
    standardized_shapes = []
    for shape in diagram_data.get("shapes", []):
        standardized_shape = {
            "id": shape.get("id"),
            "type": shape.get("type"),
            "text": shape.get("text"),
            "style": TEMPLATE_SCHEMA["shapes"].get(
                shape.get("type"), 
                {"color": "gray", "font": "Arial", "size": 10}
            )
        }
        standardized_shapes.append(standardized_shape)
    standardized_data = {
        "shapes": standardized_shapes,
        "connectors": diagram_data.get("connectors", []),
        "layout": TEMPLATE_SCHEMA["layout"]
    }
    return standardized_data

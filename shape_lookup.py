import json

# Path to your enhanced JSON file
ENHANCED_JSON_PATH = "enhanced_standardized_page1.json"

# Load the enhanced shapes
with open(ENHANCED_JSON_PATH, "r") as f:
    enhanced_shapes = json.load(f)

# Build a lookup: shape_id -> shape_data
shape_lookup = {shape["id"]: shape for shape in enhanced_shapes}

print("Loaded {} shapes from enhanced JSON.".format(len(shape_lookup)))
print("Sample mapping:", list(shape_lookup.items())[:2])  # Show first two for inspection

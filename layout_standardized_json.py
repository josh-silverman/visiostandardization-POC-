import json

INPUT_JSON = "enhanced_standardized_page1.json"
OUTPUT_JSON = "layout_enhanced_standardized_page1.json"

# Load shapes from the original JSON
with open(INPUT_JSON, "r") as f:
    shapes = json.load(f)

# Layout parameters
PINY = 5.0        # Fixed vertical position for all main shapes
PINX_START = 2.0  # Leftmost position for first shape
X_GAP = 2.2       # Horizontal gap between shapes

# Identify main shapes and connectors
main_shapes = [s for s in shapes if s['standard_type'].lower() in ('rectangle', 'ellipse')]
connectors = [s for s in shapes if s['standard_type'].lower() == 'connector']

# Sort main shapes left-to-right by existing PinX
main_shapes_sorted = sorted(main_shapes, key=lambda s: s['PinX'])

# Assign new PinX and PinY values, evenly spaced
for i, shape in enumerate(main_shapes_sorted):
    shape['PinX'] = PINX_START + i * X_GAP
    shape['PinY'] = PINY

# Update connectors to connect adjacent shapes
for i, conn in enumerate(connectors):
    # Only update connectors that connect main shapes in sequence
    if i < len(main_shapes_sorted) - 1:
        from_shape = main_shapes_sorted[i]
        to_shape = main_shapes_sorted[i + 1]
        # Connect from right edge of from_shape to left edge of to_shape
        conn['BeginX'] = from_shape['PinX'] + from_shape['Width'] / 2
        conn['BeginY'] = from_shape['PinY']
        conn['EndX'] = to_shape['PinX'] - to_shape['Width'] / 2
        conn['EndY'] = to_shape['PinY']
    # If extra connectors, leave their positions as is

# Save the updated layout JSON
with open(OUTPUT_JSON, "w") as f:
    json.dump(shapes, f, indent=2)

print(f"Saved layout-enhanced JSON to {OUTPUT_JSON}")

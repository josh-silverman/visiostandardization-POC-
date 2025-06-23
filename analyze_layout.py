import os
import json

def load_shapes(json_path):
    with open(json_path, 'r') as f:
        shapes = json.load(f)
    return shapes

def group_by_alignment(shapes, axis='y', tolerance=0.05):
    key = 'PinY' if axis == 'y' else 'PinX'
    grouped = []
    for shape in shapes:
        val = shape.get(key)
        found = False
        for group in grouped:
            if val is not None and abs(group['val'] - val) <= tolerance:
                group['shapes'].append(shape)
                found = True
                break
        if not found and val is not None:
            grouped.append({'val': val, 'shapes': [shape]})
    return {round(group['val'], 4): group['shapes'] for group in grouped}

def main():
    # Find all standardized JSON files for pages in the current directory
    files = [f for f in os.listdir('.') if f.startswith('standardized_page') and f.endswith('.json')]
    if not files:
        print("No standardized_page*.json files found in current directory.")
        return

    for file in sorted(files):
        shapes = load_shapes(file)
        print(f"\nAnalyzing {file} ({len(shapes)} shapes)")

        # Group by rows (PinY)
        row_groups = group_by_alignment(shapes, axis='y', tolerance=0.05)
        for row_val, row_shapes in row_groups.items():
            # Sort by PinX (left to right)
            row_shapes_sorted = sorted(row_shapes, key=lambda s: (s['PinX'] if s['PinX'] is not None else float('-inf')))
            print(f"Row PinY={row_val}: {len(row_shapes_sorted)} shapes (sorted left-to-right)")
            for s in row_shapes_sorted:
                print(f"  {s['standard_type']} (id: {s['id']}, PinX: {s['PinX']})")

if __name__ == "__main__":
    main()

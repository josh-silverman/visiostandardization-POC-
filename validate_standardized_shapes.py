import os
import json

REQUIRED_FIELDS = ['id', 'master', 'PinX', 'PinY', 'Width', 'Height']
CONNECTOR_FIELDS = ['BeginX', 'BeginY', 'EndX', 'EndY']

def validate_shape(shape):
    issues = []
    # Required fields
    for field in REQUIRED_FIELDS:
        if shape.get(field) is None:
            issues.append(f"Missing field: {field}")

    # Type mapping
    if shape.get('standard_type') == 'Unmapped':
        issues.append("Unmapped standard_type")

    # Connector endpoints
    if shape.get('standard_type') == 'Connector':
        for field in CONNECTOR_FIELDS:
            if shape.get(field) is None:
                issues.append(f"Connector missing endpoint: {field}")

    # Non-empty text for boxes
    if shape.get('standard_type') in ('Rectangle', 'Ellipse'):
        text = shape.get('text', '').strip()
        if not text:
            issues.append("Box shape missing or empty text")

    return issues

def validate_file(json_path):
    with open(json_path, 'r') as f:
        shapes = json.load(f)
    results = []
    for i, shape in enumerate(shapes):
        issues = validate_shape(shape)
        if issues:
            results.append({
                'shape_index': i,
                'shape_id': shape.get('id'),
                'issues': issues
            })
    return len(shapes), results

def main():
    files = [f for f in os.listdir('.') if f.startswith('standardized_page') and f.endswith('.json')]
    if not files:
        print("No standardized_page*.json files found.")
        return

    for file in sorted(files):
        print(f"\nValidating {file}")
        shape_count, issues = validate_file(file)
        report_path = file.replace('.json', '_validation_report.txt')
        with open(report_path, 'w') as report:
            report.write(f"Validation report for {file}\n")
            report.write(f"Total shapes: {shape_count}\n")
            if not issues:
                report.write("All shapes passed validation.\n")
                print("  All shapes passed validation.")
            else:
                report.write(f"{len(issues)} shapes with issues:\n")
                for entry in issues:
                    report.write(f"  Shape index {entry['shape_index']} (id: {entry['shape_id']}):\n")
                    for issue in entry['issues']:
                        report.write(f"    - {issue}\n")
                print(f"  {len(issues)} shapes with issues. See {report_path}")

if __name__ == "__main__":
    main()

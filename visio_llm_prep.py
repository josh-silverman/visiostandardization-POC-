import json
import os

# Configurable paths
PAGE_JSON = 'parsed_json/pages/page1.json'
MASTERS_JSON = 'parsed_json/masters/masters.json'
OUTPUT_SUMMARY = 'llm_prompt/page1_llm_prompt.json'

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def flatten_shape(shape, master_lookup):
    # Retain all original fields, but make it easier to read/edit
    master_id = shape.get('@Master')
    master = master_lookup.get(master_id, {})
    result = {
        'ShapeID': shape.get('@ID'),
        'Type': shape.get('@Type'),
        'MasterID': master_id,
        'MasterName': master.get('@NameU', ''),
        'MasterRaw': master,  # Full master record for reference
        'OriginalFields': shape,  # All original fields, for round-tripping
    }
    return result

def prepare_llm_prompt(page_json, masters_json):
    # Build master lookup
    masters = masters_json["http://schemas.microsoft.com/office/visio/2012/main:Masters"]["http://schemas.microsoft.com/office/visio/2012/main:Master"]
    master_lookup = {m["@ID"]: m for m in masters}

    # Get all shapes (could be a list or dict)
    shapes = page_json["http://schemas.microsoft.com/office/visio/2012/main:PageContents"]["http://schemas.microsoft.com/office/visio/2012/main:Shapes"]["http://schemas.microsoft.com/office/visio/2012/main:Shape"]
    if not isinstance(shapes, list):
        shapes = [shapes]

    # Prepare flat summary for LLM
    llm_prompt = {
        'PageSummary': {
            'Shapes': [flatten_shape(s, master_lookup) for s in shapes],
        },
        'MasterReference': master_lookup,  # Full master info
        'Instructions': (
            "You are an expert diagram assistant. "
            "Here is a Visio diagram in structured JSON. "
            "You may suggest improvements, such as moving shapes, renaming text, or changing properties. "
            "Preserve the structure and all fields. "
            "To change a shape, edit the relevant fields in 'OriginalFields'. "
            "To add a shape, append a new entry to the 'Shapes' list, using the same structure. "
            "Only return the JSON, with all original fields, after your edits."
        )
    }
    return llm_prompt

def main():
    os.makedirs(os.path.dirname(OUTPUT_SUMMARY), exist_ok=True)
    page_json = load_json(PAGE_JSON)
    masters_json = load_json(MASTERS_JSON)
    llm_prompt = prepare_llm_prompt(page_json, masters_json)
    with open(OUTPUT_SUMMARY, 'w', encoding='utf-8') as f:
        json.dump(llm_prompt, f, indent=2, ensure_ascii=False)
    print(f"LLM prompt written to {OUTPUT_SUMMARY}")

if __name__ == '__main__':
    main()

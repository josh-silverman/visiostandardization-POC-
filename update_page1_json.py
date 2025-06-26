import json
import copy

# Paths
ORIG_PAGE_JSON = "parsed_json/pages/page1.json"          # original parsed
LLM_MERGED = "llm_prompt/page1_llm_prompt_merged.json"   # LLM-merged edits
OUT_PAGE_JSON = "roundtrip_json/pages/page1.json"        # output

def main():
    # Load originals
    with open(ORIG_PAGE_JSON, "r", encoding="utf-8") as f:
        orig_page = json.load(f)
    with open(LLM_MERGED, "r", encoding="utf-8") as f:
        llm = json.load(f)

    # Get mapping from ID -> updated shape fields
    updated_shapes = {s["ShapeID"]: s["OriginalFields"] for s in llm["PageSummary"]["Shapes"]}

    # Deep copy original so we don't mutate it
    new_page = copy.deepcopy(orig_page)

    # Find the shapes array in the original structure (with correct namespace keys)
    ns = "http://schemas.microsoft.com/office/visio/2012/main"
    shapes_list = new_page[f"{ns}:PageContents"][f"{ns}:Shapes"][f"{ns}:Shape"]

    # Update shapes in-place by ID
    for i, shape in enumerate(shapes_list):
        sid = shape["@ID"]
        if sid in updated_shapes:
            shapes_list[i] = updated_shapes[sid]

    # Save to output
    import os
    os.makedirs(os.path.dirname(OUT_PAGE_JSON), exist_ok=True)
    with open(OUT_PAGE_JSON, "w", encoding="utf-8") as f:
        json.dump(new_page, f, indent=2, ensure_ascii=False)
    print(f"Wrote updated page JSON to {OUT_PAGE_JSON}")

if __name__ == "__main__":
    main()

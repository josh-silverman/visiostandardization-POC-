import json

# --- 1. File paths ---
ORIGINAL_JSON = "llm_prompt/page1_llm_prompt.json"           # Original diagram
PATCH_JSON = "llm_prompt/enhanced_diagram_llm.json"          # LLM output (patch)
MERGED_JSON = "llm_prompt/page1_llm_prompt_merged.json"      # Result after applying patch

# --- 2. Load the original diagram ---
with open(ORIGINAL_JSON, "r", encoding="utf-8") as f:
    original = json.load(f)

# --- 3. Load the patch (changed shapes only) ---
with open(PATCH_JSON, "r", encoding="utf-8") as f:
    patch = json.load(f)

# --- 4. Build a ShapeID -> patch object dictionary ---
patch_map = {obj["ShapeID"]: obj for obj in patch}

# --- 5. Replace shapes in the original with the patched ones ---
shapes = original["PageSummary"]["Shapes"]   # Adjust this path if needed

for i, shape in enumerate(shapes):
    sid = shape.get("ShapeID")
    if sid in patch_map:
        shapes[i] = patch_map[sid]

# --- 6. Write out the merged JSON ---
with open(MERGED_JSON, "w", encoding="utf-8") as f:
    json.dump(original, f, indent=2, ensure_ascii=False)

print(f"Merged JSON saved to {MERGED_JSON}")

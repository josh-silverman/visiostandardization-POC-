import os
import json
import requests
import re
from dotenv import load_dotenv

# --- 1. Load environment variables from .env ---
load_dotenv()

API_BASE = os.getenv("AZURE_OPENAI_API_BASE")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

if not (API_BASE and API_KEY and DEPLOYMENT):
    raise EnvironmentError("Missing one or more required Azure OpenAI environment variables.")

# --- 2. Load the input JSON ---
INPUT_JSON = "page1.json"
OUTPUT_JSON = "enhanced_diagram_full_page1.json"

if not os.path.exists(INPUT_JSON):
    raise FileNotFoundError(f"Input file not found: {INPUT_JSON}")

with open(INPUT_JSON, "r", encoding="utf-8") as f:
    diagram_json = json.load(f)

# --- 3. Compose the user prompt for transformation ---
user_prompt = """
You are a diagram JSON standardizer and enhancer.

Given the following Visio diagram JSON, do the following for each shape and connection:
- Ensure every shape has: "id" (string), "type", "master", "cells", "text", "role", "label", and "FillColor".
- For connector shapes (master "9"), set "role": "connector", set cells["FillColor"] = 16777215 (white), and set cells["LineColor"] = 0 (black).
- For non-connector shapes, set "role": "person" (or "group" if you infer a grouping), and set cells["FillColor"] = 15790320 (light blue, e.g., AliceBlue).
- If you use a "group" field, you may assign a unique fill color per group instead of by role.
- If a shape is missing "text", set it to the "label" or to "Unnamed".
- For each shape, add a "label" field: use the "text" if present, otherwise use "Unnamed".
- Ensure all "id" fields and all references in "connections" are strings, and that all referenced IDs exist in the "shapes" list.
- If you can, infer and add a "group" field (e.g., "family", "department", or "none").
- If you can, add a "direction" field with values "start", "end", or "middle" based on the connections (e.g., "start" = no incoming, "end" = no outgoing).
- If there are missing or invalid fields, fill or correct them.
- At the end, provide a one-paragraph summary of the diagram (who, how many, how they're connected).

For color fields, always use integer values (not strings) for colors.

Return only the updated JSON and the summary, no markdown, no explanation.

Here is the original JSON:
""" + json.dumps(diagram_json, indent=2)

# --- 4. Prepare the Azure OpenAI API call ---
headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY
}

endpoint = f"{API_BASE}/openai/deployments/{DEPLOYMENT}/chat/completions?api-version={API_VERSION}"

payload = {
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_prompt}
    ],
    "temperature": 0.2,
    "max_tokens": 6000
}

# --- 5. Make the API call ---
print("Sending request to Azure OpenAI...")
response = requests.post(endpoint, headers=headers, json=payload)
if response.status_code != 200:
    print("Error:", response.status_code, response.text)
    exit(1)

result = response.json()

# --- 6. Extract and save the LLM's response content as JSON ---
try:
    enhanced_content = result["choices"][0]["message"]["content"]

    # Remove markdown code blocks, if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", enhanced_content)
    if match:
        enhanced_content = match.group(1).strip()

    # Split at 'Summary:'
    summary_split = enhanced_content.split("Summary:", 1)
    json_text = summary_split[0].strip()
    summary_text = summary_split[1].strip() if len(summary_split) > 1 else ""

    enhanced_json = json.loads(json_text)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(enhanced_json, f, indent=2, ensure_ascii=False)
    print(f"LLM output saved to {OUTPUT_JSON}")

    if summary_text:
        with open("diagram_summary.txt", "w", encoding="utf-8") as f:
            f.write(summary_text)
        print("Diagram summary saved to diagram_summary.txt")

except Exception as e:
    print("Failed to extract or parse LLM response:", e)
    print("Raw response content:")
    print(enhanced_content)
    exit(1)


import os
import json
import requests
from dotenv import load_dotenv

# — 1. Load environment variables from .env —
load_dotenv()

API_BASE = os.getenv("AZURE_OPENAI_API_BASE")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

# — 2. Path to your parsed JSON —
PARSED_JSON_PATH = "parse_visio/page1_extracted.json"
OUTPUT_JSON_PATH = "page1_standardized.json"  # ← Output path

# — 3. Define your editing task here! —
editing_task = (
    "Change the color of all text, and labels, including the text inside the dynamic connectors, to black and make them bold."
    "Change the font of all text and labels, including text inside dynamic connectors, to a uniform size: V='0.1388888888888889'"
    "Change the color of all connectors, and dynamic connectors in the diagram to blue."
)

# — Function to process each chunk —
def process_chunk(json_chunk, editing_task):
    prompt_instructions = build_prompt(json_chunk, editing_task)

    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY
    }
    endpoint = f"{API_BASE}/openai/deployments/{DEPLOYMENT}/chat/completions?api-version={API_VERSION}"

    payload = {
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert in Visio diagrams, Visio XML, and Visio-to-JSON conversion. "
                    "You can interpret and execute high-level, non-technical editing requests by mapping them to correct JSON edits. "
                    "Always maintain the JSON structure and integrity. "
                    "Output ONLY the updated JSON, with no explanations or formatting."
                )
            },
            {"role": "user", "content": prompt_instructions}
        ],
        "temperature": 0.0,
        "max_tokens": 16000
    }

    print("Sending request to Azure OpenAI for a chunk...")
    response = requests.post(endpoint, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()

    updated_json_str = result["choices"][0]["message"]["content"]

    try:
        updated_json = json.loads(updated_json_str)
        print("Chunk processed successfully.")
        return updated_json
    except json.JSONDecodeError:
        print("WARNING: Output is not valid JSON for the chunk. Raw response below:")
        print(updated_json_str)
        return None

# — 4. Build the LLM prompt —
def build_prompt(json_data, editing_task):
    prompt = f"""
Background:
- Microsoft Visio diagrams are commonly used to visually represent processes, systems, or organizational structures.
- These diagrams are saved in the .vsdx format, which internally consists of a collection of XML files.
- The XML files describe all shapes, connectors, formatting, and metadata of the diagram.
- For automation and AI-based editing, the XML data is often parsed and converted into structured JSON, with every shape, connector, and property explicitly represented.

JSON Structure:
- The “shapes” section contains individual elements of the diagram, each with properties such as size, position, and styling. These elements can be shapes, groups, or foreign objects.
- The “connectors” section defines the connections between shapes, specifying which parts of the shapes are connected.
- The “colors” section lists color definitions used throughout the diagram, with each color having an index and an RGB value.
- The “document_properties” section contains metadata about the document, like creation and edit timestamps.

Color Information:
- The diagram includes specific color and theme settings defined in the XML, now represented in the JSON.

Colors: {json.dumps(json_data.get('colors', []), indent=2)}

Purpose of the Task:
- Your task is to understand the structure of this Visio diagram as represented in the JSON, and to make specific edits as described below.

Editing Task (as described by a non-technical user):
{editing_task}

Instructions & Constraints:
- Interpret the editing task as a non-technical user would intend, even if the request is vague or general.
- Carefully analyze the provided JSON, which directly mirrors the Visio XML structure.
- Map the user’s plain-language request to the correct modification(s) in the JSON structure, using your knowledge of Visio XML and JSON conventions.
- When performing the edit, maintain the integrity and structure of the JSON—do not remove, rename, or break any fields not directly related to the change.
- Ensure that your change is consistent with the existing schema; for example, use the same style for cell values, sections, or attributes as already present.
- When changing colors, use the color references provided in the colors section.
- Make sure the updated JSON document contains the same amount of information as the original, with no fields removed or renamed unless explicitly requested. Just the values of the fields should change.
- Output ONLY the full, updated JSON document as your response, with no explanations, markdown, or extra formatting.

Input JSON:
{json.dumps(json_data, indent=2)}
"""
    return prompt

# — 5. Read the parsed JSON —
with open(PARSED_JSON_PATH, "r", encoding="utf-8") as f:
    json_data = json.load(f)

# — 6. Process the JSON in chunks —
shapes = json_data.get("shapes", [])
chunk_size = 5  # Define a manageable chunk size
updated_shapes = []

for i in range(0, len(shapes), chunk_size):
    chunk = {"shapes": shapes[i:i + chunk_size]}
    updated_chunk = process_chunk(chunk, editing_task)
    if updated_chunk:
        updated_shapes.extend(updated_chunk.get("shapes", []))

# — 7. Combine and save the updated JSON —
json_data["shapes"] = updated_shapes

with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as outf:
    json.dump(json_data, outf, indent=2)

print(f"\nUpdated JSON saved to: {OUTPUT_JSON_PATH}")

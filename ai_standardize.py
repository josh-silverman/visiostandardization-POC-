import os
import json
import requests
from dotenv import load_dotenv

def run_ai_standardize(
    parsed_json_path="parse_visio/page1_extracted.json",
    output_json_path="page1_standardized.json",
    editing_task=None,
    chunk_size=5
):
    # — 1. Load environment variables from .env —
    load_dotenv()

    API_BASE = os.getenv("AZURE_OPENAI_API_BASE")
    API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

    # — 3. Define your editing task here! —
    if not editing_task:
        editing_task = (
            "For every Section with '@attrs':{'N':'Character'} (including all nested shapes):\n"
            "- For each Row, remove any Cell where N is 'Font', 'Color', 'Style', or 'Size'.\n"
            "- Then add: {'N':'Font','V':'Calibri'}, {'N':'Color','V':'#000000'}, {'N':'Style','V':'17'}, {'N':'Size','V':'0.10','U':'PT'}.\n"
            "Apply this to all text, including shape labels and connector text.\n"
            "For every connector line (including dynamic connectors), in each Section with '@attrs':{'N':'Line'}:\n"
            "- Remove any Cell where N is 'LineColor' or 'LineWeight'.\n"
            "- Add a Cell: {'N':'LineColor','V':'#0066FF'}.\n"
            "- Add a Cell: {'N':'LineWeight','V':'0.01388888888888889','U':'PT'}.\n"
            "Do not change any other fields or parts of the JSON or XML."
        )

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

Editing Task:
{editing_task}

Instructions & Constraints:
- Interpret the editing task as a non-technical user would intend, even if the request is vague or general.
- Carefully analyze the provided JSON, which directly mirrors the Visio XML structure.
- Map the user’s plain-language request to the correct modification(s) in the JSON structure, using your knowledge of Visio XML and JSON conventions.
- Ensure that your change is consistent with the existing schema; for example, use the same style for cell values, sections, or attributes as already present.
- When changing colors, use the color references provided in the colors section.
- Output ONLY the full, updated JSON document as your response, with no explanations, markdown, or extra formatting.

Input JSON:
{json.dumps(json_data, indent=2)}
"""
        return prompt

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

    # — 5. Read the parsed JSON —
    with open(parsed_json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # — 6a. Process the "shapes" in chunks —
    shapes = json_data.get("shapes", [])
    updated_shapes = []
    for i in range(0, len(shapes), chunk_size):
        chunk = {"shapes": shapes[i:i + chunk_size]}
        updated_chunk = process_chunk(chunk, editing_task)
        if updated_chunk:
            updated_shapes.extend(updated_chunk.get("shapes", []))
    json_data["shapes"] = updated_shapes

    # — 6b. Process the "connectors" in chunks if present —
    if "connectors" in json_data:
        connectors = json_data.get("connectors", [])
        updated_connectors = []
        for i in range(0, len(connectors), chunk_size):
            chunk = {"connectors": connectors[i:i + chunk_size]}
            updated_chunk = process_chunk(chunk, editing_task)
            if updated_chunk:
                updated_connectors.extend(updated_chunk.get("connectors", []))
        json_data["connectors"] = updated_connectors

    # — 7. Combine and save the updated JSON —
    with open(output_json_path, "w", encoding="utf-8") as outf:
        json.dump(json_data, outf, indent=2)

    print(f"\nUpdated JSON saved to: {output_json_path}")

# For CLI/standalone use
if __name__ == "__main__":
    run_ai_standardize()
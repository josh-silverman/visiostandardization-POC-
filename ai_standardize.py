import os
import json
import requests
from dotenv import load_dotenv

# --- 1. Load environment variables from .env ---
load_dotenv()

API_BASE = os.getenv("AZURE_OPENAI_API_BASE")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

# --- 2. Path to your parsed JSON ---
PARSED_JSON_PATH = "parse_visio/page1_extracted.json"
OUTPUT_JSON_PATH = "page1_standardized.json"  # <--- Output path

# --- 3. Define your editing task here! ---
editing_task = (
    "First, please bold the text in every shape. Second, change all connector lines to dashed style"
)

# --- 4. Build the LLM prompt ---
def build_prompt(json_data, editing_task):
    prompt = f"""
Background:
Microsoft Visio diagrams are commonly used to visually represent processes, systems, or organizational structures.
These diagrams are saved in the .vsdx format, which internally consists of a collection of XML files.
The XML files describe all shapes, connectors, formatting, and metadata of the diagram.
For automation and AI-based editing, the XML data is often parsed and converted into structured JSON, with every shape, connector, and property explicitly represented.

Files Being Used:
- masters.xml: Defines the master shapes (e.g., rectangles, circles, connectors) used in the diagram.
- page1.xml: Contains the actual diagram content—shapes, their properties, text, and connections.
- custom.xml: Stores document-level custom properties.

All this data has been extracted and provided as a single, comprehensive JSON document, preserving the full structure and variable names as in the original Visio XML.

Purpose of the Task:
Your job is to understand the structure of this Visio diagram as represented in the JSON, and to make a specific edit as described below.

Editing Task (as described by a non-technical user):
{editing_task}

Instructions & Constraints:
- Interpret the editing task as a non-technical user would intend, even if the request is vague or general.
- Carefully analyze the provided JSON, which directly mirrors the Visio XML structure.
- Map the user’s plain-language request to the correct modification(s) in the JSON structure, using your knowledge of Visio XML and JSON conventions.
- When performing the edit, maintain the integrity and structure of the JSON—do not remove, rename, or break any fields not directly related to the change.
- Ensure that your change is consistent with the existing schema; for example, use the same style for cell values, sections, or attributes as already present.
- Do not invent new fields or structures unless explicitly instructed; all modifications should be schema-compliant and minimal.
- Output ONLY the full, updated JSON document as your response, with no explanations, markdown, or extra formatting.

Input JSON:
{json.dumps(json_data, indent=2)}
"""
    return prompt

# --- 5. Read the parsed JSON ---
with open(PARSED_JSON_PATH, "r", encoding="utf-8") as f:
    json_data = json.load(f)

prompt_instructions = build_prompt(json_data, editing_task)

# --- 6. Prepare the Azure OpenAI API call ---
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
    "temperature": 0.2,
    "max_tokens": 14000
}

# --- 7. Send the request to Azure OpenAI ---
print("Sending request to Azure OpenAI...")
response = requests.post(endpoint, headers=headers, json=payload)
response.raise_for_status()
result = response.json()

# --- 8. Extract and print the updated JSON from the LLM output ---
updated_json_str = result["choices"][0]["message"]["content"]

# Try to parse and pretty-print the JSON (if possible), and save to file
try:
    updated_json = json.loads(updated_json_str)
    print("SUCCESS: Output is valid JSON.\n")
    print(json.dumps(updated_json, indent=2))
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as outf:
        json.dump(updated_json, outf, indent=2)
    print(f"\nUpdated JSON saved to: {OUTPUT_JSON_PATH}")
except Exception as e:
    print("WARNING: Output is not valid JSON. Raw response below:\n")
    print(updated_json_str)

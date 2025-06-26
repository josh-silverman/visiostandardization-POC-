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

if not (API_BASE and API_KEY and DEPLOYMENT):
    raise EnvironmentError("Missing one or more required Azure OpenAI environment variables.")

# --- 2. Load the input files ---
ORIGINAL_JSON_FILE = "diagram_llm_ready_page1.json"
ANALYSIS_FILE = "enhanced_diagram_full_page1.txt"
OUTPUT_JSON_FILE = "standardized.json"

for file in [ORIGINAL_JSON_FILE, ANALYSIS_FILE]:
    if not os.path.exists(file):
        raise FileNotFoundError(f"Required input file not found: {file}")

with open(ORIGINAL_JSON_FILE, "r", encoding="utf-8") as f:
    original_json = json.load(f)
with open(ANALYSIS_FILE, "r", encoding="utf-8") as f:
    analysis = f.read()

# --- 3. Compose system and user prompts ---
system_prompt = """
You are a data transformation assistant.

Given:
- The original Visio diagram JSON (below)
- The standardization plan (below)

Your task:
1. Transform the original JSON so it fully conforms to the provided standardization plan, while also maintaining its original structure. That means it must maintain all document_properties, diagram_settings, colors, shapes, connectors, and masters as the original JSON
2. Output ONLY the standardized JSON (no explanation, no markdown formatting).
"""

user_prompt = (
    "Original JSON:\n"
    + json.dumps(original_json, indent=2)
    + "\n\nStandardization Plan (reference):\n"
    + analysis
)

# --- 4. Prepare the Azure OpenAI API call ---
headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY
}

endpoint = f"{API_BASE}/openai/deployments/{DEPLOYMENT}/chat/completions?api-version={API_VERSION}"

payload = {
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    "temperature": 0,
    "max_tokens": 13000
}

# --- 5. Make the API call ---
print("Sending request to Azure OpenAI...")
response = requests.post(endpoint, headers=headers, json=payload)
if response.status_code != 200:
    print("Error:", response.status_code, response.text)
    exit(1)

result = response.json()

# --- 6. Extract and save the LLM's response content ---
try:
    standardized_content = result["choices"][0]["message"]["content"].strip()
    # Remove markdown code block if present
    if standardized_content.startswith("```json"):
        standardized_content = standardized_content[len("```json"):].strip()
    if standardized_content.endswith("```"):
        standardized_content = standardized_content[:-3].strip()
except Exception as e:
    print("Failed to extract LLM response:", e)
    print(json.dumps(result, indent=2))
    exit(1)

with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
    f.write(standardized_content)

print(f"Standardized JSON saved to {OUTPUT_JSON_FILE}")

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

# --- 2. Load the LLM-friendly Visio JSON ---
INPUT_JSON = "llm_prompt/page1_llm_prompt.json"   # <-- Use your LLM prompt file
OUTPUT_JSON = "llm_prompt/enhanced_diagram_llm.json"

if not os.path.exists(INPUT_JSON):
    raise FileNotFoundError(f"Input file not found: {INPUT_JSON}")

with open(INPUT_JSON, "r", encoding="utf-8") as f:
    diagram_json = json.load(f)

# --- 3. Compose the user prompt for the LLM ---
# You may adjust these instructions for your specific use-case
prompt_instructions = """
You are a Visio diagram expert. Here is a Visio page as JSON.

Please make these changes for every shape:
- Bold the text within each shape.

Only output the JSON objects for the shapes or fields that were changed. 
Do not output the entire diagram or any unchanged content. 
Use the exact same variable and field names as in the input, unless adding new fields as requested.
If you add a new shape, output its full JSON object. 
If you change only part of an object, output the full object for that shape, not just the changed field.
Do not include any explanation or summary.

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
        {"role": "system", "content": "You are an expert diagram assistant. Output only valid JSON."},
        {"role": "user", "content": prompt_instructions}
    ],
    "temperature": 0.2,
    "max_tokens": 14000
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

    # Try to parse JSON
    enhanced_json = json.loads(enhanced_content)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(enhanced_json, f, indent=2, ensure_ascii=False)
    print(f"LLM output saved to {OUTPUT_JSON}")

except Exception as e:
    print("Failed to extract or parse LLM response:", e)
    print("Raw response content:")
    print(enhanced_content)
    exit(1)

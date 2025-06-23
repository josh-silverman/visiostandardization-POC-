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
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")  # fallback default

# --- 2. Load standardized JSON ---
INPUT_JSON = "standardized_page1.json"
OUTPUT_JSON = "enhanced_standardized_page1.json"

with open(INPUT_JSON, "r") as f:
    shapes = json.load(f)

# --- 3. Prepare AI prompt ---
PROMPT = (
    "You are an expert in professional network diagramming. "
    "Given the following JSON representing shapes and connectors from a Visio diagram, please:\n"
    "- Standardize all shape labels to the format '[ShapeType] [ID]'.\n"
    "- For rectangles, ensure their text field follows this format.\n"
    "- Do not change the positions or connections.\n"
    "- Return ONLY the updated JSON, nothing else.\n\n"
    "JSON:\n"
    f"{json.dumps(shapes, indent=2)}"
)

# --- 4. Call Azure OpenAI GPT-4o API ---
headers = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}
endpoint = f"{API_BASE}openai/deployments/{DEPLOYMENT}/chat/completions?api-version={API_VERSION}"

data = {
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant for network diagram standardization."
        },
        {
            "role": "user",
            "content": PROMPT
        }
    ],
    "max_tokens": 2500,
    "temperature": 0,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0
}

print("Sending request to Azure OpenAI...")

try:
    response = requests.post(endpoint, headers=headers, json=data, timeout=60)
    response.raise_for_status()
except Exception as e:
    print(f"API request failed: {e}")
    exit(1)

result = response.json()
try:
    ai_content = result['choices'][0]['message']['content']
except Exception as e:
    print(f"Could not extract AI response: {e}")
    print("Raw response:", result)
    exit(1)

# --- 5. Extract JSON from AI response ---
def extract_json(text):
    # Try to extract from a code block first
    match = re.search(r'```json(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Try to extract from a generic code block
    match = re.search(r'```(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Otherwise, assume the entire text is JSON
    return text.strip()

json_str = extract_json(ai_content)

# --- 6. Parse and validate JSON ---
try:
    enhanced_shapes = json.loads(json_str)
except Exception as e:
    print("Failed to parse AI output as JSON!")
    print("AI output was:\n", ai_content)
    exit(1)

# --- 7. Save the enhanced JSON ---
with open(OUTPUT_JSON, "w") as f:
    json.dump(enhanced_shapes, f, indent=2)

print(f"AI enhancement complete. Enhanced JSON saved to {OUTPUT_JSON}.")

# --- 8. Optionally print a summary ---
print(f"Original shape count: {len(shapes)}")
print(f"Enhanced shape count: {len(enhanced_shapes)}")

# If you want to see what was changed, you could diff the two dictionaries here.

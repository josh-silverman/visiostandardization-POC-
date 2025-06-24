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

# --- 2. Load the new combined JSON ---
INPUT_JSON = "diagram_full_page1.json"
OUTPUT_JSON = "enhanced_diagram_full_page1.json"

with open(INPUT_JSON, "r") as f:
    data = json.load(f)

shapes = data["shapes"]
connectors = data["connectors"]


# --- 3. Prepare AI prompt (IMPROVED) ---
PROMPT = (
    "You are an expert in professional network diagramming. "
    "Given the following JSON representing both 'shapes' and 'connectors' from a Visio diagram, please:\n"
    "- For each shape in the 'shapes' list, ensure the label/text will be visually centered and formatted correctly within the shape (e.g., add or update a 'text_align': 'center' property if available).\n"
    "- For each different shape type (use 'master_nameU' or 'master_name'), assign a visually distinct fill color (add a 'fill_color' property) to help differentiate them, using pleasant and professional colors. The same shape type must always get the same color (e.g. all rectangles are blue).\n"
    "- For connectors/arrows (entries in the 'connectors' list, i.e. those whose 'master_nameU' or 'master_name' contains 'connector'), set the 'line_weight' property to 'bold' to make arrows stand out. Ensure each connector's visual length and size are consistent. Do not change their 'text' unless it already contains a label, and keep it as-is.\n"
    "- You may adjust the diagram's shape positions (such as PinX/PinY or geometry fields) for a more logical and professional layout, but DO NOT change the shape-to-shape connections specified by 'begin_shape' and 'end_shape' fields in the connectors.\n"
    "- Retain all other properties and structure, including all fields present in both 'shapes' and 'connectors'.\n"
    "- Return ONLY the updated JSON in the same structure, nothing else.\n\n"
    "JSON:\n"
    f"{json.dumps(data, indent=2)}"
)

# --- 4. Call Azure OpenAI GPT-4o API ---
headers = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}
endpoint = f"{API_BASE}openai/deployments/{DEPLOYMENT}/chat/completions?api-version={API_VERSION}"

data_api = {
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
    "max_tokens": 5500,
    "temperature": 0,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0
}

print("Sending request to Azure OpenAI...")

try:
    response = requests.post(endpoint, headers=headers, json=data_api, timeout=90)
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
    enhanced_data = json.loads(json_str)
except Exception as e:
    print("Failed to parse AI output as JSON!")
    print("AI output was:\n", ai_content)
    exit(1)

# --- 7. No post-processing of text ---
# (We keep the text field as returned by the LLM, as instructed in the prompt.)

# --- 8. Save the enhanced JSON ---
with open(OUTPUT_JSON, "w") as f:
    json.dump(enhanced_data, f, indent=2)

print(f"AI enhancement complete. Enhanced JSON saved to {OUTPUT_JSON}.")

# --- 9. Optionally print a summary ---
print(f"Original shape count: {len(shapes)}")
print(f"Enhanced shape count: {len(enhanced_data['shapes'])}")

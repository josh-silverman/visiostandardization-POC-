# gpt_analysis.py
import base64
import openai
from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION, GPT_ENGINE_NAME

openai.api_type = "azure"
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_key = AZURE_OPENAI_API_KEY
openai.api_version = AZURE_OPENAI_API_VERSION

def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def gpt4o_analyze_image(image_path):
    b64_image = image_to_base64(image_path)
    response = openai.ChatCompletion.create(
        engine=GPT_ENGINE_NAME,
        messages=[
            {"role": "system", "content": "You are an expert in analyzing Visio flowcharts. Extract all shapes, connectors, and their properties in JSON format."},
            {"role": "user", "content": [
                {"type": "text", "text": "Analyze this Visio diagram and return a JSON object with all shapes, connectors, text, and their spatial layout."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}}
            ]}
        ],
        response_format="json"
    )
    content = response.choices[0].message["content"]
    return content

def gpt4o_analyze_xml(xml_content):
    response = openai.ChatCompletion.create(
        engine=GPT_ENGINE_NAME,
        messages=[
            {"role": "system", "content": "Parse Visio XML and extract shapes, text, and connectors in JSON format."},
            {"role": "user", "content": f"XML content: {xml_content}"}
        ],
        response_format="json"
    )
    content = response.choices[0].message["content"]
    return content

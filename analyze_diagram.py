import openai
import base64
import os

def analyze_image_with_gpt4o(image_path, config):
    # Read and encode the image to base64
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # Build the proper image_url for OpenAI's vision endpoint
    image_url = f"data:image/png;base64,{image_b64}"

    # Pick the model name/deployment name
    # For Azure OpenAI: use deployment name (e.g., "gpt-4o")
    # For OpenAI cloud: use model name (e.g., "gpt-4o")
    model_name = config.get("AZURE_OPENAI_DEPLOYMENT") or config.get("OPENAI_MODEL", "gpt-4o")

    # Compose your prompt
    user_prompt = "Extract all shapes, connectors, and texts from this diagram as structured JSON."

    # Call the OpenAI API (works for both Azure OpenAI and OpenAI cloud)
    response = openai.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        max_tokens=2048,
        temperature=0.0,
    )

    # Return just the content (the model's reply)
    return response.choices[0].message.content

# Example usage:
# config = {"AZURE_OPENAI_DEPLOYMENT": "gpt-4o"}
# analyze_image_with_gpt4o("sample process.png", config)

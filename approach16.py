import streamlit as st
import os
import openai
from dotenv import load_dotenv
import tempfile

# Load environment variables
load_dotenv()
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Initialize Azure OpenAI client
openai.api_type = "azure"
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = "2024-02-15-preview"
openai.api_key = AZURE_OPENAI_API_KEY

def combine_svgs_with_gpt(main_svg_content, footer_svg_content):
    """Use Azure OpenAI GPT to combine SVG content."""
    prompt = f"""
    You are provided with two SVG files. Combine the contents of both SVGs into a single SVG file.
    Ensure the output is valid XML, starting with an <svg> tag, and that all elements from both SVGs are included.

    Main SVG Content:
    {main_svg_content.decode("utf-8")}

    Footer SVG Content:
    {footer_svg_content.decode("utf-8")}
    """
    
    response = openai.ChatCompletion.create(
        engine=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3000
    )
    
    combined_content = response.choices[0].message['content'].strip()
    return combined_content

# Streamlit UI
st.title("SVG Merger with Azure OpenAI GPT")

st.write("Upload the main diagram SVG and the footer SVG to merge them using Azure OpenAI.")

# File uploaders for the two SVG files
main_svg_file = st.file_uploader("Upload Main Diagram SVG", type="svg")
footer_svg_file = st.file_uploader("Upload Footer SVG", type="svg")

if main_svg_file and footer_svg_file:
    # Read the contents of the uploaded files
    main_svg_content = main_svg_file.read()
    footer_svg_content = footer_svg_file.read()

    # Combine SVG content with Azure OpenAI
    combined_svg_content = combine_svgs_with_gpt(main_svg_content, footer_svg_content)

    # Save the result to a temporary file to display it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".svg", mode='w', encoding='utf-8') as temp_file:
        temp_file.write(combined_svg_content)
        temp_file_path = temp_file.name

    # Display the combined SVG as an image
    st.image(temp_file_path, caption='Combined SVG', use_container_width=True)
    
    # Provide a download link for the combined SVG
    st.download_button(
        label="Download Combined SVG",
        data=combined_svg_content,
        file_name="combined_diagram.svg",
        mime="image/svg+xml"
    )
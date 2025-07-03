import streamlit as st
from lxml import etree
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

def transform_svg_with_gpt(svg_content, purpose):
    """Use Azure OpenAI GPT-4o to transform SVG content."""
    prompt = f"""
    You are provided with an SVG file representing {purpose}. 
    Edit the SVG content to optimize its structure and ensure it is ready for merging with another SVG.
    
    Please ensure the output is valid XML, starting with an <svg> tag.
    
    SVG Content:
    {svg_content.decode("utf-8")}
    """
    
    response = openai.ChatCompletion.create(
        engine=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500
    )
    
    transformed_content = response.choices[0].message['content'].strip()
    
    # Display the generated output
    st.text("Generated SVG Content:")
    st.text(transformed_content)
    
    # Ensure the output starts with '<' and looks like SVG
    if not transformed_content.startswith('<svg'):
        st.error("Generated content does not appear to be valid SVG XML.")
        return None
    
    # Validate the transformed content as XML
    try:
        etree.fromstring(transformed_content.encode("utf-8"))
    except etree.XMLSyntaxError as e:
        st.error(f"Generated SVG content is not valid XML: {e}")
        return None
    
    return transformed_content

def merge_svgs(test_svg_content, footer_svg_content):
    """Merge footer SVG elements into the test diagram SVG."""
    # Parse the SVG content
    test_svg = etree.fromstring(test_svg_content)
    footer_svg = etree.fromstring(footer_svg_content)

    # Append each element from the footer SVG to the test SVG
    for element in footer_svg:
        test_svg.append(element)

    # Return the merged SVG as a string
    return etree.tostring(test_svg, pretty_print=True)

# Streamlit UI
st.title("SVG Merger with Azure OpenAI GPT-4o")

st.write("Upload the test diagram SVG and the footer SVG to merge them. Azure OpenAI will edit and optimize the SVG content.")

# File uploaders for the two SVG files
test_svg_file = st.file_uploader("Upload Test Diagram SVG", type="svg")
footer_svg_file = st.file_uploader("Upload Footer SVG", type="svg")

if test_svg_file and footer_svg_file:
    # Read the contents of the uploaded files
    test_svg_content = test_svg_file.read()
    footer_svg_content = footer_svg_file.read()

    # Transform SVG content with Azure OpenAI
    st.subheader("Azure OpenAI Transformation")
    transformed_test_svg_content = transform_svg_with_gpt(test_svg_content, "test diagram")
    transformed_footer_svg_content = transform_svg_with_gpt(footer_svg_content, "footer")

    # Ensure both transformations are valid before proceeding
    if transformed_test_svg_content and transformed_footer_svg_content:
        # Merge the SVG files
        merged_svg_content = merge_svgs(transformed_test_svg_content.encode("utf-8"), transformed_footer_svg_content.encode("utf-8"))

        # Save the result to a temporary file to display it
        with tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as temp_file:
            temp_file.write(merged_svg_content)
            temp_file_path = temp_file.name

        # Display the merged SVG
        st.image(temp_file_path, caption='Merged SVG', use_column_width=True)
        
        # Provide a download link for the merged SVG
        st.download_button(
            label="Download Merged SVG",
            data=merged_svg_content,
            file_name="merged_diagram.svg",
            mime="image/svg+xml"
        )

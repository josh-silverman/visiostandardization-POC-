import streamlit as st
import os
from dotenv import load_dotenv
import openai

# Load environment variables (AZURE_OPENAI_DEPLOYMENT, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY)
load_dotenv()
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2024-02-15-preview"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")

def edit_svg_with_llm_azure(svg_content):
    system = (
        "You are an expert SVG editor AI. When given SVG code and an instruction, "
        "respond ONLY with the modified SVG code."
    )
    user = (
        f"Here is an SVG:\n\n{svg_content}\n\n"
        "Instruction: In the SVG, find the <g> element with id='shape25-73'. "
        "Replace the text content of its <desc> element with the word 'update'. "
        "Do not change anything else. Return the full, valid SVG."
    )
    response = openai.ChatCompletion.create(
        engine=AZURE_OPENAI_DEPLOYMENT,  # Azure uses 'engine', not 'model'
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.0,
        max_tokens=4096
    )
    return response.choices[0].message.content.strip()

def main():
    st.title("SVG Table Text Box Updater (Azure OpenAI LLM)")
    st.write("Upload an SVG. All text boxes in tables will be replaced with 'update' by the LLM.")

    uploaded_file = st.file_uploader("Choose an SVG file", type="svg")

    if uploaded_file is not None:
        svg_content = uploaded_file.read().decode("utf-8")
        with st.spinner("Processing SVG with Azure OpenAI..."):
            try:
                updated_svg = edit_svg_with_llm_azure(svg_content)
                st.success("SVG updated!")
                st.markdown(f'<div>{updated_svg}</div>', unsafe_allow_html=True)
                st.download_button(
                    "Download Modified SVG",
                    data=updated_svg.encode("utf-8"),
                    file_name="updated.svg",
                    mime="image/svg+xml"
                )
            except Exception as e:
                st.error(f"Error updating SVG: {e}")

if __name__ == "__main__":
    main()

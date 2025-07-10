import streamlit as st
import os
from dotenv import load_dotenv
import openai
from lxml import etree as ET

# Load environment variables
load_dotenv()
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2024-02-15-preview"
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")

def normalize_svg_dimensions(root1, root2):
    vb1 = list(map(float, root1.get('viewBox').split()))
    vb2 = list(map(float, root2.get('viewBox').split()))
    common_width = max(vb1[2], vb2[2])
    scale1 = common_width / vb1[2]
    scale2 = common_width / vb2[2]
    vb1[2] *= scale1
    vb1[3] *= scale1
    vb2[2] *= scale2
    vb2[3] *= scale2
    root1.set('viewBox', f'0 0 {vb1[2]} {vb1[3]}')
    root2.set('viewBox', f'0 0 {vb2[2]} {vb2[3]}')
    return vb1, vb2, scale1, scale2

def merge_svgs(svg1_content, svg2_content):
    root1 = ET.fromstring(svg1_content)
    root2 = ET.fromstring(svg2_content)
    vb1, vb2, scale1, scale2 = normalize_svg_dimensions(root1, root2)
    scale2 *= 1.2
    new_height = vb1[3] + vb2[3] * scale2
    root1.set('viewBox', f'0 0 {vb1[2]} {new_height}')
    root1.set('height', f'{new_height}')
    svg_ns = root1.nsmap.get(None, "http://www.w3.org/2000/svg")
    g_tag = f'{{{svg_ns}}}g' if svg_ns else 'g'
    transform_group = f'scale({scale2}) translate(0, {vb1[3] / scale2})'
    group2 = ET.Element(g_tag, attrib={'transform': transform_group})
    for element in list(root2):
        group2.append(element)
    root1.append(group2)
    merged_svg_bytes = ET.tostring(root1, encoding='utf-8', method='xml')
    return merged_svg_bytes

def edit_svg_with_llm_azure(svg_content, instruction):
    system = (
        "You are an expert SVG editor AI. When given SVG code and an instruction, "
        "respond ONLY with the modified SVG code."
    )
    user = (
        f"Here is an SVG:\n\n{svg_content}\n\n"
        f"Instruction: {instruction}\n\n"
        "Respond ONLY with the full, valid SVG code."
    )
    response = openai.ChatCompletion.create(
        engine=AZURE_OPENAI_DEPLOYMENT,  # Use 'engine' for Azure, not 'model'
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.0,
        max_tokens=4096
    )
    return response.choices[0].message.content.strip()

def main():
    st.title("Azure OpenAI SVG Merger with LLM Text Box Styling")
    st.write("Upload two SVG files to merge and style them with Azure OpenAI.")

    uploaded_file1 = st.file_uploader("Choose first SVG file", type="svg")
    uploaded_file2 = st.file_uploader("Choose second SVG file", type="svg")

    if uploaded_file1 is not None and uploaded_file2 is not None:
        svg1_content = uploaded_file1.read()
        svg2_content = uploaded_file2.read()
        with st.spinner("Merging SVGs..."):
            merged_svg_bytes = merge_svgs(svg1_content, svg2_content)
            merged_svg_str = merged_svg_bytes.decode('utf-8')
        instruction = (
            "For every <text> element in the SVG, add a blue rectangle background directly behind the text. "
            "The rectangle should have a blue fill (e.g. fill='lightblue') and a black outline (e.g. stroke='black', stroke-width='2'). "
            "Ensure rectangles are sized and positioned so that the text appears centered on the blue background. "
            "Return the modified SVG."
        )
        with st.spinner("Asking the Azure LLM to style your SVG..."):
            llm_svg = edit_svg_with_llm_azure(merged_svg_str, instruction)
        st.subheader("Final SVG with LLM-styled Text Boxes")
        st.markdown(f'<div>{llm_svg}</div>', unsafe_allow_html=True)
        st.download_button(
            "Download Final SVG",
            data=llm_svg.encode("utf-8"),
            file_name="merged_styled.svg",
            mime="image/svg+xml"
        )

if __name__ == "__main__":
    main()

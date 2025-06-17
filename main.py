# import streamlit as st
# import openai
# import os
# import base64
# import json
# import math
# import re
# from dotenv import load_dotenv

# # --- Load environment variables ---
# load_dotenv()
# AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
# AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
# AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")  # GPT-4o deployment

# # --- Initialize Azure OpenAI client ---
# openai.api_type = "azure"
# openai.api_base = AZURE_OPENAI_ENDPOINT
# openai.api_version = "2024-02-15-preview"
# openai.api_key = AZURE_OPENAI_API_KEY

# st.title("Diagram Standardizer: Convert All Shapes to Squares")

# st.markdown("""
# 1. **Upload a PNG diagram**.
# 2. **GPT-4o Vision extracts the diagram's structure**.
# 3. **All shapes are converted to squares in a new SVG diagram**.
# """)

# # --- 1. Upload PNG ---
# uploaded_file = st.file_uploader("Upload your PNG diagram", type=["png"])

# if uploaded_file is not None:
#     st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
#     st.markdown("Click the button below to extract and standardize the diagram.")

#     if st.button("Extract & Standardize"):
#         # --- 2. Send to GPT-4o Vision for JSON extraction ---
#         uploaded_file.seek(0)
#         image_bytes = uploaded_file.read()
#         image_base64 = base64.b64encode(image_bytes).decode()

#         # Prompt: ask for JSON only!
#         extraction_prompt = (
#             "Analyze this diagram. "
#             "Return ONLY a JSON object representing the shapes and relationships. "
#             "For each shape, include its label (if present), type (rectangle, ellipse, diamond, etc.), "
#             "and relationships (arrows/edges) as a list of nodes and edges. "
#             "Format: "
#             "{'nodes': [{'id': ..., 'label': ..., 'type': ...}, ...], 'edges': [{'from': ..., 'to': ...}, ...]}."
#             "Output only the JSON and nothing else."
#         )

#         with st.spinner("Sending image to Azure OpenAI GPT-4o..."):
#             try:
#                 response = openai.ChatCompletion.create(
#                     engine=AZURE_OPENAI_DEPLOYMENT,
#                     messages=[
#                         {"role": "system", "content": "You are a helpful assistant who extracts diagram structure as JSON."},
#                         {
#                             "role": "user",
#                             "content": [
#                                 {"type": "text", "text": extraction_prompt},
#                                 {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
#                             ],
#                         }
#                     ],
#                     max_tokens=700,
#                 )
#                 answer = response['choices'][0]['message']['content']

#                 # --- 3. Parse JSON from the response ---
#                 json_match = re.search(r'({.*})', answer, re.DOTALL)
#                 if not json_match:
#                     st.error("Could not extract a valid JSON block from the model response.")
#                     st.write(answer)
#                     st.stop()
#                 json_str = json_match.group(1)
#                 # Replace single quotes with double quotes for JSON
#                 json_str = json_str.replace("'", '"')
#                 try:
#                     data = json.loads(json_str)
#                 except Exception as e:
#                     st.error("Failed to parse JSON: " + str(e))
#                     st.code(json_str)
#                     st.stop()

#                 st.markdown("**Extracted Diagram JSON:**")
#                 st.code(json.dumps(data, indent=2), language="json")

#                 nodes = data.get("nodes", [])
#                 edges = data.get("edges", [])

#                 # --- 4. Standardize & Render as SVG (all shapes as squares) ---
#                 # Layout Parameters
#                 square_size = 80
#                 h_spacing = 120
#                 v_spacing = 120
#                 margin = 40
#                 font_size = 14

#                 # Simple horizontal grid layout
#                 positions = {}
#                 for idx, node in enumerate(nodes):
#                     x = margin + idx * h_spacing
#                     y = margin
#                     positions[node["id"]] = (x, y)

#                 # SVG elements
#                 svg_elements = []

#                 # Draw edges
#                 for edge in edges:
#                     from_id, to_id = edge["from"], edge["to"]
#                     x1, y1 = positions[from_id]
#                     x2, y2 = positions[to_id]
#                     # Compute direction
#                     dx = x2 - x1
#                     dy = y2 - y1
#                     length = math.hypot(dx, dy)
#                     if length == 0:
#                         length = 1
#                     ux = dx / length
#                     uy = dy / length
#                     # Start/end at square edge
#                     start_x = x1 + square_size/2 * ux
#                     start_y = y1 + square_size/2 * uy
#                     end_x = x2 - square_size/2 * ux
#                     end_y = y2 - square_size/2 * uy
#                     svg_elements.append(
#                         f'<line x1="{start_x}" y1="{start_y}" x2="{end_x}" y2="{end_y}" stroke="black" marker-end="url(#arrow)" />'
#                     )

#                 # Draw nodes as squares
#                 for node in nodes:
#                     x, y = positions[node["id"]]
#                     top_left_x = x - square_size/2
#                     top_left_y = y - square_size/2
#                     svg_elements.append(
#                         f'<rect x="{top_left_x}" y="{top_left_y}" width="{square_size}" height="{square_size}" fill="#e0e0e0" stroke="black" />'
#                     )
#                     # Centered label
#                     label = node.get("label", "")
#                     svg_elements.append(
#                         f'<text x="{x}" y="{y+font_size/2}" font-size="{font_size}" text-anchor="middle" alignment-baseline="middle">{label}</text>'
#                     )

#                 # SVG header/footer
#                 width = margin*2 + max(1, len(nodes)) * h_spacing
#                 height = margin*2 + v_spacing
#                 svg_header = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
# <defs>
#   <marker id="arrow" markerWidth="10" markerHeight="10" refX="10" refY="5" orient="auto" markerUnits="strokeWidth">
#     <path d="M0,0 L10,5 L0,10 L2,5 z" fill="#000"/>
#   </marker>
# </defs>
# '''
#                 svg_footer = '</svg>'

#                 svg_content = svg_header + "\n".join(svg_elements) + svg_footer

#                 # --- 5. Display SVG ---
#                 st.markdown("**Standardized Diagram (all shapes as squares):**")
#                 st.image(svg_content)

#                 # --- 6. Download option ---
#                 st.download_button(
#                     label="Download SVG",
#                     data=svg_content,
#                     file_name="standardized_diagram.svg",
#                     mime="image/svg+xml"
#                 )

#             except Exception as e:
#                 st.error(f"Azure OpenAI error: {e}")



import streamlit as st
import openai
import os
import base64
import json
import math
import re
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")  # GPT-4o deployment

# --- Initialize Azure OpenAI client ---
openai.api_type = "azure"
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = "2024-02-15-preview"
openai.api_key = AZURE_OPENAI_API_KEY

st.title("Diagram Standardizer: Replace All Shapes with Squares (Original Layout)")

st.markdown("""
1. **Upload a PNG diagram**.
2. **GPT-4o Vision extracts shapes, connectors, and each shape's (x, y) position.**
3. **All shapes are replaced with squares at the original locations in a new SVG diagram.**
""")

# --- 1. Upload PNG ---
uploaded_file = st.file_uploader("Upload your PNG diagram", type=["png"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    st.markdown("Click the button below to extract and standardize the diagram.")

    if st.button("Extract & Standardize"):
        # --- 2. Send to GPT-4o Vision for JSON extraction with coordinates ---
        uploaded_file.seek(0)
        image_bytes = uploaded_file.read()
        image_base64 = base64.b64encode(image_bytes).decode()

        # Prompt: ask for JSON with x/y coordinates
        extraction_prompt = (
            "Analyze this diagram. "
            "Return ONLY a JSON object representing the shapes and relationships. "
            "For each shape, include its label (if present), type (rectangle, ellipse, diamond, etc.), "
            "and its center coordinates (x, y) in pixels relative to the image. "
            "Also include relationships (arrows/edges) as a list of nodes and edges. "
            "Format: "
            "{'nodes': [{'id': ..., 'label': ..., 'type': ..., 'x': ..., 'y': ...}, ...], 'edges': [{'from': ..., 'to': ...}, ...]}."
            "Output only the JSON and nothing else."
        )

        with st.spinner("Sending image to Azure OpenAI GPT-4o..."):
            try:
                response = openai.ChatCompletion.create(
                    engine=AZURE_OPENAI_DEPLOYMENT,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant who extracts diagram structure as JSON including x/y coordinates for each shape."},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": extraction_prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                            ],
                        }
                    ],
                    max_tokens=1000,
                )
                answer = response['choices'][0]['message']['content']

                # --- 3. Parse JSON from the response ---
                json_match = re.search(r'({.*})', answer, re.DOTALL)
                if not json_match:
                    st.error("Could not extract a valid JSON block from the model response.")
                    st.write(answer)
                    st.stop()
                json_str = json_match.group(1)
                # Replace single quotes with double quotes for JSON
                json_str = json_str.replace("'", '"')
                try:
                    data = json.loads(json_str)
                except Exception as e:
                    st.error("Failed to parse JSON: " + str(e))
                    st.code(json_str)
                    st.stop()

                st.markdown("**Extracted Diagram JSON:**")
                st.code(json.dumps(data, indent=2), language="json")

                nodes = data.get("nodes", [])
                edges = data.get("edges", [])

                # --- 4. Standardize & Render as SVG (all shapes as squares at extracted (x, y)) ---
                # Layout Parameters
                square_size = 80
                font_size = 14

                # Compute SVG bounds
                all_x = [node['x'] for node in nodes if 'x' in node]
                all_y = [node['y'] for node in nodes if 'y' in node]
                if not all_x or not all_y:
                    st.error("No coordinates found in extracted JSON.")
                    st.stop()
                min_x, max_x = min(all_x), max(all_x)
                min_y, max_y = min(all_y), max(all_y)
                margin = 80
                width = max_x - min_x + margin * 2
                height = max_y - min_y + margin * 2

                # Map node ids to positions
                positions = {}
                for node in nodes:
                    # Center the diagram within the SVG
                    x = node.get("x", 0) - min_x + margin
                    y = node.get("y", 0) - min_y + margin
                    positions[node["id"]] = (x, y)

                # SVG elements
                svg_elements = []

                # Draw edges
                for edge in edges:
                    from_id, to_id = edge["from"], edge["to"]
                    if from_id not in positions or to_id not in positions:
                        continue
                    x1, y1 = positions[from_id]
                    x2, y2 = positions[to_id]
                    # Compute direction
                    dx = x2 - x1
                    dy = y2 - y1
                    length = math.hypot(dx, dy)
                    if length == 0:
                        length = 1
                    ux = dx / length
                    uy = dy / length
                    # Start/end at square edge
                    start_x = x1 + square_size / 2 * ux
                    start_y = y1 + square_size / 2 * uy
                    end_x = x2 - square_size / 2 * ux
                    end_y = y2 - square_size / 2 * uy
                    svg_elements.append(
                        f'<line x1="{start_x}" y1="{start_y}" x2="{end_x}" y2="{end_y}" stroke="black" marker-end="url(#arrow)" />'
                    )

                # Draw nodes as squares
                for node in nodes:
                    node_id = node["id"]
                    x, y = positions[node_id]
                    top_left_x = x - square_size / 2
                    top_left_y = y - square_size / 2
                    svg_elements.append(
                        f'<rect x="{top_left_x}" y="{top_left_y}" width="{square_size}" height="{square_size}" fill="#e0e0e0" stroke="black" />'
                    )
                    # Centered label
                    label = node.get("label", "")
                    svg_elements.append(
                        f'<text x="{x}" y="{y+font_size/2}" font-size="{font_size}" text-anchor="middle" alignment-baseline="middle">{label}</text>'
                    )

                # SVG header/footer
                svg_header = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="10" refY="5" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L10,5 L0,10 L2,5 z" fill="#000"/>
  </marker>
</defs>
'''
                svg_footer = '</svg>'

                svg_content = svg_header + "\n".join(svg_elements) + svg_footer

                # --- 5. Display SVG ---
                st.markdown("**Standardized Diagram (all shapes as squares, original layout):**")
                st.image(svg_content)

                # --- 6. Download option ---
                st.download_button(
                    label="Download SVG",
                    data=svg_content,
                    file_name="standardized_diagram.svg",
                    mime="image/svg+xml"
                )

            except Exception as e:
                st.error(f"Azure OpenAI error: {e}")

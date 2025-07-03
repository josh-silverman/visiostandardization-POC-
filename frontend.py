# # import streamlit as st
# # import tempfile
# # import os

# # # Import all your backend functions (assumes they're in backend.py)
# # import backend

# # st.set_page_config(page_title="Visio AI Processor", layout="wide")

# # st.title("Visio AI Diagram Processor")
# # st.markdown("""
# # This tool downloads a Visio diagram from Azure, processes and transforms it with AI, and uploads the result back to Azure.  
# # You can visually track each processing step below.
# # """)

# # # Progress bar initialization
# # progress = st.progress(0, text="Starting pipeline...")

# # steps = [
# #     "Download VSDX from Azure Blob Storage",
# #     "Unzip VSDX file",
# #     "Convert VSDX to SVG and PNG",
# #     "Process diagram pages with AI",
# #     "Re-zip updated files",
# #     "Upload to Azure Blob Storage"
# # ]

# # status_msgs = ["Not started"] * len(steps)
# # step_percents = [0, 20, 35, 70, 85, 100]

# # for i, step in enumerate(steps):
# #     st.write(f":hourglass_flowing_sand: {step} -- {status_msgs[i]}")

# # run = st.button("Start Processing")

# # if run:
# #     with st.spinner("Running the backend pipeline..."):
# #         try:
# #             with tempfile.TemporaryDirectory() as tempdir:
# #                 # Step 1: Download
# #                 progress.progress(step_percents[0], text=steps[0])
# #                 st.write(f":hourglass: {steps[0]}")
# #                 local_input = os.path.join(tempdir, "input.vsdx")
# #                 backend.download_blob_to_file(
# #                     backend.INPUT_CONTAINER_NAME,
# #                     backend.INPUT_BLOB_NAME,
# #                     local_input
# #                 )
# #                 st.success("Downloaded VSDX from Azure.")

# #                 # Step 2: Unzip
# #                 progress.progress(step_percents[1], text=steps[1])
# #                 st.write(f":hourglass: {steps[1]}")
# #                 unzip_dir = os.path.join(tempdir, "unzipped")
# #                 backend.unzip_vsdx(local_input, unzip_dir)
# #                 st.success("Unzipped VSDX file.")

# #                 # Step 3: Export SVG/PNG
# #                 progress.progress(step_percents[2], text=steps[2])
# #                 st.write(f":hourglass: {steps[2]}")
# #                 export_dir = os.path.join(tempdir, "exports")
# #                 svg_files, png_files = backend.convert_vsdx_to_svg_and_png(local_input, export_dir)
# #                 st.success("Converted VSDX to SVG and PNG.")

# #                 # Step 4: AI Processing
# #                 progress.progress(step_percents[3], text=steps[3])
# #                 st.write(f":hourglass: {steps[3]}")
# #                 pages_dir = os.path.join(unzip_dir, "visio", "pages")
# #                 page_xml_files = sorted([
# #                     f for f in os.listdir(pages_dir)
# #                     if f.startswith('page') and f.endswith('.xml')
# #                 ])
# #                 updated_pages = 0
# #                 for i, page_xml in enumerate(page_xml_files):
# #                     xml_path = os.path.join(pages_dir, page_xml)
# #                     with open(xml_path, "r", encoding="utf-8") as f:
# #                         xml_text = f.read()
# #                     svg_text = ""
# #                     png_path = None
# #                     if i < len(svg_files):
# #                         with open(svg_files[i], "r", encoding="utf-8") as f:
# #                             svg_text = f.read()
# #                     if i < len(png_files):
# #                         png_path = png_files[i]
# #                     if not svg_text or not png_path:
# #                         st.warning(f"SVG or PNG missing for {page_xml}, skipping.")
# #                         continue
# #                     st.info(f"Processing page {page_xml} with AI...")
# #                     try:
# #                         updated_xml = backend.ai_update_xml_with_svg_and_png(xml_text, svg_text, png_path)
# #                     except Exception as e:
# #                         st.error(f"AI call failed for {page_xml}: {e}")
# #                         continue
# #                     with open(xml_path, "w", encoding="utf-8") as f:
# #                         f.write(updated_xml)
# #                     updated_pages += 1
# #                     st.success(f"Updated {page_xml} with AI.")
# #                 st.success(f"Processed {updated_pages} pages with AI.")

# #                 # Step 5: Re-zip
# #                 progress.progress(step_percents[4], text=steps[4])
# #                 st.write(f":hourglass: {steps[4]}")
# #                 output_vsdx = os.path.join(tempdir, "updated.vsdx")
# #                 backend.rezip_to_vsdx(unzip_dir, output_vsdx)
# #                 st.success("Re-zipped updated files.")

# #                 # Step 6: Upload
# #                 progress.progress(step_percents[5], text=steps[5])
# #                 st.write(f":hourglass: {steps[5]}")
# #                 backend.upload_file_to_blob(
# #                     backend.OUTPUT_CONTAINER_NAME,
# #                     backend.OUTPUT_BLOB_NAME,
# #                     output_vsdx
# #                 )
# #                 st.success("Uploaded updated VSDX to Azure.")

# #                 progress.progress(100, text="Pipeline complete!")

# #                 # Display SVG from the first page as the result
# #                 if svg_files:
# #                     st.markdown("---")
# #                     st.header("Result: First Page SVG Preview")
# #                     with open(svg_files[0], "r", encoding="utf-8") as f:
# #                         svg_content = f.read()
# #                     st.image(svg_files[0], caption="First Page SVG", use_column_width=True)
# #                     # Or, to directly show SVG inline:
# #                     st.markdown(
# #                         f'<div style="border:1px solid #eee">{svg_content}</div>',
# #                         unsafe_allow_html=True
# #                     )

# #         except Exception as e:
# #             st.error(f"Pipeline failed: {e}")





# import streamlit as st
# import tempfile
# import os

# # Import your backend functions (assumes they're in backend.py and are implemented)
# import backend

# st.set_page_config(page_title="Visio AI Processor", layout="wide")

# st.title("Visio AI Diagram Processor (Azure Pipeline)")
# st.markdown("""
# This tool downloads a Visio diagram from Azure, processes and transforms it with AI, and uploads the result back to Azure.  
# You can visually track each processing step below.
# """)

# steps = [
#     "Download VSDX from Azure Blob Storage",
#     "Unzip VSDX file",
#     "Convert VSDX to SVG and PNG",
#     "Process diagram pages with AI",
#     "Re-zip updated files",
#     "Upload to Azure Blob Storage"
# ]
# step_percents = [0, 16, 32, 68, 84, 100]

# # Show steps with status
# step_status = ["Not started"] * len(steps)
# step_cols = st.columns(len(steps))
# for i, step in enumerate(steps):
#     step_cols[i].write(f"**{step}**\n\n:hourglass_flowing_sand: {step_status[i]}")

# progress = st.progress(0, text="Ready to start pipeline...")

# run = st.button("Start Processing")

# # if run:
# #     with st.spinner("Running the backend pipeline..."):
# #         try:
# #             with tempfile.TemporaryDirectory() as tempdir:
# #                 # Step 1: Download
# #                 progress.progress(step_percents[0], text=steps[0])
# #                 st.info(f":hourglass: {steps[0]}")
# #                 local_input = os.path.join(tempdir, "input.vsdx")
# #                 backend.download_blob_to_file(
# #                     backend.INPUT_CONTAINER_NAME,
# #                     backend.INPUT_BLOB_NAME,
# #                     local_input
# #                 )
# #                 st.success("Downloaded VSDX from Azure.")

# #                 # Step 2: Unzip
# #                 progress.progress(step_percents[1], text=steps[1])
# #                 st.info(f":hourglass: {steps[1]}")
# #                 unzip_dir = os.path.join(tempdir, "unzipped")
# #                 backend.unzip_vsdx(local_input, unzip_dir)
# #                 st.success("Unzipped VSDX file.")

# #                 # Step 3: Export SVG/PNG
# #                 progress.progress(step_percents[2], text=steps[2])
# #                 st.info(f":hourglass: {steps[2]}")
# #                 export_dir = os.path.join(tempdir, "exports")
# #                 svg_files, png_files = backend.convert_vsdx_to_svg_and_png(local_input, export_dir)
# #                 st.success("Converted VSDX to SVG and PNG.")

# #                 # ---- Show original SVG before AI ----
# #                 st.markdown("---")
# #                 st.subheader("Original Diagram SVG Preview (First Page)")
# #                 if svg_files:
# #                     with open(svg_files[0], "r", encoding="utf-8") as f:
# #                         svg_content = f.read()
# #                     st.markdown(
# #                         f'<div style="width:100%;max-width:420px;height:auto;border:1px solid #eee">'
# #                         f'<div style="width:100%;height:420px;overflow:auto">{svg_content}</div>'
# #                         f'</div>',
# #                         unsafe_allow_html=True
# #                     )
# #                 else:
# #                     st.warning("No SVG files found to preview.")

# #                 # Step 4: AI Processing (show AI-updated SVGs side by side)
# #                 progress.progress(step_percents[3], text=steps[3])
# #                 st.info(f":hourglass: {steps[3]}")
# #                 pages_dir = os.path.join(unzip_dir, "visio", "pages")
# #                 page_xml_files = sorted([
# #                     f for f in os.listdir(pages_dir)
# #                     if f.startswith('page') and f.endswith('.xml')
# #                 ])
# #                 updated_pages = 0
# #                 updated_svgs = []
# #                 original_svgs = []

# #                 st.markdown("---")
# #                 st.subheader("AI Processing: Side-by-Side SVG Comparison")

# #                 for i, page_xml in enumerate(page_xml_files):
# #                     xml_path = os.path.join(pages_dir, page_xml)
# #                     with open(xml_path, "r", encoding="utf-8") as f:
# #                         xml_text = f.read()
# #                     svg_text = ""
# #                     png_path = None
# #                     if i < len(svg_files):
# #                         with open(svg_files[i], "r", encoding="utf-8") as f:
# #                             svg_text = f.read()
# #                     if i < len(png_files):
# #                         png_path = png_files[i]
# #                     if not svg_text or not png_path:
# #                         st.warning(f"SVG or PNG missing for {page_xml}, skipping.")
# #                         continue
# #                     st.info(f"Processing page {page_xml} with AI...")
# #                     try:
# #                         # Now returns both updated XML and updated SVG
# #                         updated_xml, updated_svg = backend.ai_update_xml_and_svg(xml_text, svg_text, png_path)
# #                     except Exception as e:
# #                         st.error(f"AI call failed for {page_xml}: {e}")
# #                         continue
# #                     with open(xml_path, "w", encoding="utf-8") as f:
# #                         f.write(updated_xml)
# #                     updated_pages += 1
# #                     original_svgs.append(svg_text)
# #                     updated_svgs.append(updated_svg)
# #                     # Show side by side
# #                     cols = st.columns(2)
# #                     with cols[0]:
# #                         st.markdown(f"**Original SVG (Page {i+1})**")
# #                         st.markdown(
# #                             f'<div style="width:100%;max-width:420px;height:auto;border:1px solid #eee">'
# #                             f'<div style="width:100%;height:420px;overflow:auto">{svg_text}</div>'
# #                             f'</div>',
# #                             unsafe_allow_html=True
# #                         )
# #                     with cols[1]:
# #                         st.markdown(f"**AI-Updated SVG (Page {i+1})**")
# #                         if updated_svg:
# #                             st.markdown(
# #                                 f'<div style="width:100%;max-width:420px;height:auto;border:1px solid #eee">'
# #                                 f'<div style="width:100%;height:420px;overflow:auto">{updated_svg}</div>'
# #                                 f'</div>',
# #                                 unsafe_allow_html=True
# #                             )
# #                             st.download_button(
# #                                 label=f"Download AI-Updated SVG (Page {i+1})",
# #                                 data=updated_svg,
# #                                 file_name=f"updated_page_{i+1}.svg",
# #                                 mime="image/svg+xml"
# #                             )
# #                         else:
# #                             st.error("No AI-updated SVG was generated.")
# #                 st.success(f"Processed {updated_pages} pages with AI.")

# #                 # Step 5: Re-zip
# #                 progress.progress(step_percents[4], text=steps[4])
# #                 st.info(f":hourglass: {steps[4]}")
# #                 output_vsdx = os.path.join(tempdir, "updated.vsdx")
# #                 backend.rezip_to_vsdx(unzip_dir, output_vsdx)
# #                 st.success("Re-zipped updated files.")

# #                 # Step 6: Upload
# #                 progress.progress(step_percents[5], text=steps[5])
# #                 st.info(f":hourglass: {steps[5]}")
# #                 backend.upload_file_to_blob(
# #                     backend.OUTPUT_CONTAINER_NAME,
# #                     backend.OUTPUT_BLOB_NAME,
# #                     output_vsdx
# #                 )
# #                 st.success("Uploaded updated VSDX to Azure.")

# #                 progress.progress(100, text="Pipeline complete!")

# #                 # Optional: Download AI-updated VSDX
# #                 with open(output_vsdx, "rb") as f:
# #                     st.download_button(
# #                         label="Download AI-Updated VSDX",
# #                         data=f,
# #                         file_name="updated_diagram.vsdx",
# #                         mime="application/vnd.ms-visio.drawing"
# #                     )

# #         except Exception as e:
# #             st.error(f"Pipeline failed: {e}")

# if run:
#     with st.spinner("Running the backend pipeline..."):
#         try:
#             with tempfile.TemporaryDirectory() as tempdir:
#                 # Step 1: Download
#                 progress.progress(step_percents[0], text=steps[0])
#                 st.info(f":hourglass: {steps[0]}")
#                 local_input = os.path.join(tempdir, "input.vsdx")
#                 backend.download_blob_to_file(
#                     backend.INPUT_CONTAINER_NAME,
#                     backend.INPUT_BLOB_NAME,
#                     local_input
#                 )
#                 st.success("Downloaded VSDX from Azure.")

#                 # Step 2: Unzip
#                 progress.progress(step_percents[1], text=steps[1])
#                 st.info(f":hourglass: {steps[1]}")
#                 unzip_dir = os.path.join(tempdir, "unzipped")
#                 backend.unzip_vsdx(local_input, unzip_dir)
#                 st.success("Unzipped VSDX file.")

#                 # Step 3: Export SVG/PNG
#                 progress.progress(step_percents[2], text=steps[2])
#                 st.info(f":hourglass: {steps[2]}")
#                 export_dir = os.path.join(tempdir, "exports")
#                 svg_files, png_files = backend.convert_vsdx_to_svg_and_png(local_input, export_dir)
#                 st.success("Converted VSDX to SVG and PNG.")

#                 # --- PNG existence and usage check ---
#                 if not png_files:
#                     st.error("No PNG file was exported! Cannot proceed.")
#                     st.stop()
#                 png_path = png_files[0]
#                 if not os.path.isfile(png_path):
#                     st.error(f"PNG file not found at {png_path}. Cannot proceed.")
#                     st.stop()
#                 png_size = os.path.getsize(png_path)
#                 if png_size < 100:
#                     st.warning(f"PNG file {png_path} is very small ({png_size} bytes) -- may be invalid.")
#                 st.info(f"Verified PNG to be used: {png_path} ({png_size} bytes)")

#                 if not svg_files:
#                     st.error("No SVG file was exported! Cannot proceed.")
#                     st.stop()
#                 svg_path = svg_files[0]
#                 with open(svg_path, "r", encoding="utf-8") as f:
#                     svg_text_all = f.read()

#                 # ---- Show original SVG before AI ----
#                 st.markdown("---")
#                 st.subheader("Original Diagram SVG Preview (First Page)")
#                 st.markdown(
#                     f'<div style="width:100%;max-width:420px;height:auto;border:1px solid #eee">'
#                     f'<div style="width:100%;height:420px;overflow:auto">{svg_text_all}</div>'
#                     f'</div>',
#                     unsafe_allow_html=True
#                 )

#                 # Step 4: AI Processing (side-by-side SVGs)
#                 progress.progress(step_percents[3], text=steps[3])
#                 st.info(f":hourglass: {steps[3]}")
#                 pages_dir = os.path.join(unzip_dir, "visio", "pages")
#                 page_xml_files = sorted([
#                     f for f in os.listdir(pages_dir)
#                     if f.startswith('page') and f.endswith('.xml')
#                 ])
#                 updated_pages = 0
#                 updated_svgs = []
#                 original_svgs = []

#                 st.markdown("---")
#                 st.subheader("AI Processing: Side-by-Side SVG Comparison")

#                 for i, page_xml in enumerate(page_xml_files):
#                     xml_path = os.path.join(pages_dir, page_xml)
#                     with open(xml_path, "r", encoding="utf-8") as f:
#                         xml_text = f.read()
#                     # Always use the same SVG/PNG for every page
#                     svg_text = svg_text_all
#                     png_path_to_use = png_path
#                     st.info(f"Processing page {page_xml} with AI. Using PNG: {png_path_to_use}")
#                     try:
#                         # Now returns both updated XML and updated SVG
#                         updated_xml, updated_svg = backend.ai_update_xml_and_svg(
#                             xml_text, svg_text, png_path_to_use
#                         )
#                     except Exception as e:
#                         st.error(f"AI call failed for {page_xml}: {e}")
#                         continue
#                     with open(xml_path, "w", encoding="utf-8") as f:
#                         f.write(updated_xml)
#                     updated_pages += 1
#                     original_svgs.append(svg_text)
#                     updated_svgs.append(updated_svg)
#                     # Show side by side
#                     cols = st.columns(2)
#                     with cols[0]:
#                         st.markdown(f"**Original SVG (Page {i+1})**")
#                         st.markdown(
#                             f'<div style="width:100%;max-width:420px;height:auto;border:1px solid #eee">'
#                             f'<div style="width:100%;height:420px;overflow:auto">{svg_text}</div>'
#                             f'</div>',
#                             unsafe_allow_html=True
#                         )
#                     with cols[1]:
#                         st.markdown(f"**AI-Updated SVG (Page {i+1})**")
#                         if updated_svg:
#                             st.markdown(
#                                 f'<div style="width:100%;max-width:420px;height:auto;border:1px solid #eee">'
#                                 f'<div style="width:100%;height:420px;overflow:auto">{updated_svg}</div>'
#                                 f'</div>',
#                                 unsafe_allow_html=True
#                             )
#                             st.download_button(
#                                 label=f"Download AI-Updated SVG (Page {i+1})",
#                                 data=updated_svg,
#                                 file_name=f"updated_page_{i+1}.svg",
#                                 mime="image/svg+xml"
#                             )
#                         else:
#                             st.error("No AI-updated SVG was generated.")
#                 st.success(f"Processed {updated_pages} pages with AI.")

#                 # Step 5: Re-zip
#                 progress.progress(step_percents[4], text=steps[4])
#                 st.info(f":hourglass: {steps[4]}")
#                 output_vsdx = os.path.join(tempdir, "updated.vsdx")
#                 backend.rezip_to_vsdx(unzip_dir, output_vsdx)
#                 st.success("Re-zipped updated files.")

#                 # Step 6: Upload
#                 progress.progress(step_percents[5], text=steps[5])
#                 st.info(f":hourglass: {steps[5]}")
#                 backend.upload_file_to_blob(
#                     backend.OUTPUT_CONTAINER_NAME,
#                     backend.OUTPUT_BLOB_NAME,
#                     output_vsdx
#                 )
#                 st.success("Uploaded updated VSDX to Azure.")

#                 progress.progress(100, text="Pipeline complete!")

#                 # Optional: Download AI-updated VSDX
#                 with open(output_vsdx, "rb") as f:
#                     st.download_button(
#                         label="Download AI-Updated VSDX",
#                         data=f,
#                         file_name="updated_diagram.vsdx",
#                         mime="application/vnd.ms-visio.drawing"
#                     )

#         except Exception as e:
#             st.error(f"Pipeline failed: {e}")




import streamlit as st
import tempfile
import os

# Import your backend functions (assumes they're in backend.py and are implemented)
import backend

st.set_page_config(page_title="Visio AI Processor", layout="wide")

st.title("Visio AI Diagram Processor (Azure Pipeline)")
st.markdown("""
This tool downloads a Visio diagram from Azure, processes and transforms it with AI, and uploads the result back to Azure.  
You can visually track each processing step below.
""")

steps = [
    "Download VSDX from Azure Blob Storage",
    "Unzip VSDX file",
    "Convert VSDX to SVG and PNG",
    "Process diagram pages with AI",
    "Re-zip updated files",
    "Upload to Azure Blob Storage"
]
step_percents = [0, 16, 32, 68, 84, 100]

# Show steps with status
step_status = ["Not started"] * len(steps)
step_cols = st.columns(len(steps))
for i, step in enumerate(steps):
    step_cols[i].write(f"**{step}**\n\n:hourglass_flowing_sand: {step_status[i]}")

progress = st.progress(0, text="Ready to start pipeline...")

run = st.button("Start Processing")

if run:
    with st.spinner("Running the backend pipeline..."):
        try:
            with tempfile.TemporaryDirectory() as tempdir:
                # Step 1: Download
                progress.progress(step_percents[0], text=steps[0])
                st.info(f":hourglass: {steps[0]}")
                local_input = os.path.join(tempdir, "input.vsdx")
                backend.download_blob_to_file(
                    backend.INPUT_CONTAINER_NAME,
                    backend.INPUT_BLOB_NAME,
                    local_input
                )
                st.success("Downloaded VSDX from Azure.")

                # Step 2: Unzip
                progress.progress(step_percents[1], text=steps[1])
                st.info(f":hourglass: {steps[1]}")
                unzip_dir = os.path.join(tempdir, "unzipped")
                backend.unzip_vsdx(local_input, unzip_dir)
                st.success("Unzipped VSDX file.")

                # Step 3: Export SVG/PNG
                progress.progress(step_percents[2], text=steps[2])
                st.info(f":hourglass: {steps[2]}")
                export_dir = os.path.join(tempdir, "exports")
                svg_files, png_files = backend.convert_vsdx_to_svg_and_png(local_input, export_dir)
                st.success("Converted VSDX to SVG and PNG.")

                # --- PNG existence and usage check ---
                if not png_files:
                    st.error("No PNG file was exported! Cannot proceed.")
                    st.stop()
                png_path = png_files[0]
                if not os.path.isfile(png_path):
                    st.error(f"PNG file not found at {png_path}. Cannot proceed.")
                    st.stop()
                png_size = os.path.getsize(png_path)
                if png_size < 100:
                    st.warning(f"PNG file {png_path} is very small ({png_size} bytes) -- may be invalid.")
                st.info(f"Verified PNG to be used: {png_path} ({png_size} bytes)")

                if not svg_files:
                    st.error("No SVG file was exported! Cannot proceed.")
                    st.stop()
                svg_path = svg_files[0]
                with open(svg_path, "r", encoding="utf-8") as f:
                    svg_text_all = f.read()

                # ---- Show original SVG before AI ----
                st.markdown("---")
                st.subheader("Original Diagram SVG Preview (First Page)")
                st.markdown(
                    f'<div style="width:100%;max-width:420px;height:auto;border:1px solid #eee">'
                    f'<div style="width:100%;height:420px;overflow:auto">{svg_text_all}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # Step 4: AI Processing (ONLY first page)
                progress.progress(step_percents[3], text=steps[3])
                st.info(f":hourglass: {steps[3]}")
                pages_dir = os.path.join(unzip_dir, "visio", "pages")
                page_xml_files = sorted([
                    f for f in os.listdir(pages_dir)
                    if f.startswith('page') and f.endswith('.xml')
                ])

                st.markdown("---")
                st.subheader("AI Processing: Side-by-Side SVG Comparison (First Page Only)")

                if page_xml_files:
                    page_xml = page_xml_files[0]
                    xml_path = os.path.join(pages_dir, page_xml)
                    with open(xml_path, "r", encoding="utf-8") as f:
                        xml_text = f.read()
                    svg_text = svg_text_all
                    png_path_to_use = png_path
                    st.info(f"Processing ONLY page {page_xml} with AI. Using PNG: {png_path_to_use}")
                    try:
                        updated_xml, updated_svg, description = backend.ai_update_xml_and_svg(
                            xml_text, svg_text, png_path_to_use
                        )
                    except Exception as e:
                        st.error(f"AI call failed for {page_xml}: {e}")
                    else:
                        # Write back the updated XML for this page
                        with open(xml_path, "w", encoding="utf-8") as f:
                            f.write(updated_xml)
                        # Show side by side
                        cols = st.columns(2)
                        with cols[0]:
                            st.markdown(f"**Original SVG (Page 1)**")
                            st.markdown(
                                f'<div style="width:100%;max-width:420px;height:auto;border:1px solid #eee">'
                                f'<div style="width:100%;height:420px;overflow:auto">{svg_text}</div>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                        with cols[1]:
                            st.markdown(f"**AI-Updated SVG (Page 1)**")
                            if updated_svg:
                                st.markdown(
                                    f'<div style="width:100%;max-width:420px;height:auto;border:1px solid #eee">'
                                    f'<div style="width:100%;height:420px;overflow:auto">{updated_svg}</div>'
                                    f'</div>',
                                    unsafe_allow_html=True
                                )
                                st.download_button(
                                    label="Download AI-Updated SVG (Page 1)",
                                    data=updated_svg,
                                    file_name="updated_page_1.svg",
                                    mime="image/svg+xml"
                                )
                            else:
                                st.error("No AI-updated SVG was generated.")
                        st.success(f"Processed ONLY the first page with AI.")

                    if description:
                                st.markdown("---")
                                st.subheader("Diagram Description (AI-generated)")
                                st.info(description)
                else:
                    st.warning("No Visio pages found to process.")

                # Step 5: Re-zip
                progress.progress(step_percents[4], text=steps[4])
                st.info(f":hourglass: {steps[4]}")
                output_vsdx = os.path.join(tempdir, "updated.vsdx")
                backend.rezip_to_vsdx(unzip_dir, output_vsdx)
                st.success("Re-zipped updated files.")

                # Step 6: Upload
                progress.progress(step_percents[5], text=steps[5])
                st.info(f":hourglass: {steps[5]}")
                backend.upload_file_to_blob(
                    backend.OUTPUT_CONTAINER_NAME,
                    backend.OUTPUT_BLOB_NAME,
                    output_vsdx
                )
                st.success("Uploaded updated VSDX to Azure.")

                progress.progress(100, text="Pipeline complete!")

                # Optional: Download AI-updated VSDX
                with open(output_vsdx, "rb") as f:
                    st.download_button(
                        label="Download AI-Updated VSDX",
                        data=f,
                        file_name="updated_diagram.vsdx",
                        mime="application/vnd.ms-visio.drawing"
                    )

        except Exception as e:
            st.error(f"Pipeline failed: {e}")

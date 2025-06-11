# visio_convert.py
import os
import zipfile

try:
    import comtypes.client
except ImportError:
    comtypes = None

def visio_to_pngs(vsdx_path, output_dir):
    if comtypes is None:
        raise RuntimeError("comtypes is not available. Must run on Windows with Visio installed.")
    visio = comtypes.client.CreateObject("Visio.Application")
    visio.Visible = False
    doc = visio.Documents.Open(vsdx_path)
    page_paths = []
    for i, page in enumerate(doc.Pages):
        output_path = os.path.join(output_dir, f"page_{i+1}.png")
        page.Export(output_path)
        page_paths.append(output_path)
    doc.Close()
    visio.Quit()
    return page_paths

def extract_visio_xml(vsdx_path, extract_dir):
    with zipfile.ZipFile(vsdx_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    page_dir = os.path.join(extract_dir, "visio", "pages")
    page_xmls = []
    if os.path.exists(page_dir):
        for file in os.listdir(page_dir):
            if file.endswith(".xml"):
                page_xmls.append(os.path.join(page_dir, file))
    return page_xmls

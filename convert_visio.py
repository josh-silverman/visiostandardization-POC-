import os
import comtypes.client
import zipfile

def visio_to_pngs(visio_file, output_dir):
    """Converts each page of .vsdx to a PNG in output_dir."""
    visio = comtypes.client.CreateObject("Visio.Application")
    visio.Visible = False
    doc = visio.Documents.Open(visio_file)
    png_paths = []
    for i, page in enumerate(doc.Pages):
        output_path = os.path.join(output_dir, f"page_{i+1}.png")
        page.Export(output_path)
        png_paths.append(output_path)
    doc.Close()
    visio.Quit()
    return png_paths

def extract_vsdx_xml(vsdx_path, extract_dir):
    """Extracts all XML files from a .vsdx (ZIP) to extract_dir."""
    with zipfile.ZipFile(vsdx_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    # Returns the path to Pages XML directory
    return os.path.join(extract_dir, "visio", "pages")

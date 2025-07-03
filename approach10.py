import zipfile
import os

def extract_vsdx_to_folder(vsdx_path, output_folder):
    """
    Extracts a VSDX file (which is a ZIP archive) to the output_folder,
    preserving the internal folder structure.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    with zipfile.ZipFile(vsdx_path, 'r') as zip_ref:
        zip_ref.extractall(output_folder)
    print(f"Extracted {vsdx_path} to {output_folder}")

if __name__ == "__main__":
    # Example usage:
    vsdx_file = r"C:\Users\333798\OneDrive - NTT DATA North America\Desktop\Visio POC\SLM-DMVOSCI- Initial.vsdx"     # <-- Change this to your .vsdx file
    output_dir = r"C:\Users\333798\OneDrive - NTT DATA North America\Desktop\Visio POC\Zipped files"   # <-- Change this to your desired output folder
    extract_vsdx_to_folder(vsdx_file, output_dir)
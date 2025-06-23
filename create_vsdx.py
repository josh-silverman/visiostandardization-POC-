import os
import zipfile

# Set up your paths
output_folder = 'output_xml'            # The folder containing your extracted/editable Visio files
output_vsdx = 'enhanced_diagram.vsdx'   # Name of the final vsdx file

# Create the zip file
with zipfile.ZipFile(output_vsdx, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(output_folder):
        for file in files:
            file_path = os.path.join(root, file)
            # arcname: path inside the zip file (relative to output_xml, not including it)
            arcname = os.path.relpath(file_path, output_folder)
            zipf.write(file_path, arcname)

print(f"Created {output_vsdx} successfully!")

# import os
# import zipfile

# def zipdir(path, ziph):
#     # Zip the directory, keeping the folder structure
#     for root, dirs, files in os.walk(path):
#         for file in files:
#             full_path = os.path.join(root, file)
#             arcname = os.path.relpath(full_path, path)
#             ziph.write(full_path, arcname)

# output_folder = 'output_xml'
# output_vsdx = 'output.vsdx'

# with zipfile.ZipFile(output_vsdx, 'w', zipfile.ZIP_DEFLATED) as zipf:
#     zipdir(output_folder, zipf)

# print(f"Created {output_vsdx}")



import os
import zipfile

def zipdir(path, ziph):
    # Zip the directory, keeping the folder structure
    for root, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, path)
            ziph.write(full_path, arcname)

def run_create_vsdx():
    output_folder = 'output_xml'
    output_vsdx = 'output.vsdx'
    with zipfile.ZipFile(output_vsdx, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(output_folder, zipf)
    print(f"Created {output_vsdx}")

if __name__ == "__main__":
    run_create_vsdx()

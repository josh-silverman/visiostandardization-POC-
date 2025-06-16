import os
import tempfile
import json

from setup import load_config
from upload_to_blob import (
    get_blob_service_client,
    list_blobs,
    download_blob_to_file,
    upload_file_to_blob
)
from analyze_diagram import analyze_image_with_gpt4o
from standardize import standardize_diagram_data

def main():
    # Load environment/config settings
    config = load_config()
    blob_service_client = get_blob_service_client(config["AZURE_STORAGE_CONNECTION_STRING"])
    input_container = config["BLOB_CONTAINER"]
    output_container = config["STANDARDIZED_CONTAINER"]

    # List all PNG files in the input container
    print(f"Listing PNG blobs in container: {input_container}")
    png_blobs = list_blobs(blob_service_client, input_container, suffix=".png")
    print("Blobs found in container:")
    for blob in png_blobs:
        print(f"- '{blob}'")

    if not png_blobs:
        print("No PNG files found. Please upload PNGs to your input container.")
        return

    print(f"\nFound {len(png_blobs)} PNG files to process.\n")

    for png_blob in png_blobs:
        print(f"Processing: '{png_blob}'")
        with tempfile.TemporaryDirectory() as tmpdir:
            local_png = os.path.join(tmpdir, os.path.basename(png_blob))

            try:
                # Download PNG
                print(f"Downloading '{png_blob}' to '{local_png}'...")
                download_blob_to_file(blob_service_client, input_container, png_blob, local_png)
                print("Download complete.")

                # Analyze the PNG with GPT-4o
                print("Analyzing image with GPT-4o...")
                diagram_data = analyze_image_with_gpt4o(local_png, config)
                print("Analysis complete.")

                # Standardize the result
                print("Standardizing extracted data...")
                standardized_data = standardize_diagram_data(diagram_data)
                print("Standardization complete.")

                # Save standardized JSON locally
                json_name = os.path.splitext(os.path.basename(png_blob))[0] + "_standardized.json"
                json_path = os.path.join(tmpdir, json_name)
                with open(json_path, "w") as f:
                    json.dump(standardized_data, f, indent=2)

                # Upload standardized JSON
                print(f"Uploading standardized JSON as '{json_name}' to container '{output_container}'...")
                upload_file_to_blob(blob_service_client, output_container, json_path, blob_name=json_name)
                print("Upload complete.\n")

            except Exception as e:
                print(f"Error processing '{png_blob}': {e}\n")

if __name__ == "__main__":
    main()

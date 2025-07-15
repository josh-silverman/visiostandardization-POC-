from extract_xml import run_extract_xml
from parse_visio import run_parse_visio
from ai_standardize import run_ai_standardize
from json_to_xml import run_json_to_xml
from create_vsdx import run_create_vsdx

def main():
    print("\n--- Step 1: Extracting VSDX and uploading XML to Azure... ---")
    run_extract_xml()

    print("\n--- Step 2: Parsing Visio XML to JSON... ---")
    run_parse_visio()

    print("\n--- Step 3: AI Standardizing the JSON... ---")
    run_ai_standardize()

    print("\n--- Step 4: Writing standardized JSON back to XML... ---")
    run_json_to_xml()

    print("\n--- Step 5: Creating new VSDX from updated XML... ---")
    run_create_vsdx()

    print("\nPipeline complete!")

if __name__ == "__main__":
    main()

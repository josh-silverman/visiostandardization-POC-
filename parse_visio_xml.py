import os
import xmltodict
import json

def get_all_xml_files(root_dir):
    xml_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith('.xml'):
                xml_files.append(os.path.join(dirpath, filename))
    return xml_files

def parse_xml_file(xml_path):
    with open(xml_path, 'r', encoding='utf-8') as f:
        return xmltodict.parse(f.read(), process_namespaces=True)

def save_json(data, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    visio_root = os.path.join("output_xml", "visio")
    output_dir = "parsed_json"
    os.makedirs(output_dir, exist_ok=True)

    # Focus on pages and masters only
    dirs_to_parse = [
        os.path.join(visio_root, "pages"),
        os.path.join(visio_root, "masters"),
    ]

    for dir_to_parse in dirs_to_parse:
        if not os.path.exists(dir_to_parse):
            continue
        for xml_path in get_all_xml_files(dir_to_parse):
            rel_path = os.path.relpath(xml_path, visio_root)
            json_path = os.path.join(output_dir, rel_path[:-4] + ".json")
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            print(f"Parsing {xml_path} ...")
            data = parse_xml_file(xml_path)
            save_json(data, json_path)
            print(f"Saved to {json_path}")

if __name__ == "__main__":
    main()

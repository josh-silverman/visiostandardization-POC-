import os
import json
import xmltodict
import re

INPUT_JSON = "roundtrip_json/pages/page1.json"
OUTPUT_XML = "output_xml/visio/pages/page1.xml"

def strip_ns(obj):
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            tag = re.sub(r'^(.*[:}])', '', k)
            new_obj[tag] = strip_ns(v)
        return new_obj
    elif isinstance(obj, list):
        return [strip_ns(x) for x in obj]
    else:
        return obj

def main():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    data_no_ns = strip_ns(data)
    root_key = list(data_no_ns.keys())[0]
    print(f"Root key is: {root_key}")

    data_no_ns[root_key]["@xmlns"] = "http://schemas.microsoft.com/office/visio/2012/main"
    data_no_ns[root_key]["@xmlns:r"] = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    # Optionally: data_no_ns[root_key]["@xml:space"] = "preserve"  # Only if you really need it

    xml_str = xmltodict.unparse(
        data_no_ns,
        pretty=True,
        full_document=True,
        encoding="utf-8"
    )

    os.makedirs(os.path.dirname(OUTPUT_XML), exist_ok=True)
    with open(OUTPUT_XML, "w", encoding="utf-8") as f:
        f.write(xml_str)

    print(f"Wrote updated XML to {OUTPUT_XML}")

if __name__ == "__main__":
    main()

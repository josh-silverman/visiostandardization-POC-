1. install venv
2. source ./venv/bin/activate
3. python extract_xml.py
4. python parse_visio.py
5. python ai_standardize.py
6. python footer.py (has to be before json_to_xml.py every time)
7. python json_to_xml.py
8. python footer.py (again)
9. python create_vsdx.py
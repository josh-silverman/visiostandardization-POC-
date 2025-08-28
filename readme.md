1. install venv
2. source ./venv/bin/activate
3. python extract_xml.py (vsdx --> zip (xml files))
4. python parse_visio.py (xml --> json)
5. python ai_standardize.py (json --> standardized json)
6. python footer.py (has to be before json_to_xml.py every time) 
7. python json_to_xml.py (standardized json --> standardized xml)
9. python create_vsdx.py (standardized zip --> standardized vsdx)
10. download output.vsdx

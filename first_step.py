from lxml import etree

# --- Standardization constants ---
STANDARD_FONT = 'Calibri'
STANDARD_FONT_F = 'THEMEVAL("LatinFont",4)'
STANDARD_SIZE = '0.075'  # Your preferred size
STANDARD_SIZE_UNIT = 'PT'
STANDARD_COLOR = '#000000'
STANDARD_STYLE = '17'

STANDARD_LINE_WEIGHT = '0.01388888888888889'
STANDARD_LINE_WEIGHT_UNIT = 'PT'
STANDARD_LINE_WEIGHT_F = 'THEMEVAL("LineWeight",0.72PT)'

# FILL COLORS
STANDARD_DEVICE_FILL = '#23b8e9'
STANDARD_GRADIENT_TOP = '#e7e4cd'
STANDARD_CONNECTOR_FILL = '#ADD8E6'

# --- Property Section Standardization ---
STANDARD_PROPERTIES = [
    ('DeviceName', ''),
    ('Location', ''),
    ('Notes', ''),
    ('VLAN', ''),
    # Add/remove property tuples as needed
]

def apply_device_gradient_format(shape, NS, fill_color=STANDARD_DEVICE_FILL):
    fillfore = shape.find('v:Cell[@N="FillForegnd"]', namespaces=NS)
    if fillfore is None:
        fillfore = etree.Element('{%s}Cell' % NS['v'], N="FillForegnd")
        shape.append(fillfore)
    fillfore.set('V', fill_color)
    fillfore.set('F', 'THEMEVAL("FillColor",1)')
    fillbkg = shape.find('v:Cell[@N="FillBkgnd"]', namespaces=NS)
    if fillbkg is None:
        fillbkg = etree.Element('{%s}Cell' % NS['v'], N="FillBkgnd")
        shape.append(fillbkg)
    fillbkg.set('V', 'Themed')
    fillbkg.set('F', 'THEMEVAL()')
    for grad_section in shape.findall('v:Section[@N="FillGradient"]', namespaces=NS):
        shape.remove(grad_section)
    grad_section = etree.Element('{%s}Section' % NS['v'], N="FillGradient")
    row0 = etree.Element('{%s}Row' % NS['v'], IX="0")
    cell0a = etree.Element('{%s}Cell' % NS['v'], N="GradientStopColor", V=STANDARD_GRADIENT_TOP)
    cell0b = etree.Element('{%s}Cell' % NS['v'], N="GradientStopColorTrans", V="0")
    row0.extend([cell0a, cell0b])
    grad_section.append(row0)
    row1 = etree.Element('{%s}Row' % NS['v'], IX="1")
    cell1a = etree.Element('{%s}Cell' % NS['v'], N="GradientStopColor", V=fill_color, F="Inh")
    cell1b = etree.Element('{%s}Cell' % NS['v'], N="GradientStopColorTrans", V="0", F="Inh")
    row1.extend([cell1a, cell1b])
    grad_section.append(row1)
    shape.append(grad_section)

def apply_connector_fill(shape, NS):
    fillfore = shape.find('v:Cell[@N="FillForegnd"]', namespaces=NS)
    if fillfore is None:
        fillfore = etree.Element('{%s}Cell' % NS['v'], N="FillForegnd")
        shape.append(fillfore)
    fillfore.set('V', STANDARD_CONNECTOR_FILL)
    fillfore.set('F', 'THEMEVAL("FillColor",1)')
    for grad_section in shape.findall('v:Section[@N="FillGradient"]', namespaces=NS):
        shape.remove(grad_section)

def ensure_character_section(shape, NS):
    char_section = shape.find('.//v:Section[@N="Character"]', namespaces=NS)
    if char_section is None:
        char_section = etree.Element('{%s}Section' % NS['v'], N="Character")
        shape.append(char_section)
    row = char_section.find('.//v:Row[@IX="0"]', namespaces=NS)
    if row is None:
        row = etree.Element('{%s}Row' % NS['v'], IX="0")
        char_section.append(row)
    return row

def standardize_font_on_shape(shape, NS):
    row = ensure_character_section(shape, NS)
    font_cell = row.find('v:Cell[@N="Font"]', namespaces=NS)
    if font_cell is None:
        font_cell = etree.Element('{%s}Cell' % NS['v'], N="Font")
        row.append(font_cell)
    font_cell.set('V', STANDARD_FONT)
    font_cell.set('F', STANDARD_FONT_F)
    color_cell = row.find('v:Cell[@N="Color"]', namespaces=NS)
    if color_cell is None:
        color_cell = etree.Element('{%s}Cell' % NS['v'], N="Color")
        row.append(color_cell)
    color_cell.set('V', STANDARD_COLOR)
    size_cell = row.find('v:Cell[@N="Size"]', namespaces=NS)
    if size_cell is None:
        size_cell = etree.Element('{%s}Cell' % NS['v'], N="Size", U=STANDARD_SIZE_UNIT)
        row.append(size_cell)
    size_cell.set('V', STANDARD_SIZE)
    size_cell.set('U', STANDARD_SIZE_UNIT)
    style_cell = row.find('v:Cell[@N="Style"]', namespaces=NS)
    if style_cell is None:
        style_cell = etree.Element('{%s}Cell' % NS['v'], N="Style")
        row.append(style_cell)
    style_cell.set('V', STANDARD_STYLE)

def standardize_connector(shape, NS):
    lw_cell = shape.find('v:Cell[@N="LineWeight"]', namespaces=NS)
    if lw_cell is None:
        lw_cell = etree.Element('{%s}Cell' % NS['v'], N="LineWeight", U=STANDARD_LINE_WEIGHT_UNIT)
        shape.append(lw_cell)
    lw_cell.set('V', STANDARD_LINE_WEIGHT)
    lw_cell.set('U', STANDARD_LINE_WEIGHT_UNIT)
    lw_cell.set('F', STANDARD_LINE_WEIGHT_F)
    ff_cell = shape.find('v:Cell[@N="FillForegnd"]', namespaces=NS)
    if ff_cell is None:
        ff_cell = etree.Element('{%s}Cell' % NS['v'], N="FillForegnd")
        shape.append(ff_cell)
    ff_cell.set('V', STANDARD_CONNECTOR_FILL)
    ff_cell.set('F', 'THEMEVAL("FillColor",1)')
    for lc_cell in shape.findall('v:Cell[@N="LineColor"]', namespaces=NS):
        shape.remove(lc_cell)
    for grad_section in shape.findall('v:Section[@N="FillGradient"]', namespaces=NS):
        shape.remove(grad_section)

def ensure_standard_properties(shape, NS):
    prop_section = shape.find('v:Section[@N="Prop"]', namespaces=NS)
    if prop_section is None:
        prop_section = etree.Element('{%s}Section' % NS['v'], N="Prop")
        shape.append(prop_section)
    # Build set of existing property names
    existing_props = set()
    for row in prop_section.findall('v:Row', namespaces=NS):
        prop_name = row.get('N')
        if prop_name:
            existing_props.add(prop_name)
    # Ensure every property exists
    for prop_name, default_value in STANDARD_PROPERTIES:
        if prop_name not in existing_props:
            row = etree.Element('{%s}Row' % NS['v'], N=prop_name, IX=str(len(existing_props)))
            value_cell = etree.Element('{%s}Cell' % NS['v'], N="Value")
            value_cell.set('V', default_value)
            row.append(value_cell)
            prop_section.append(row)
            existing_props.add(prop_name)

def is_text_shape(shape, NS):
    # True if shape has a Text element and no nested shapes
    has_text = shape.find('v:Text', namespaces=NS) is not None
    has_children = shape.find('v:Shapes', namespaces=NS) is not None
    return has_text and not has_children

def standardize_text_block(shape, NS):
    # Set paragraph alignment to center
    para_section = shape.find('v:Section[@N="Paragraph"]', namespaces=NS)
    if para_section is None:
        para_section = etree.Element('{%s}Section' % NS['v'], N="Paragraph")
        shape.append(para_section)
    row = para_section.find('.//v:Row[@IX="0"]', namespaces=NS)
    if row is None:
        row = etree.Element('{%s}Row' % NS['v'], IX="0")
        para_section.append(row)
    align_cell = row.find('v:Cell[@N="Align"]', namespaces=NS)
    if align_cell is None:
        align_cell = etree.Element('{%s}Cell' % NS['v'], N="Align")
        row.append(align_cell)
    align_cell.set('V', '1')  # 0=left, 1=center, 2=right

    # Remove fills and gradients for clean text block
    for cell_name in ["FillForegnd", "FillBkgnd"]:
        cell = shape.find(f'v:Cell[@N="{cell_name}"]', namespaces=NS)
        if cell is not None:
            shape.remove(cell)
    for grad_section in shape.findall('v:Section[@N="FillGradient"]', namespaces=NS):
        shape.remove(grad_section)

def standardize_text_connectors_and_fill(xml_path):
    NS = {'v': 'http://schemas.microsoft.com/office/visio/2012/main'}
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(xml_path, parser)
    root = tree.getroot()

    def process_shape(shape):
        standardize_font_on_shape(shape, NS)
        nameu = shape.get('NameU', '').lower() if shape.get('NameU') else ''
        if 'connector' in nameu:
            standardize_connector(shape, NS)
            apply_connector_fill(shape, NS)
        elif is_text_shape(shape, NS):
            standardize_text_block(shape, NS)
        else:
            apply_device_gradient_format(shape, NS, fill_color=STANDARD_DEVICE_FILL)
        ensure_standard_properties(shape, NS)
        nested_shapes = shape.find('v:Shapes', namespaces=NS)
        if nested_shapes is not None:
            for child_shape in nested_shapes.findall('v:Shape', namespaces=NS):
                process_shape(child_shape)

    shapes = root.find('v:Shapes', namespaces=NS)
    if shapes is not None:
        for shape in shapes.findall('v:Shape', namespaces=NS):
            process_shape(shape)

    # Overwrite the file
    tree.write(xml_path, encoding='utf-8', xml_declaration=True, pretty_print=True)
    print(f"Standardized XML saved to: {xml_path}")

# Example usage
standardize_text_connectors_and_fill('output_xml/visio/pages/page1.xml')

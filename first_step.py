from lxml import etree

# --- Standardization constants ---
STANDARD_FONT = 'Calibri'
STANDARD_FONT_F = 'THEMEVAL("LatinFont",4)'
STANDARD_SIZE = '0.0500000'
STANDARD_SIZE_UNIT = 'PT'
STANDARD_COLOR = '#000000'
STANDARD_STYLE = '17'

STANDARD_LINE_WEIGHT = '0.01388888888888889'
STANDARD_LINE_WEIGHT_UNIT = 'PT'
STANDARD_LINE_WEIGHT_F = 'THEMEVAL("LineWeight",0.72PT)'

def apply_firewall_gradient_format(shape, NS):
    # --- FillForegnd ---
    fillfore = shape.find('v:Cell[@N="FillForegnd"]', namespaces=NS)
    if fillfore is None:
        fillfore = etree.Element('{%s}Cell' % NS['v'], N="FillForegnd")
        shape.append(fillfore)
    fillfore.set('V', '#23b8e9')
    fillfore.set('F', 'THEMEVAL("FillColor",1)')

    # --- FillBkgnd ---
    fillbkg = shape.find('v:Cell[@N="FillBkgnd"]', namespaces=NS)
    if fillbkg is None:
        fillbkg = etree.Element('{%s}Cell' % NS['v'], N="FillBkgnd")
        shape.append(fillbkg)
    fillbkg.set('V', 'Themed')
    fillbkg.set('F', 'THEMEVAL()')

    # --- Remove existing FillGradient section(s) ---
    for grad_section in shape.findall('v:Section[@N="FillGradient"]', namespaces=NS):
        shape.remove(grad_section)

    # --- Add FillGradient section ---
    grad_section = etree.Element('{%s}Section' % NS['v'], N="FillGradient")
    # Row 0
    row0 = etree.Element('{%s}Row' % NS['v'], IX="0")
    cell0a = etree.Element('{%s}Cell' % NS['v'], N="GradientStopColor", V="#e7e4cd")
    cell0b = etree.Element('{%s}Cell' % NS['v'], N="GradientStopColorTrans", V="0")
    row0.extend([cell0a, cell0b])
    grad_section.append(row0)
    # Row 1
    row1 = etree.Element('{%s}Row' % NS['v'], IX="1")
    cell1a = etree.Element('{%s}Cell' % NS['v'], N="GradientStopColor", V="#23b8e9", F="Inh")
    cell1b = etree.Element('{%s}Cell' % NS['v'], N="GradientStopColorTrans", V="0", F="Inh")
    row1.extend([cell1a, cell1b])
    grad_section.append(row1)
    shape.append(grad_section)

def standardize_text_connectors_and_fill(xml_path, output_path=None):
    NS = {'v': 'http://schemas.microsoft.com/office/visio/2012/main'}
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(xml_path, parser)
    root = tree.getroot()

    def ensure_character_section(shape):
        char_section = shape.find('.//v:Section[@N="Character"]', namespaces=NS)
        if char_section is None:
            char_section = etree.Element('{%s}Section' % NS['v'], N="Character")
            shape.append(char_section)
        row = char_section.find('.//v:Row[@IX="0"]', namespaces=NS)
        if row is None:
            row = etree.Element('{%s}Row' % NS['v'], IX="0")
            char_section.append(row)
        return row

    def standardize_connector(shape):
        nameu = shape.get('NameU', '').lower()
        if 'connector' in nameu:
            # LineWeight
            lw_cell = shape.find('v:Cell[@N="LineWeight"]', namespaces=NS)
            if lw_cell is None:
                lw_cell = etree.Element('{%s}Cell' % NS['v'], N="LineWeight", U=STANDARD_LINE_WEIGHT_UNIT)
                shape.append(lw_cell)
            lw_cell.set('V', STANDARD_LINE_WEIGHT)
            lw_cell.set('U', STANDARD_LINE_WEIGHT_UNIT)
            lw_cell.set('F', STANDARD_LINE_WEIGHT_F)
            # FillForegnd (for connector line color)
            ff_cell = shape.find('v:Cell[@N="FillForegnd"]', namespaces=NS)
            if ff_cell is None:
                ff_cell = etree.Element('{%s}Cell' % NS['v'], N="FillForegnd")
                shape.append(ff_cell)
            ff_cell.set('V', "#ADD8E6")
            ff_cell.set('F', 'THEMEVAL("FillColor",1)')
            # Remove LineColor if present (optional, since future state doesn't use it)
            for lc_cell in shape.findall('v:Cell[@N="LineColor"]', namespaces=NS):
                shape.remove(lc_cell)
            # Remove any FillGradient section
            for grad_section in shape.findall('v:Section[@N="FillGradient"]', namespaces=NS):
                shape.remove(grad_section)

    def process_shape(shape):
        # --- Standardize text ---
        has_text = shape.find('v:Text', namespaces=NS) is not None \
                   or shape.find('.//v:Section[@N="Character"]', namespaces=NS) is not None

        if has_text:
            row = ensure_character_section(shape)
            # Font
            font_cell = row.find('v:Cell[@N="Font"]', namespaces=NS)
            if font_cell is None:
                font_cell = etree.Element('{%s}Cell' % NS['v'], N="Font")
                row.append(font_cell)
            font_cell.set('V', STANDARD_FONT)
            font_cell.set('F', STANDARD_FONT_F)
            # Color
            color_cell = row.find('v:Cell[@N="Color"]', namespaces=NS)
            if color_cell is None:
                color_cell = etree.Element('{%s}Cell' % NS['v'], N="Color")
                row.append(color_cell)
            color_cell.set('V', STANDARD_COLOR)
            # Size
            size_cell = row.find('v:Cell[@N="Size"]', namespaces=NS)
            if size_cell is None:
                size_cell = etree.Element('{%s}Cell' % NS['v'], N="Size", U=STANDARD_SIZE_UNIT)
                row.append(size_cell)
            size_cell.set('V', STANDARD_SIZE)
            size_cell.set('U', STANDARD_SIZE_UNIT)
            # Style (bold only, no italics, no underline)
            style_cell = row.find('v:Cell[@N="Style"]', namespaces=NS)
            if style_cell is None:
                style_cell = etree.Element('{%s}Cell' % NS['v'], N="Style")
                row.append(style_cell)
            style_cell.set('V', STANDARD_STYLE)

        # --- Standardize connector if applicable ---
        nameu = shape.get('NameU', '').lower()
        if 'connector' in nameu:
            standardize_connector(shape)
        else:
            # --- Standardize fill/gradient for all non-connectors ---
            apply_firewall_gradient_format(shape, NS)

        # --- Process nested shapes if group ---
        nested_shapes = shape.find('v:Shapes', namespaces=NS)
        if nested_shapes is not None:
            for child_shape in nested_shapes.findall('v:Shape', namespaces=NS):
                process_shape(child_shape)

    # Top-level shapes
    shapes = root.find('v:Shapes', namespaces=NS)
    if shapes is not None:
        for shape in shapes.findall('v:Shape', namespaces=NS):
            process_shape(shape)

    if output_path is None:
        output_path = xml_path.replace('.xml', '_standardized.xml')
    tree.write(output_path, encoding='utf-8', xml_declaration=True, pretty_print=True)
    print(f"Standardized XML saved to: {output_path}")

# Example usage
standardize_text_connectors_and_fill('current_page.xml')

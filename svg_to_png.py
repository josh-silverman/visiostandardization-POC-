import cairosvg

# Example SVG code from AI (replace this string with your actual SVG output)
svg_code = """
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">
  <!-- Squares -->
  <!-- Top Square -->
  <rect x="325" y="50" width="100" height="100" fill="none" stroke="black" />
  <text x="360" y="110" font-family="Arial" font-size="12" text-anchor="middle">Square</text>

  <!-- Middle Square (Diamond replacement) -->
  <rect x="325" y="200" width="100" height="100" fill="none" stroke="black" />
  <text x="375" y="260" font-family="Arial" font-size="12" text-anchor="middle">Diamond</text>

  <!-- Bottom Square -->
  <rect x="325" y="350" width="100" height="100" fill="none" stroke="black" />
  <text x="375" y="410" font-family="Arial" font-size="12" text-anchor="middle">Rectangle</text>

  <!-- Left Square -->
  <rect x="150" y="200" width="100" height="100" fill="none" stroke="black" />
  <text x="200" y="260" font-family="Arial" font-size="12" text-anchor="middle">Circle</text>

  <!-- Bottom-left Square -->
  <rect x="150" y="425" width="100" height="100" fill="none" stroke="black" />
  <text x="200" y="485" font-family="Arial" font-size="12" text-anchor="middle">Semi-circle</text>

  <!-- Right Square -->
  <rect x="575" y="200" width="100" height="100" fill="none" stroke="black" />
  <text x="625" y="260" font-family="Arial" font-size="12" text-anchor="middle">Hexagon</text>

  <!-- Bottom-right Square -->
  <rect x="575" y="425" width="100" height="100" fill="none" stroke="black" />
  <text x="625" y="485" font-family="Arial" font-size="12" text-anchor="middle">Circle</text>

  <!-- Connectors/Arrows -->
  <!-- Arrow from middle square to top square -->
  <line x1="375" y1="200" x2="375" y2="150" stroke="black" marker-end="url(#arrow)" />

  <!-- Arrow from left square to middle square -->
  <line x1="250" y1="250" x2="325" y2="250" stroke="black" marker-end="url(#arrow)" />

  <!-- Arrow from middle square to right square -->
  <line x1="425" y1="250" x2="575" y2="250" stroke="black" marker-end="url(#arrow)" />
  <polyline points="425,250 475,250 475,240 575,240" fill="none" stroke="black" />

  <!-- Arrow from middle square to bottom square -->
  <line x1="375" y1="300" x2="375" y2="350" stroke="black" marker-end="url(#arrow)" />

  <!-- Arrow from bottom-left square to bottom square -->
  <line x1="250" y1="475" x2="325" y2="475" stroke="black" marker-end="url(#arrow)" />
  <polyline points="250,475 275,475 275,450 325,450" fill="none" stroke="black" />

  <!-- Arrow from bottom-right square to bottom-left square -->
  <line x1="575" y1="475" x2="375" y2="475" stroke="black" marker-end="url(#arrow)" />
  <polyline points="575,475 550,475 550,445 375,445" fill="none" stroke="black" />

  <!-- Arrow marker definition -->
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="black" />
    </marker>
  </defs>
</svg>
"""

# Convert SVG code to PNG and save to a file
cairosvg.svg2png(bytestring=svg_code.encode('utf-8'), write_to='output.png')

print("PNG image saved as output1.png")

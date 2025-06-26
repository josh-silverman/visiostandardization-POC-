# Visio Diagram Standardization Pipeline

This project provides a workflow to enhance and standardize Visio diagrams using AI, and regenerate them as fully functional `.vsdx` files.

---

## **Workflow Overview**

### 1. **Extract Visio Page XML**
- **Script:** `extract_xml.py`
- **Purpose:** Extracts the raw XML files (including pages, masters, and resources) from a Visio `.vsdx` file and places them in the `output_xml` folder for further processing.

### 2. **Parse Visio XML**
- **Script:** `parse_visio_xml.py`
- **Purpose:** Parses the Visio `page1.xml` (and related XML files), extracting shapes, their properties, and connections into a structured JSON file (`diagram_full_page1.json`).

### 3. **Enhance Diagram with AI**
- **Script:** `ai_enhance_json.py`
- **Purpose:** Sends `diagram_full_page1.json` to Azure OpenAI for enhancement. The AI adds human-friendly features such as colors, text alignment, and bold connectors, producing `enhanced_diagram_full_page1.json`.

### 4. **Update Visio Page XML**
- **Script:** `update_visio_xml.py`
- **Purpose:** Reads the enhanced JSON (`enhanced_diagram_full_page1.json`) and updates the corresponding Visio `output_xml/visio/pages/page1.xml` (and possibly other XML files) with new shape properties (text, fill color, alignment, connector style, etc.).

### 5. **Create Enhanced VSDX**
- **Script:** `create_vsdx.py`
- **Purpose:** Packages the updated `output_xml` folder back into a `.vsdx` file (`enhanced_diagram.vsdx`) that can be opened in Microsoft Visio.

---

## **Script Execution Order**

1. `extract_xml.py`
2. `parse_visio_xml.py`
3. `ai_enhance_json.py`
4. `update_visio_xml.py`
5. `create_vsdx.py`

---

## **Key Files**

- **input:**  
  - Your source `.vsdx` file (to be extracted)
- **intermediate:**  
  - `output_xml/visio/pages/page1.xml` — working copy of the Visio page XML
  - `diagram_full_page1.json` — initial parsed diagram data
  - `enhanced_diagram_full_page1.json` — AI-enhanced diagram data
- **output:**  
  - `enhanced_diagram.vsdx` — the final, enhanced Visio file

---

## **Requirements**

- Python 3.8+
- See `requirements.txt` for dependencies.

---

## **Notes**

- The `.env` file is required for Azure OpenAI API authentication.
- For custom diagrams or multiple pages, adjust script parameters and filenames as needed.

---

*If you need details for each script’s arguments or want a one-liner for each step, just ask!*



Summary of Your Visio + LLM Enhancement Pipeline
You have built a robust, semi-automated pipeline that takes raw Visio diagram data, enhances it using a Large Language Model (LLM), and updates the diagram’s XML representation—making your Visio diagrams smarter, cleaner, and visually informative.

How Your Pipeline Works:
Extract Raw Diagram Data:

You start with a Visio diagram and export or extract its shapes and connections as JSON (e.g., page1.json).
Standardize and Enrich with LLM:

You send this JSON to an LLM (via Azure OpenAI) with a carefully crafted prompt.
The LLM:
Fills in missing fields (like labels, roles, and directions).
Standardizes and cleans up the structure.
Infers metadata (roles, groups, connection direction).
Adds styling fields (e.g., FillColor, LineColor) based on business rules (like color-coding by role or group).
Returns a summary paragraph describing the diagram.
Save Enhanced Output:

You save the LLM’s enhanced JSON and its diagram summary for documentation.
Update Visio XML:

A Python script reads the enhanced JSON and updates your Visio XML files:
Applies standardized labels, text, and attributes.
Updates shape and connector styles (colors, lines) according to the enhanced data.
Optionally, makes a backup of the original XML for safety.
Ensures all references and fields are correct and complete.
Visual Result:

You open the updated Visio file and see a clean, labeled, color-coded diagram, with all shapes and connectors reflecting their roles and relationships.
The diagram summary provides a human-readable overview of the structure.
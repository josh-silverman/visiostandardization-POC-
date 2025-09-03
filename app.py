import streamlit as st
import traceback
import os
import time
from datetime import datetime

# --- Import your backend functions ---
from extract_xml import main as run_extract_xml
from first_step import standardize_text_connectors_and_fill as run_standardize
from footer import main as run_footer
from create_vsdx import main as run_create_vsdx

# Professional pipeline configuration
PIPELINE_CONFIG = {
    "steps": [
        {
            "id": "upload",
            "title": "Upload Visio File",
            "description": "Upload your .vsdx file for processing",
            "icon": "📁",
            "function": None,
            "estimated_time": "Instant"
        },
        {
            "id": "extract",
            "title": "Extract & Parse",
            "description": "Extract XML content from Visio file",
            "icon": "🔍",
            "function": run_extract_xml,
            "estimated_time": "5-10 seconds"
        },
        {
            "id": "standardize",
            "title": "Standardize Diagram",
            "description": "Apply Oregon DMV visual standards (fonts, colors, properties)",
            "icon": "🎨",
            "function": lambda: run_standardize("output_xml/visio/pages/page1.xml"),
            "estimated_time": "10-30 seconds"
        },
        {
            "id": "footer",
            "title": "Add Footer",
            "description": "Apply standardized Oregon classification footer",
            "icon": "📝",
            "function": run_footer,
            "estimated_time": "2-5 seconds"
        },
        {
            "id": "repackage",
            "title": "Create Final File",
            "description": "Package standardized content into new .vsdx file",
            "icon": "📦",
            "function": run_create_vsdx,
            "estimated_time": "5-10 seconds"
        }
    ]
}

def init_session_state():
    """Initialize session state variables"""
    if "step_status" not in st.session_state:
        st.session_state.step_status = {step["id"]: False for step in PIPELINE_CONFIG["steps"]}
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "current_step" not in st.session_state:
        st.session_state.current_step = None
    if "uploaded_filename" not in st.session_state:
        st.session_state.uploaded_filename = None
    if "processing_start_time" not in st.session_state:
        st.session_state.processing_start_time = None
    if "processing_started" not in st.session_state:
        st.session_state.processing_started = False

def reset_pipeline():
    """Reset all pipeline steps"""
    st.session_state.step_status = {step["id"]: False for step in PIPELINE_CONFIG["steps"]}
    st.session_state.processing = False
    st.session_state.current_step = None
    st.session_state.processing_start_time = None
    st.session_state.processing_started = False

def get_step_status_icon(step_id):
    """Get status icon for a step"""
    if st.session_state.processing and st.session_state.current_step == step_id:
        return "🔄"
    elif st.session_state.step_status.get(step_id, False):
        return "✅"
    else:
        return "⬜"

def create_progress_bar():
    """Create a professional progress indicator"""
    completed_steps = sum(1 for status in st.session_state.step_status.values() if status)
    total_steps = len(PIPELINE_CONFIG["steps"])
    progress = completed_steps / total_steps
    
    st.progress(progress)
    st.caption(f"Progress: {completed_steps}/{total_steps} steps completed ({progress:.0%})")

def display_pipeline_status():
    """Display current pipeline status with professional styling"""
    st.markdown("### 🔄 Pipeline Status")
    create_progress_bar()
    
    # Single column layout for cleaner appearance
    for step in PIPELINE_CONFIG["steps"]:
        step_id = step["id"]
        status_icon = get_step_status_icon(step_id)
        
        # Professional color coding based on status
        if st.session_state.step_status.get(step_id, False):
            st.success(f"{status_icon} {step['icon']} **{step['title']}** - {step['description']}")
        elif st.session_state.processing and st.session_state.current_step == step_id:
            st.info(f"{status_icon} {step['icon']} **{step['title']}** - Processing...")
        else:
            st.info(f"{status_icon} {step['icon']} **{step['title']}** - {step['description']}")

def run_step(step):
    """Execute a single pipeline step with professional error handling"""
    step_id = step["id"]
    st.session_state.current_step = step_id
    
    try:
        if step["function"] is not None:
            with st.spinner(f"Processing {step['title']}..."):
                step["function"]()
        
        st.session_state.step_status[step_id] = True
        st.session_state.current_step = None
        return True
        
    except Exception as e:
        st.session_state.step_status[step_id] = False
        st.session_state.current_step = None
        st.error(f"❌ **{step['title']} Failed**")
        
        # Professional error display
        with st.expander("🔍 Error Details", expanded=False):
            st.code(f"Error: {str(e)}")
            st.code(traceback.format_exc())
        
        return False

def main():
    # Professional page configuration
    st.set_page_config(
        page_title="State of Oregon Visio Standardizer",
        page_icon="🗂️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Professional State of Oregon header
    st.markdown("""
    <div style="background: linear-gradient(90deg, #23b8e9 0%, #1a8fb8 100%); padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0; text-align: center; font-weight: 600;">
            🗂️ State of Oregon Visio Network Diagram Standardizer
        </h1>
        <p style="color: white; margin: 0.5rem 0 0 0; text-align: center; opacity: 0.95; font-size: 1.1rem;">
            Transform your network diagrams to State of Oregon standards
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Professional sidebar
    with st.sidebar:
        st.header("🎛️ Controls")
        
        # File upload section
        st.markdown("### 📁 File Upload")
        uploaded_file = st.file_uploader(
            "Choose a Visio file",
            type=["vsdx"],
            help="Select your .vsdx file to begin the standardization process"
        )
        
        if uploaded_file is not None:
            if st.session_state.uploaded_filename != uploaded_file.name:
                # New file uploaded, reset pipeline
                reset_pipeline()
                st.session_state.uploaded_filename = uploaded_file.name
            
            # Save uploaded file
            with open("input.vsdx", "wb") as f:
                f.write(uploaded_file.read())
            st.session_state.step_status["upload"] = True
            st.success(f"✅ {uploaded_file.name}")
        else:
            st.session_state.step_status["upload"] = False
            st.session_state.uploaded_filename = None
        
        st.markdown("---")
        
        # Processing controls - only show if file is uploaded
        if st.session_state.step_status.get("upload", False):
            st.markdown("### 🚦 Processing")
            
            can_run = st.session_state.step_status.get("upload", False) and not st.session_state.processing
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶️ Run All", disabled=not can_run, use_container_width=True):
                    st.session_state.processing = True
                    st.session_state.processing_started = True  # Mark that processing has been initiated
                    st.session_state.processing_start_time = time.time()
                    st.rerun()
            
            with col2:
                if st.button("🔄 Reset", use_container_width=True):
                    reset_pipeline()
                    st.rerun()
            
            # Processing time display - only during processing
            if st.session_state.processing_start_time and st.session_state.processing:
                elapsed = time.time() - st.session_state.processing_start_time
                st.metric("⏱️ Processing Time", f"{elapsed:.1f}s")
            
            st.markdown("---")
        
        # System info - only show relevant information when files exist
        st.markdown("### ℹ️ System Info")
        st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # File system status - only show files that exist
        if os.path.exists("input.vsdx"):
            file_size = os.path.getsize("input.vsdx") / 1024  # KB
            st.caption(f"📊 Input file: {file_size:.1f} KB")
        
        if os.path.exists("output.vsdx"):
            file_size = os.path.getsize("output.vsdx") / 1024  # KB
            st.caption(f"📤 Output file: {file_size:.1f} KB")

    # Main content area
    display_pipeline_status()
    
    # Process pipeline if running
    if st.session_state.processing:
        steps_to_process = [step for step in PIPELINE_CONFIG["steps"] 
                           if not st.session_state.step_status.get(step["id"], False)]
        
        if steps_to_process:
            current_step = steps_to_process[0]
            if current_step["id"] != "upload":  # Skip upload step in processing
                success = run_step(current_step)
                if success:
                    st.rerun()  # Continue to next step
                else:
                    st.session_state.processing = False  # Stop on error
            else:
                # Skip upload step and continue
                st.session_state.step_status["upload"] = True
                st.rerun()
        else:
            # All steps completed - professional completion message
            st.session_state.processing = False
            st.success("✅ **Pipeline completed successfully** - All standardization steps have been applied")
    
    st.markdown("---")
    
    # Professional download section - only show when output file exists and all steps complete
    output_path = "output.vsdx"
    all_steps_complete = all(st.session_state.step_status.values())
    
    if os.path.isfile(output_path) and all_steps_complete:
        st.markdown("### 📥 Download Results")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            with open(output_path, "rb") as f:
                original_name = st.session_state.uploaded_filename or "diagram"
                base_name = original_name.replace('.vsdx', '')
                output_filename = f"{base_name}_standardized.vsdx"
                
                st.download_button(
                    "⬇️ Download Standardized Diagram",
                    data=f.read(),
                    file_name=output_filename,
                    mime="application/vnd.visio",
                    use_container_width=True,
                    type="primary"
                )
        
        with col2:
            file_size = os.path.getsize(output_path) / 1024
            st.metric("File Size", f"{file_size:.1f} KB")
        
        with col3:
            if st.session_state.processing_start_time:
                total_time = time.time() - st.session_state.processing_start_time
                st.metric("Total Time", f"{total_time:.1f}s")
    
    elif st.session_state.step_status.get("upload", False) and not all_steps_complete:
        st.info("📋 Complete all pipeline steps to download the standardized diagram")
    
    # Professional advanced options section - ONLY show if processing has been started
    if st.session_state.processing_started:
        st.markdown("---")
        
        with st.expander("🔍 Advanced Options & Preview", expanded=False):
            tab1, tab2, tab3 = st.tabs(["📄 XML Preview", "📊 Processing Log", "⚙️ Settings"])
            
            with tab1:
                st.markdown("#### Standardized XML Preview")
                xml_path = "output_xml/visio/pages/page1.xml"
                
                if os.path.isfile(xml_path):
                    try:
                        with open(xml_path, "r", encoding="utf-8") as f:
                            xml_content = f.read()
                        
                        # Professional search functionality
                        search_term = st.text_input("🔍 Search XML content:", placeholder="Enter search term...")
                        
                        if search_term:
                            lines = xml_content.split('\n')
                            matching_lines = [f"Line {i+1}: {line.strip()}" for i, line in enumerate(lines) 
                                            if search_term.lower() in line.lower()]
                            
                            if matching_lines:
                                st.success(f"Found {len(matching_lines)} matches:")
                                for match in matching_lines[:10]:  # Show first 10 matches
                                    st.code(match, language="xml")
                                if len(matching_lines) > 10:
                                    st.info(f"... and {len(matching_lines) - 10} more matches")
                            else:
                                st.warning("No matches found")
                        
                        # Display XML with professional formatting
                        st.code(xml_content[:5000] + ("..." if len(xml_content) > 5000 else ""), 
                               language="xml")
                        
                        if len(xml_content) > 5000:
                            st.info(f"Showing first 5,000 characters of {len(xml_content):,} total")
                            
                    except Exception as e:
                        st.error(f"Error reading XML file: {e}")
                else:
                    st.info("XML file not available. Complete the extraction step first.")
            
            with tab2:
                st.markdown("#### Processing Log")
                
                # Professional step status table
                import pandas as pd
                
                log_data = []
                for i, step in enumerate(PIPELINE_CONFIG["steps"]):
                    status = "✅ Completed" if st.session_state.step_status.get(step["id"], False) else "⏳ Pending"
                    log_data.append({
                        "Step": i,
                        "Process": step["title"],
                        "Status": status,
                        "Description": step["description"],
                        "Estimated Time": step["estimated_time"]
                    })
                
                df = pd.DataFrame(log_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Professional file system status - only show files that exist
                st.markdown("##### File System Status")
                files_to_check = [
                    ("input.vsdx", "Input Visio file"),
                    ("output_xml/visio/pages/page1.xml", "Extracted XML"),
                    ("output.vsdx", "Final output file")
                ]
                
                files_exist = False
                for filepath, description in files_to_check:
                    if os.path.exists(filepath):
                        size = os.path.getsize(filepath)
                        st.success(f"✅ {description}: {size:,} bytes")
                        files_exist = True
                
                if not files_exist:
                    st.info("⏳ No processed files available yet. Run the pipeline to generate files.")
            
            with tab3:
                st.markdown("#### Configuration & Standards")
                
                # Professional configuration display
                st.markdown("##### State of Oregon Standardization Settings")
                
                config_col1, config_col2 = st.columns(2)
                
                with config_col1:
                    st.markdown("""
                    **Visual Standards:**
                    - Primary Color: Oregon Blue (#23b8e9)
                    - Font Family: Calibri
                    - Line Weight: Standardized
                    - Shape Consistency: Enforced
                    """)
                
                with config_col2:
                    st.markdown("""
                    **Compliance Level:**
                    - Classification: Level 3 - Restricted
                    - Footer: State of Oregon
                    - Format: Microsoft Visio (.vsdx)
                    - Validation: Automated
                    """)
                
                st.markdown("##### Pipeline Statistics")
                stats_col1, stats_col2, stats_col3 = st.columns(3)
                
                with stats_col1:
                    st.metric("Total Steps", len(PIPELINE_CONFIG["steps"]))
                
                with stats_col2:
                    completed = sum(1 for status in st.session_state.step_status.values() if status)
                    st.metric("Completed Steps", completed)
                
                with stats_col3:
                    if st.session_state.processing_start_time and not st.session_state.processing:
                        total_time = time.time() - st.session_state.processing_start_time
                        st.metric("Processing Time", f"{total_time:.1f}s")
                    elif st.session_state.processing and st.session_state.processing_start_time:
                        elapsed = time.time() - st.session_state.processing_start_time
                        st.metric("Current Time", f"{elapsed:.1f}s")
                    else:
                        st.metric("Processing Time", "Not started")
    
    # Professional Oregon footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1.5rem; background-color: #f8f9fa; border-radius: 8px; margin-top: 2rem;">
        <div style="margin-bottom: 0.5rem;">
            <strong>🏛️ State of Oregon | Enterprise Information Services</strong>
        </div>
        <div style="font-size: 0.9rem;">
            📋 Classification: Level 3 - Restricted | 🔒 For Internal Use Only
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()





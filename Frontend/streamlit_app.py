import streamlit as st
import requests
import time
import json

# Configuration
API_URL = "http://localhost:8000"

st.set_page_config(page_title="EVA Phase 1 Tester", layout="wide")

st.title("EVA: Autonomous Data Science Assistant")
st.markdown("### Phase 1: Core Foundation & Dataset Intelligence")

# --- Initialize session state ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'csv_filename' not in st.session_state:
    st.session_state.csv_filename = None
if 'pipeline_status' not in st.session_state:
    st.session_state.pipeline_status = None

# --- UI Layout ---
col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Session Setup")
    
    if st.button("Initialize New Session"):
        try:
            resp = requests.post(f"{API_URL}/session/create")
            resp.raise_for_status()
            data = resp.json()
            st.session_state.session_id = data["session_id"]
            st.success(f"Session Created: {st.session_state.session_id[:8]}...")
        except Exception as e:
            st.error(f"Failed: {str(e)}")
            
    if st.session_state.session_id:
        st.header("2. Upload Dataset")
        uploaded_file = st.file_uploader("Upload CSV", type="csv")
        
        if uploaded_file is not None and st.button("Upload to EVA"):
            with st.spinner("Uploading..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                try:
                    resp = requests.post(f"{API_URL}/session/{st.session_state.session_id}/upload", files=files)
                    resp.raise_for_status()
                    st.session_state.csv_filename = uploaded_file.name
                    st.success("File uploaded successfully!")
                except Exception as e:
                    st.error(f"Upload failed: {str(e)}")

    if st.session_state.csv_filename:
        st.header("3. Run Pipeline")
        st.markdown("Executes: **DPSU -> QBII -> DRIL -> EPR**")
        
        if st.button("Execute Intelligence Phase 1"):
            with st.spinner("EVA is Reasoning... this may take 20-30 seconds"):
                try:
                    params = {"csv_file_name": st.session_state.csv_filename}
                    resp = requests.post(f"{API_URL}/session/{st.session_state.session_id}/execute", params=params)
                    resp.raise_for_status()
                    data = resp.json()
                    if data.get("error"):
                        st.error(f"Pipeline Error: {data['error']}")
                    else:
                        st.session_state.pipeline_status = data["status"]
                        st.success("Pipeline Execution Complete!")
                except Exception as e:
                    st.error(f"Execution failed: {str(e)}")

with col2:
    st.header("Global Analysis Ledger (GAL)")
    
    if st.session_state.session_id:
        if st.button("Refresh GAL State"):
            try:
                resp = requests.get(f"{API_URL}/session/{st.session_state.session_id}/gal")
                resp.raise_for_status()
                gal_data = resp.json()
                
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Identity", "Intent", "Integrity", "Findings"])
                
                with tab1:
                    st.json({"session_id": gal_data["session_id"], "created_at": gal_data["created_at"]})
                    
                with tab2:
                    if gal_data.get("dataset_identity"):
                        st.json(gal_data["dataset_identity"])
                    else:
                        st.info("No Identity Data Yet")
                        
                with tab3:
                    if gal_data.get("user_intent"):
                        st.json(gal_data["user_intent"])
                    else:
                        st.info("No Intent Data Yet")
                        
                with tab4:
                    if gal_data.get("data_integrity"):
                        st.json(gal_data["data_integrity"])
                    else:
                        st.info("No Integrity Data Yet")
                        
                with tab5:
                    if gal_data.get("exploratory_findings"):
                        st.json(gal_data["exploratory_findings"])
                    else:
                        st.info("No Exploratory Data Yet")
                        
            except Exception as e:
                st.error("Failed to read GAL (it may not be initialized).")
    else:
        st.info("Create a session to view the GAL.")

import streamlit as st
import requests
import json
import time

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Backend.config import settings

# Configuration
API_URL = settings.streamlit.api_url
TIMEOUT = settings.execution.default_timeout

st.set_page_config(page_title="EVA LOM Pipeline", layout="wide", page_icon="🔍")

st.title("EVA: Observability & Diagnostics (LOM)")
st.markdown("### Logging, Monitoring & Observability Pipeline")

# --- Initialize session state ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'pipeline_status' not in st.session_state:
    st.session_state.pipeline_status = None
if 'has_lom_data' not in st.session_state:
    st.session_state.has_lom_data = False
if 'has_lom_profile' not in st.session_state:
    st.session_state.has_lom_profile = False
if 'has_lom_timeline' not in st.session_state:
    st.session_state.has_lom_timeline = False
if 'has_lom_report' not in st.session_state:
    st.session_state.has_lom_report = False

# --- UI Layout ---
col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Session Setup")

    # --- Resume existing session ---
    api_error = False
    try:
        sessions_resp = requests.get(f"{API_URL}/session/list", timeout=5)
        if sessions_resp.status_code == 200:
            sessions_list = sessions_resp.json()
        else:
            sessions_list = []
            api_error = True
    except Exception:
        sessions_list = []
        api_error = True

    if api_error:
        st.error("⚠️ Cannot connect to the backend API. Please ensure the backend server is running.")
    elif not sessions_list:
        st.info("No previous sessions found.")
    
    if sessions_list:
        def _session_label(s):
            sid = s["session_id"][:8]
            files_count = s.get("lom_file_count", 0)
            data_info = f"{files_count} files" if files_count else "no LOM data"
            steps = []
            if s.get("has_lom_report"): steps.append("Report✅")
            elif s.get("has_lom_rca"): steps.append("RCA✅")
            elif s.get("has_lom_timeline"): steps.append("Timeline✅")
            elif s.get("has_lom_profile"): steps.append("Profile✅")
            elif s.get("has_lom_data"): steps.append("Data✅")
            progress = f" [{', '.join(steps)}]" if steps else ""
            return f"{sid}... | {data_info}{progress}"

        options = ["— Select a session —"] + [s["session_id"] for s in sessions_list]
        labels = ["— Select a session —"] + [_session_label(s) for s in sessions_list]

        selected = st.selectbox("Resume existing session", options, format_func=lambda x: labels[options.index(x)])

        if selected != "— Select a session —" and selected != st.session_state.session_id:
            if st.button("Load LOM Session"):
                s_info = next((s for s in sessions_list if s["session_id"] == selected), None)
                st.session_state.session_id = selected
                st.session_state.has_lom_data = s_info.get("has_lom_data", False) if s_info else False
                st.session_state.has_lom_profile = s_info.get("has_lom_profile", False) if s_info else False
                st.session_state.has_lom_timeline = s_info.get("has_lom_timeline", False) if s_info else False
                st.session_state.has_lom_report = s_info.get("has_lom_report", False) if s_info else False
                st.success(f"Loaded session: {selected[:8]}...")
                st.rerun()

        st.markdown("---")

    if st.button("Initialize New Session"):
        try:
            resp = requests.post(f"{API_URL}/session/create")
            resp.raise_for_status()
            data = resp.json()
            st.session_state.session_id = data["session_id"]
            st.session_state.has_lom_data = False
            st.session_state.has_lom_profile = False
            st.session_state.has_lom_timeline = False
            st.session_state.has_lom_report = False
            st.session_state.pipeline_status = None
            st.success(f"Session Created: {st.session_state.session_id[:8]}...")
        except Exception as e:
            st.error(f"Failed: {str(e)}")
            
    if st.session_state.session_id:
        st.header("2. Upload LOM Data")
        st.markdown("Upload your logs, JSON metrics, code snippets, or configuration files.")
        
        uploaded_files = st.file_uploader("Upload observability files", accept_multiple_files=True)
        
        if uploaded_files and st.button("Upload to EVA LOM"):
            with st.spinner("Uploading..."):
                files_to_upload = [("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files]
                try:
                    resp = requests.post(f"{API_URL}/session/{st.session_state.session_id}/upload-lom", files=files_to_upload)
                    resp.raise_for_status()
                    result = resp.json()
                    st.session_state.has_lom_data = True
                    st.success(f"Successfully uploaded {result.get('total_uploaded')} files!")
                    if result.get("errors"):
                        for err in result["errors"]:
                            st.warning(err)
                    st.rerun()
                except Exception as e:
                    st.error(f"Upload failed: {str(e)}")

        st.markdown("---")

    if st.session_state.has_lom_data:
        st.header("3. Profile & Structure")
        st.markdown("Parses unstructured files into high-fidelity models and creates empirical profiles.")

        if st.button("Run LOM Profiler"):
            with st.spinner("EVA is parsing and profiling your observability data..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/session/{st.session_state.session_id}/execute/lom-profile",
                        timeout=TIMEOUT,
                    )
                    if resp.status_code != 200:
                        st.error(f"Profile Error ({resp.status_code}): {resp.text}")
                    else:
                        data = resp.json()
                        st.session_state.has_lom_profile = True
                        st.success("Profiling complete! Check LOM GAL.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Execution failed: {str(e)}")
                    
        st.markdown("---")

    if st.session_state.has_lom_profile:
        st.header("4. Timeline & Root Cause")
        st.markdown("Reconstructs the chronological event sequence, detects anomalies, and generates evidence-backed RCA hypotheses.")

        if st.button("Run Timeline & RCA"):
            with st.spinner("EVA is reconstructing timelines and identifying root causes..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/session/{st.session_state.session_id}/execute/lom-timeline",
                        timeout=TIMEOUT,
                    )
                    if resp.status_code != 200:
                        st.error(f"Timeline/RCA Error ({resp.status_code}): {resp.text}")
                    else:
                        data = resp.json()
                        st.session_state.has_lom_timeline = True
                        st.success(f"Timeline complete! Found {data.get('anomalies_found')} anomalies and {data.get('hypotheses_count')} hypotheses.")
                        st.rerun()
                except Exception as e:
                    st.error(f"Execution failed: {str(e)}")
                    
        st.markdown("---")

    if st.session_state.has_lom_timeline:
        st.header("5. Executive Report")
        st.markdown("Generates a clear, actionable narrative Root Cause Analysis report with remediation steps.")

        if st.button("Generate RCA Report"):
            with st.spinner("EVA is compiling the final RCA narrative..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/session/{st.session_state.session_id}/execute/lom-report",
                        timeout=TIMEOUT,
                    )
                    if resp.status_code != 200:
                        st.error(f"Report Error ({resp.status_code}): {resp.text}")
                    else:
                        data = resp.json()
                        st.session_state.has_lom_report = True
                        st.success("RCA Report generated successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Execution failed: {str(e)}")


with col2:
    st.header("LOM Analysis Ledger (LOM GAL)")
    
    if st.session_state.session_id:
        if st.button("Refresh LOM GAL State"):
            try:
                resp = requests.get(f"{API_URL}/session/{st.session_state.session_id}/lom-gal", timeout=5)
                if resp.status_code == 404:
                    st.info("LOM GAL is empty. Upload data to begin.")
                else:
                    resp.raise_for_status()
                    gal = resp.json()
                    
                    t1, t2, t3, t4, t5, t6, t7, t8 = st.tabs([
                        "Source Inv", "Log Profile", "Metric Profile", "Code Context", 
                        "Timeline", "Anomalies", "RCA Hypotheses", "RCA Report"
                    ])
                    
                    with t1:
                        if gal.get("source_inventory"):
                            st.json(gal["source_inventory"])
                        else:
                            st.info("No Source Inventory Yet")
                            
                    with t2:
                        if gal.get("log_profile"):
                            st.json(gal["log_profile"])
                        else:
                            st.info("No Log Profile Yet")
                            
                    with t3:
                        if gal.get("metric_profile"):
                            st.json(gal["metric_profile"])
                        else:
                            st.info("No Metric Profile Yet")
                            
                    with t4:
                        if gal.get("code_context") and gal["code_context"].get("artifacts"):
                            for i, art in enumerate(gal["code_context"]["artifacts"]):
                                st.markdown(f"**Code File:** `{art.get('filename')}` ({art.get('language')})")
                                if art.get("functions_detected"):
                                    st.markdown(f"Functions: {', '.join(art['functions_detected'])}")
                                if art.get("traceback"):
                                    st.error(f"Traceback ({art.get('error_type', 'Unknown')}):")
                                    st.code(art["traceback"], language=art.get("language", "text"))
                                st.markdown("---")
                        else:
                            st.info("No Code Context Yet")
                            
                    with t5:
                        if gal.get("timeline") and gal["timeline"].get("event_sequence"):
                            st.markdown(f"**Overall Time Range:** {gal['timeline'].get('overall_start_time', '?')} to {gal['timeline'].get('overall_end_time', '?')}")
                            if gal['timeline'].get('chronological_narrative'):
                                st.markdown(f"_{gal['timeline']['chronological_narrative']}_")
                            st.markdown("---")
                            
                            for ev in gal["timeline"]["event_sequence"]:
                                badge = "🔴" if ev.get("severity") in ("ERROR", "CRITICAL") else ("🟡" if ev.get("severity") in ("WARN", "WARNING") else "🔵")
                                st.markdown(f"{badge} **{ev.get('timestamp')}** | [{ev.get('source_file')}]")
                                st.markdown(f"**{ev.get('description')}**")
                                if ev.get("associated_metric") or ev.get("associated_code"):
                                    st.caption(f"Code: {ev.get('associated_code')} | Metric: {ev.get('associated_metric')}")
                                st.markdown("---")
                        else:
                            st.info("No Timeline Yet")
                            
                    with t6:
                        if gal.get("anomaly_findings") and gal["anomaly_findings"].get("anomalies"):
                            st.error(f"**Primary Disruption System:** {gal['anomaly_findings'].get('primary_disruption_system', 'Unknown')}")
                            for anom in gal["anomaly_findings"]["anomalies"]:
                                st.markdown(f"### 🚨 {anom.get('type')}: {anom.get('description')}")
                                st.markdown(f"**First seen:** {anom.get('first_seen_timestamp')} | **Last seen:** {anom.get('last_seen_timestamp')}")
                                st.markdown(f"**Affected Systems:** {', '.join(anom.get('affected_systems', []))}")
                                if anom.get("cascade_pattern"):
                                    st.info(f"Cascade: {anom['cascade_pattern']}")
                                st.markdown("---")
                        else:
                            st.info("No Anomalies Found Yet")
                            
                    with t7:
                        if gal.get("rca_hypotheses"):
                            rca = gal["rca_hypotheses"]
                            st.markdown(f"**Primary Suspect Entity:** {rca.get('primary_suspect_entity', 'Unknown')}")
                            if rca.get("overall_reasoning"):
                                st.markdown(f"_{rca['overall_reasoning']}_")
                            st.markdown("---")
                            for i, hyp in enumerate(rca.get("hypotheses", [])):
                                plaus = hyp.get("plausibility", "Unknown")
                                badge = {"High": "🟢", "Moderate": "🟡", "Low": "🔴"}.get(plaus, "⚪")
                                st.markdown(f"### {badge} Hypothesis {i+1}: {plaus} Plausibility")
                                st.markdown(f"**Root Cause:** {hyp.get('proposed_root_cause')}")
                                if hyp.get("five_whys"):
                                    with st.expander("5 Whys Analysis"):
                                        for why in hyp["five_whys"]:
                                            st.markdown(f"- {why}")
                                with st.expander("Evidence Chain"):
                                    for ev in hyp.get("evidence_chain", []):
                                        st.markdown(f"- {ev}")
                                st.caption(f"Confidence Note: {hyp.get('confidence_note', 'None')}")
                                st.markdown("---")
                        else:
                            st.info("No RCA Hypotheses Yet")
                            
                    with t8:
                        if gal.get("rca_report"):
                            # The RCA report could have sections or just be one big dict
                            st.json(gal["rca_report"])
                        else:
                            st.info("No RCA Report Yet")
                            
            except Exception as e:
                st.error(f"Failed to fetch LOM GAL: {e}")

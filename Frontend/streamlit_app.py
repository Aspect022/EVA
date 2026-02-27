import streamlit as st
import requests
import json
import time

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Backend.config import settings

# Configuration
API_URL = settings.streamlit.api_url
TIMEOUT = settings.execution.default_timeout

st.set_page_config(page_title="EVA Testing UI", layout="wide")

st.title("EVA: Autonomous Data Science Assistant")
st.markdown("### Pipeline Testing Interface")

# --- Rules Mode Toggle ---
rules_mode = st.radio(
    "Rules Mode",
    ["full", "lite"],
    format_func=lambda x: "🔥 Full (detailed reasoning)" if x == "full" else "⚡ Lite (faster, shorter prompts)",
    horizontal=True,
    help="Full uses detailed 5-step reasoning rules. Lite uses condensed rules for faster/smaller models.",
)

# --- Initialize session state ---
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'csv_filename' not in st.session_state:
    st.session_state.csv_filename = None
if 'pipeline_status' not in st.session_state:
    st.session_state.pipeline_status = None
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'intent_confirmed' not in st.session_state:
    st.session_state.intent_confirmed = False
if 'phase1b_complete' not in st.session_state:
    st.session_state.phase1b_complete = False
if 'hypotheses_generated' not in st.session_state:
    st.session_state.hypotheses_generated = False
if 'has_visualizations' not in st.session_state:
    st.session_state.has_visualizations = False
if 'has_dashboard' not in st.session_state:
    st.session_state.has_dashboard = False
if 'has_features' not in st.session_state:
    st.session_state.has_features = False
if 'has_report' not in st.session_state:
    st.session_state.has_report = False
if 'quick_mode_available' not in st.session_state:
    st.session_state.quick_mode_available = False
if 'quick_mode_enabled' not in st.session_state:
    st.session_state.quick_mode_enabled = False
if 'source_session_id' not in st.session_state:
    st.session_state.source_session_id = None

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
        st.error("⚠️ Cannot connect to the backend API (http://localhost:8000). Please ensure the backend server is running.")
    elif not sessions_list:
        st.info("No previous sessions found.")
    
    if sessions_list:
        def _session_label(s):
            sid = s["session_id"][:8]
            csv = s.get("csv_file") or "no file"
            steps = []
            if s.get("has_report"): steps.append("RG✅")
            elif s.get("has_dashboard"): steps.append("ADC✅")
            elif s.get("has_visualizations"): steps.append("VPE✅")
            elif s.get("has_features"): steps.append("FIE✅")
            elif s.get("has_hypotheses"): steps.append("IHE✅")
            elif s.get("has_findings"): steps.append("EPR✅")
            elif s.get("has_intent"): steps.append("QBII✅")
            elif s.get("has_identity"): steps.append("DPSU✅")
            progress = f" [{', '.join(steps)}]" if steps else ""
            return f"{sid}... | {csv}{progress}"

        options = ["— Select a session —"] + [s["session_id"] for s in sessions_list]
        labels = ["— Select a session —"] + [_session_label(s) for s in sessions_list]

        selected = st.selectbox("Resume existing session", options, format_func=lambda x: labels[options.index(x)])

        if selected != "— Select a session —" and selected != st.session_state.session_id:
            if st.button("Load Session"):
                s_info = next((s for s in sessions_list if s["session_id"] == selected), None)
                st.session_state.session_id = selected
                st.session_state.csv_filename = s_info.get("csv_file") if s_info else None
                st.session_state.intent_confirmed = s_info.get("has_intent", False) if s_info else False
                st.session_state.phase1b_complete = s_info.get("has_findings", False) if s_info else False
                st.session_state.hypotheses_generated = s_info.get("has_hypotheses", False) if s_info else False
                st.session_state.has_features = s_info.get("has_features", False) if s_info else False
                st.session_state.has_visualizations = s_info.get("has_visualizations", False) if s_info else False
                st.session_state.has_dashboard = s_info.get("has_dashboard", False) if s_info else False
                st.session_state.has_report = s_info.get("has_report", False) if s_info else False
                # Reset Quick Mode flags when switching sessions
                st.session_state.quick_mode_available = False
                st.session_state.quick_mode_enabled = False
                st.session_state.source_session_id = None
                # Restore questions state if identity exists but intent not confirmed
                if s_info and s_info.get("has_identity") and not s_info.get("has_intent"):
                    try:
                        gal_resp = requests.get(f"{API_URL}/session/{selected}/gal", timeout=10)
                        if gal_resp.status_code == 200:
                            gal = gal_resp.json()
                            if gal.get("user_intent") and gal["user_intent"].get("generated_questions"):
                                st.session_state.questions = [{"question": q["question"], "question_type": q.get("question_type",""), "why_asked": q.get("why_asked","")} for q in gal["user_intent"]["generated_questions"]]
                    except Exception:
                        pass
                else:
                    st.session_state.questions = []
                st.success(f"Loaded session: {selected[:8]}...")
                st.rerun()

        st.markdown("---")

    if st.button("Initialize New Session"):
        try:
            resp = requests.post(f"{API_URL}/session/create")
            resp.raise_for_status()
            data = resp.json()
            st.session_state.session_id = data["session_id"]
            st.session_state.csv_filename = None
            st.session_state.questions = []
            st.session_state.intent_confirmed = False
            st.session_state.phase1b_complete = False
            st.session_state.hypotheses_generated = False
            st.session_state.has_features = False
            st.session_state.has_visualizations = False
            st.session_state.has_dashboard = False
            st.session_state.has_report = False
            st.session_state.pipeline_status = None
            # Reset Quick Mode flags for a brand new session
            st.session_state.quick_mode_available = False
            st.session_state.quick_mode_enabled = False
            st.session_state.source_session_id = None
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

                    # Reset Quick Mode flags for this session & dataset
                    st.session_state.quick_mode_available = False
                    st.session_state.quick_mode_enabled = False
                    st.session_state.source_session_id = None

                    # Check for Quick Mode availability (same dataset used in a previous completed session)
                    try:
                        check_resp = requests.post(f"{API_URL}/session/{st.session_state.session_id}/check-dataset", timeout=10)
                        if check_resp.status_code == 200:
                            check_data = check_resp.json()
                            if check_data.get("quick_mode_available"):
                                st.session_state.quick_mode_available = True
                                st.session_state.source_session_id = check_data.get("source_session_id")
                    except Exception:
                        pass

                    st.rerun()
                except Exception as e:
                    st.error(f"Upload failed: {str(e)}")

        # Quick Mode toggle (only if dataset was seen before)
        if st.session_state.csv_filename and st.session_state.quick_mode_available:
            st.session_state.quick_mode_enabled = st.checkbox("⚡ Quick Mode", value=st.session_state.quick_mode_enabled, help="Use cached analysis for faster results")

    # --- Phase 1a: Profile + Questions ---
    if st.session_state.csv_filename and not st.session_state.questions:
        st.header("3. Profile & Understand")
        st.markdown("Runs **DPSU** (profiling) + **QBII** (question generation)")
        
        if st.session_state.quick_mode_enabled and st.session_state.source_session_id:
            # --- Quick Mode: simulate the full pipeline ---
            if st.button("Start Quick Analysis"):
                source_sid = st.session_state.source_session_id
                session_id = st.session_state.session_id
                try:
                    resp = requests.post(
                        f"{API_URL}/session/{session_id}/quick-mode",
                        params={"source_session_id": source_sid},
                        stream=True,
                        timeout=180,
                    )
                    resp.raise_for_status()

                    status_container = st.status("Running Quick Mode...", expanded=True)
                    current_agent = ""

                    for line in resp.iter_lines(decode_unicode=True):
                        if not line or not line.startswith("data: "):
                            continue
                        try:
                            event = json.loads(line[6:])
                        except json.JSONDecodeError:
                            continue

                        if event.get("type") == "log":
                            agent = event.get("agent", "SYSTEM")
                            msg = event.get("message", "")
                            log_type = event.get("log_type", "info")
                            if agent != current_agent:
                                current_agent = agent
                            icon = "✅" if log_type == "success" else "🔄"
                            status_container.write(f"{icon} **{agent}**: {msg}")

                        elif event.get("type") == "phase_result":
                            phase = event.get("phase", "")
                            if phase == "phase1a":
                                st.session_state.questions = event.get("questions", [])
                            elif phase == "answers":
                                st.session_state.intent_confirmed = True
                            elif phase == "phase1b":
                                st.session_state.phase1b_complete = True
                            elif phase == "phase2":
                                st.session_state.hypotheses_generated = True
                            elif phase == "fie":
                                st.session_state.has_features = True
                            elif phase == "vpe":
                                st.session_state.has_visualizations = True
                            elif phase == "adc":
                                st.session_state.has_dashboard = True
                            elif phase == "rg":
                                st.session_state.has_report = True
                            status_container.write(f"✅ Phase **{phase}** complete")

                        elif event.get("type") == "done":
                            status_container.update(label="Quick Mode Complete", state="complete")
                            st.success("All phases simulated successfully!")
                            # Set all completed flags
                            st.session_state.questions = st.session_state.questions or [{"question": "simulated"}]
                            st.rerun()

                except requests.exceptions.Timeout:
                    st.error("Quick Mode timed out after 180 seconds.")
                except Exception as e:
                    st.error(f"Quick Mode failed: {str(e)}")
        else:
            # --- Normal pipeline execution ---
            if st.button("Start Analysis"):
                with st.spinner("EVA is profiling your dataset and generating questions..."):
                    try:
                        params = {"csv_file_name": st.session_state.csv_filename, "rules_mode": rules_mode}
                        resp = requests.post(
                            f"{API_URL}/session/{st.session_state.session_id}/execute/phase1a",
                            params=params,
                            timeout=TIMEOUT,
                        )
                        if resp.status_code != 200:
                            try:
                                err = resp.json().get("detail", resp.text)
                            except Exception:
                                err = resp.text
                            st.error(f"Phase 1a Error ({resp.status_code}): {err}")
                        else:
                            data = resp.json()
                            if data.get("error"):
                                st.error(f"Phase 1a Error: {data['error']}")
                            else:
                                st.session_state.questions = data.get("questions", [])
                                st.session_state.pipeline_status = data["status"]
                                st.success("EVA has questions for you!")
                                st.rerun()
                    except requests.exceptions.Timeout:
                        st.error("Phase 1a timed out after 800 seconds.")
                    except Exception as e:
                        st.error(f"Execution failed: {str(e)}")

    # --- QBII: Answer Questions ---
    if st.session_state.questions and not st.session_state.intent_confirmed:
        st.header("4. Answer EVA's Questions")
        st.markdown("EVA needs to understand your analytical goals before proceeding.")
        
        with st.form("qbii_form"):
            answers = {}
            for i, q in enumerate(st.session_state.questions):
                q_type = q.get("question_type", "general")
                badge = {"goal": "🎯", "stakeholder": "👤", "priority": "⚖️", "time": "⏰"}.get(q_type, "❓")
                answers[q["question"]] = st.text_area(
                    f"{badge} {q['question']}",
                    key=f"q_{i}",
                    help=q.get("why_asked", ""),
                    height=68,
                )
            
            submitted = st.form_submit_button("Submit Answers")
            if submitted:
                with st.spinner("EVA is inferring your analytical intent..."):
                    try:
                        resp = requests.post(
                            f"{API_URL}/session/{st.session_state.session_id}/submit-answers",
                            json={"answers": answers},
                            params={"rules_mode": rules_mode},
                            timeout=TIMEOUT,
                        )
                        if resp.status_code != 200:
                            st.error(f"Error: {resp.text}")
                        else:
                            data = resp.json()
                            if data.get("error"):
                                st.error(f"Intent Error: {data['error']}")
                            else:
                                st.session_state.intent_confirmed = True
                                st.success(f"Intent confirmed: **{data.get('primary_objective', 'unknown')}**")
                                st.rerun()
                    except Exception as e:
                        st.error(f"Failed: {str(e)}")

    # --- Phase 1b: Repair + Explore ---
    if st.session_state.intent_confirmed:
        st.header("5. Repair & Explore")
        st.markdown("Runs **DRIL** (data repair via generated script) + **EPR** (pattern recognition)")
        
        if st.button("Execute Repair & Exploration"):
            with st.spinner("EVA is writing and executing analysis scripts..."):
                try:
                    params = {"csv_file_name": st.session_state.csv_filename, "rules_mode": rules_mode}
                    resp = requests.post(
                        f"{API_URL}/session/{st.session_state.session_id}/execute/phase1b",
                        params=params,
                        timeout=TIMEOUT,
                    )
                    if resp.status_code != 200:
                        try:
                            err = resp.json().get("detail", resp.text)
                        except Exception:
                            err = resp.text
                        st.error(f"Phase 1b Error ({resp.status_code}): {err}")
                    else:
                        data = resp.json()
                        if data.get("error"):
                            st.error(f"Phase 1b Error: {data['error']}")
                        else:
                            st.session_state.pipeline_status = data["status"]
                            st.session_state.phase1b_complete = True
                            st.success("Phase 1 Complete!")
                            st.rerun()
                except requests.exceptions.Timeout:
                    st.error("Phase 1b timed out after 400 seconds.")
                except Exception as e:
                    st.error(f"Execution failed: {str(e)}")

    # --- Phase 2: IHE Hypothesis Generation ---
    if st.session_state.phase1b_complete and not st.session_state.hypotheses_generated:
        st.header("6. Investigation & Hypothesis")
        st.markdown("Runs **IHE** — generates real-world explanations for observed patterns.")

        if st.button("Generate Hypotheses"):
            with st.spinner("EVA is reasoning about patterns and generating hypotheses..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/session/{st.session_state.session_id}/execute/phase2",
                        params={"rules_mode": rules_mode},
                        timeout=TIMEOUT,
                    )
                    if resp.status_code != 200:
                        try:
                            err = resp.json().get("detail", resp.text)
                        except Exception:
                            err = resp.text
                        st.error(f"Phase 2 Error ({resp.status_code}): {err}")
                    else:
                        data = resp.json()
                        if data.get("error"):
                            st.error(f"IHE Error: {data['error']}")
                        else:
                            st.session_state.pipeline_status = data["status"]
                            st.session_state.hypotheses_generated = True
                            count = data.get("hypotheses_count", 0)
                            st.success(f"IHE generated {count} hypotheses. Awaiting your review.")
                            st.rerun()
                except requests.exceptions.Timeout:
                    st.error("Phase 2 timed out.")
                except Exception as e:
                    st.error(f"Execution failed: {str(e)}")

    if st.session_state.hypotheses_generated:
        st.header("6. ✅ Hypotheses Generated")
        st.info("Review the hypotheses in the GAL panel → then proceed to visualization.")

    if st.session_state.hypotheses_generated and not st.session_state.has_features:
        st.header("7. 🧠 Feature Intelligence Engine")
        st.markdown("Runs **FIE** — designs domain-specific features based on RAG and hypotheses.")

        if st.button("Generate Feature Engineering Plan"):
            with st.spinner("EVA is researching domain features and creating a feature plan..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/session/{st.session_state.session_id}/execute/fie",
                        params={"rules_mode": rules_mode},
                        timeout=TIMEOUT,
                    )
                    if resp.status_code != 200:
                        try:
                            err = resp.json().get("detail", resp.text)
                        except Exception:
                            err = resp.text
                        st.error(f"FIE Error ({resp.status_code}): {err}")
                    else:
                        data = resp.json()
                        if data.get("error"):
                            st.error(f"FIE Error: {data['error']}")
                        else:
                            st.session_state.pipeline_status = data["status"]
                            st.session_state.has_features = True
                            count = data.get("features_count", 0)
                            st.success(f"FIE generated {count} feature ideas. See the GAL for details.")
                            st.rerun()
                except requests.exceptions.Timeout:
                    st.error("Phase 2b FIE timed out.")
                except Exception as e:
                    st.error(f"Execution failed: {str(e)}")

    if st.session_state.has_features:
        st.header("7. ✅ Features Generated")
        st.info("Review the feature plan in the GAL panel.")

        if st.button("🔄 Regenerate Feature Plan"):
            with st.spinner("EVA is regenerating the feature plan..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/session/{st.session_state.session_id}/execute/fie",
                        params={"rules_mode": rules_mode},
                        timeout=TIMEOUT,
                    )
                    if resp.status_code != 200:
                        try:
                            err = resp.json().get("detail", resp.text)
                        except Exception:
                            err = resp.text
                        st.error(f"FIE Error ({resp.status_code}): {err}")
                    else:
                        data = resp.json()
                        if data.get("error"):
                            st.error(f"FIE Error: {data['error']}")
                        else:
                            st.session_state.pipeline_status = data["status"]
                            st.success("Feature plan regenerated!")
                            st.rerun()
                except requests.exceptions.Timeout:
                    st.error("FIE timed out.")
                except Exception as e:
                    st.error(f"Execution failed: {str(e)}")

        st.markdown("---")
        st.header("8. 📊 Data Visualizer")
        st.markdown("**Visualize Findings** → Go straight to visualizing your findings and hypotheses.")
        st.markdown(f"Run the visualizer in a new terminal:")
        st.code(f"streamlit run Frontend/pages/streamlit_viz.py -- --session_id {st.session_state.session_id}", language="bash")
        viz_url = f"http://localhost:8502?session_id={st.session_state.session_id}"
        st.link_button("📊 Open Data Visualizer", viz_url, type="primary")

        if not st.session_state.has_visualizations:
            st.markdown("Once you have generated visualizations in the new tab, click below to continue:")
            if st.button("Proceed to Dashboard Maker"):
                try:
                    gal_resp = requests.get(f"{API_URL}/session/{st.session_state.session_id}/gal", timeout=10)
                    if gal_resp.status_code == 200:
                        gal_data = gal_resp.json()
                        if gal_data.get("visualization_plan"):
                            st.session_state.has_visualizations = True
                            st.rerun()
                        else:
                            st.warning("Visualizations not found in GAL yet. Please generate them in the Visualizer tab first.")
                except Exception as e:
                    st.error(f"Failed to check GAL status: {e}")

    if st.session_state.has_visualizations and not st.session_state.has_dashboard:
        st.markdown("---")
        st.header("9. 📈 Dashboard Maker")
        st.markdown("Runs **ADC** — Analytical Dashboard Composer to generate KPIs, alerts, and recommendations.")

        if st.button("Generate Dashboard"):
            with st.spinner("EVA is composing the dashboard..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/session/{st.session_state.session_id}/execute/adc",
                        params={"rules_mode": rules_mode},
                        timeout=TIMEOUT,
                    )
                    if resp.status_code != 200:
                        try:
                            err = resp.json().get("detail", resp.text)
                        except Exception:
                            err = resp.text
                        st.error(f"ADC Error ({resp.status_code}): {err}")
                    else:
                        data = resp.json()
                        if data.get("error"):
                            st.error(f"ADC Error: {data['error']}")
                        else:
                            st.session_state.pipeline_status = data["status"]
                            st.session_state.has_dashboard = True
                            st.success(f"Dashboard generated with {data.get('kpis')} KPIs and {data.get('recommendations')} recommendations!")
                            st.rerun()
                except requests.exceptions.Timeout:
                    st.error("ADC timed out.")
                except Exception as e:
                    st.error(f"Execution failed: {str(e)}")

    if st.session_state.has_dashboard:
        st.markdown("---")
        st.header("9. ✅ Dashboard Generated")
        st.info("Review the dashboard metrics in the GAL panel.")
        
        if st.button("🔄 Regenerate Dashboard"):
            with st.spinner("EVA is regenerating the dashboard..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/session/{st.session_state.session_id}/execute/adc",
                        params={"rules_mode": rules_mode},
                        timeout=TIMEOUT,
                    )
                    if resp.status_code != 200:
                        try:
                            err = resp.json().get("detail", resp.text)
                        except Exception:
                            err = resp.text
                        st.error(f"ADC Error ({resp.status_code}): {err}")
                    else:
                        data = resp.json()
                        if data.get("error"):
                            st.error(f"ADC Error: {data['error']}")
                        else:
                            st.session_state.pipeline_status = data["status"]
                            st.success(f"Dashboard regenerated with {data.get('kpis')} KPIs and {data.get('recommendations')} recommendations!")
                            st.rerun()
                except requests.exceptions.Timeout:
                    st.error("ADC timed out.")
                except Exception as e:
                    st.error(f"Execution failed: {str(e)}")

    if st.session_state.has_dashboard and not st.session_state.has_report:
        st.markdown("---")
        st.header("10. 📝 Report Generator")
        st.markdown("Runs **RG** — Report Generator to build a structured narrative of the entire analysis.")

        if st.button("Generate Narrative Report"):
            with st.spinner("EVA is writing the final report..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/session/{st.session_state.session_id}/execute/rg",
                        params={"rules_mode": rules_mode},
                        timeout=TIMEOUT,
                    )
                    if resp.status_code != 200:
                        try:
                            err = resp.json().get("detail", resp.text)
                        except Exception:
                            err = resp.text
                        st.error(f"RG Error ({resp.status_code}): {err}")
                    else:
                        data = resp.json()
                        if data.get("error"):
                            st.error(f"RG Error: {data['error']}")
                        else:
                            st.session_state.pipeline_status = data["status"]
                            st.session_state.has_report = True
                            st.success("Report generated successfully!")
                            st.rerun()
                except requests.exceptions.Timeout:
                    st.error("RG timed out.")
                except Exception as e:
                    st.error(f"Execution failed: {str(e)}")

    if st.session_state.has_report:
        st.markdown("---")
        st.header("10. ✅ Report Generated")
        st.info("Review the final narrative report in the GAL panel.")
        
        if st.button("🔄 Regenerate Report"):
            with st.spinner("EVA is regenerating the narrative report..."):
                try:
                    resp = requests.post(
                        f"{API_URL}/session/{st.session_state.session_id}/execute/rg",
                        params={"rules_mode": rules_mode},
                        timeout=TIMEOUT,
                    )
                    if resp.status_code != 200:
                        try:
                            err = resp.json().get("detail", resp.text)
                        except Exception:
                            err = resp.text
                        st.error(f"RG Error ({resp.status_code}): {err}")
                    else:
                        data = resp.json()
                        if data.get("error"):
                            st.error(f"RG Error: {data['error']}")
                        else:
                            st.session_state.pipeline_status = data["status"]
                            st.success("Report regenerated!")
                            st.rerun()
                except requests.exceptions.Timeout:
                    st.error("RG timed out.")
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
                
                tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(["Overview", "Identity", "Intent", "Integrity", "Findings", "Hypotheses", "Features", "Visualizations", "Dashboard", "Report"])
                
                with tab1:
                    overview = {
                        "session_id": gal_data["session_id"],
                        "created_at": gal_data["created_at"],
                        "current_dataset": gal_data.get("current_dataset_path", "N/A"),
                    }
                    st.json(overview)
                    
                with tab2:
                    if gal_data.get("dataset_identity"):
                        st.json(gal_data["dataset_identity"])
                    else:
                        st.info("No Identity Data Yet")
                        
                with tab3:
                    if gal_data.get("user_intent"):
                        intent = gal_data["user_intent"]
                        if intent.get("primary_objective") == "pending_user_input":
                            st.warning("Waiting for your answers to the questions on the left.")
                            if intent.get("generated_questions"):
                                st.markdown("**Generated Questions:**")
                                for q in intent["generated_questions"]:
                                    st.markdown(f"- {q['question']}")
                        else:
                            st.json(intent)
                    else:
                        st.info("No Intent Data Yet")
                        
                with tab4:
                    if gal_data.get("data_integrity"):
                        integrity = gal_data["data_integrity"]
                        # Show script execution info prominently
                        if integrity.get("script_execution"):
                            se = integrity["script_execution"]
                            status_icon = "✅" if se.get("success") else "❌"
                            st.markdown(f"**Script Execution:** {status_icon}")
                            st.code(se.get("script_path", "N/A"), language="text")
                            if se.get("stdout"):
                                with st.expander("Script Output"):
                                    st.code(se["stdout"], language="text")
                            if se.get("stderr") and not se.get("success"):
                                with st.expander("Script Errors"):
                                    st.code(se["stderr"], language="text")
                        st.json(integrity.get("modifications", []))
                    else:
                        st.info("No Integrity Data Yet")
                        
                with tab5:
                    if gal_data.get("exploratory_findings"):
                        findings = gal_data["exploratory_findings"]
                        if findings.get("script_execution"):
                            se = findings["script_execution"]
                            status_icon = "✅" if se.get("success") else "❌"
                            st.markdown(f"**Script Execution:** {status_icon}")
                            st.code(se.get("script_path", "N/A"), language="text")
                            if se.get("stdout"):
                                with st.expander("Script Output"):
                                    st.code(se["stdout"], language="text")
                        st.json({
                            "anomalies": findings.get("anomalies", []),
                            "target_associations": findings.get("target_associations", {}),
                        })
                    else:
                        st.info("No Exploratory Data Yet")

                with tab6:
                    if gal_data.get("hypotheses"):
                        hyp_data = gal_data["hypotheses"]
                        st.markdown(f"**Significant findings analyzed:** {hyp_data.get('significant_findings_count', 0)} | "
                                    f"**Skipped:** {hyp_data.get('skipped_findings_count', 0)}")
                        if hyp_data.get("overall_reasoning"):
                            st.markdown(f"_{hyp_data['overall_reasoning']}_")
                        st.markdown("---")
                        for i, h in enumerate(hyp_data.get("hypotheses", [])):
                            plaus = h.get("plausibility", "Unknown")
                            badge = {"High": "🟢", "Moderate": "🟡", "Low": "🔴"}.get(plaus, "⚪")
                            st.markdown(f"### {badge} Hypothesis {i+1}: {plaus} Plausibility")
                            st.markdown(f"**Observation:** {h.get('observation_plain_language', h.get('observation_ref', 'N/A'))}")
                            st.markdown(f"**Proposed Mechanism:** {h.get('hypothesis', 'N/A')}")
                            with st.expander("Evidence Details"):
                                st.markdown("**Supporting:**")
                                for ev in (h.get("supporting_evidence") or []):
                                    st.markdown(f"  - ✅ {ev}")
                                st.markdown("**Contradicting:**")
                                for ev in (h.get("contradicting_evidence") or []):
                                    st.markdown(f"  - ❌ {ev}")
                                st.markdown("**Missing:**")
                                for ev in (h.get("missing_evidence") or []):
                                    st.markdown(f"  - ❓ {ev}")
                            if h.get("reasoning"):
                                st.caption(f"Reasoning: {h['reasoning']}")
                            if h.get("confidence_note"):
                                st.caption(f"⚠️ {h['confidence_note']}")
                            st.markdown("---")
                    else:
                        st.info("No Hypotheses Generated Yet")

                with tab7:
                    if gal_data.get("feature_plan"):
                        feat_data = gal_data["feature_plan"]
                        if feat_data.get("overall_reasoning"):
                            st.markdown(f"**Overall Reasoning:**\n_{feat_data['overall_reasoning']}_")
                        
                        st.markdown("---")
                        
                        for i, f in enumerate(feat_data.get("features", [])):
                            st.markdown(f"### 💡 Feature {i+1}: `{f.get('name', 'N/A')}`")
                            st.markdown(f"**Business Meaning:** {f.get('business_meaning', 'N/A')}")
                            st.code(f.get('formula', 'N/A'), language="text")
                            
                            cols = st.columns(2)
                            cols[0].markdown(f"**Type:** {f.get('type', 'N/A')}")
                            cols[1].markdown(f"**Expected ML Impact:** {f.get('expected_ml_impact', 'N/A')}")
                            
                            with st.expander("Why it Matters"):
                                st.markdown(f"{f.get('why_it_matters', 'N/A')}")
                            st.markdown("---")
                    else:
                        st.info("No Features Engineered Yet")

                with tab8:
                    if gal_data.get("visualization_plan"):
                        viz_data = gal_data["visualization_plan"]
                        st.markdown(f"**Rendered:** {viz_data.get('total_rendered', 0)} | "
                                    f"**Failed:** {viz_data.get('total_failed', 0)}")
                        if viz_data.get("overall_reasoning"):
                            st.markdown(f"_{viz_data['overall_reasoning']}_")
                        st.markdown("---")
                        for i, v in enumerate(viz_data.get("visualizations", [])):
                            status_icon = "✅" if v.get("validation_result") == "passed" else "❌"
                            st.markdown(f"### {status_icon} Chart {i+1}: {v.get('chart_type', '?').title()}")
                            st.markdown(f"**Question:** {v.get('question', 'N/A')}")
                            st.markdown(f"**Interpretation:** {v.get('interpretation', 'N/A')}")
                            if v.get("confidence_note"):
                                st.caption(f"⚠️ {v['confidence_note']}")
                            st.markdown("---")
                    else:
                        st.info("No Visualizations Generated Yet")
                        
                with tab9:
                    if gal_data.get("dashboard_plan"):
                        db_data = gal_data["dashboard_plan"]
                        if db_data.get("overall_reasoning"):
                            st.markdown(f"_{db_data['overall_reasoning']}_")
                        st.markdown(f"**Stakeholder Calibration:** {db_data.get('stakeholder_calibration', 'N/A')}")
                        st.markdown("---")

                        st.subheader("📊 KPIs")
                        for kpi in db_data.get("kpis", []):
                            st.markdown(f"**{kpi.get('name')}**: {kpi.get('value')} _(Source: {kpi.get('derivation_source')})_")
                            st.caption(f"Reasoning: {kpi.get('justification')}")

                        st.markdown("---")
                        st.subheader("🚨 Alerts")
                        for alert in db_data.get("alerts", []):
                            alert_type = alert.get("alert_type", "Info")
                            icon = "🔴" if alert_type == "Critical" else ("🟡" if alert_type == "Warning" else "🔵")
                            st.markdown(f"{icon} **{alert_type}**: {alert.get('description')}")
                            st.caption(f"Ref: {alert.get('evidence_ref')} | Confidence: {alert.get('confidence')}")

                        st.markdown("---")
                        st.subheader("💡 Recommendations")
                        for rec in db_data.get("recommendations", []):
                            st.markdown(f"**Action:** {rec.get('action')}")
                            st.markdown(f"- **Target:** {rec.get('target_group')} | **Impact:** {rec.get('expected_impact')} | **Urgency:** {rec.get('urgency')}")
                            st.caption(f"Based on: {rec.get('supporting_evidence_ref')} & {rec.get('supporting_hypothesis_ref')}")
                            st.markdown("---")
                    else:
                        st.info("No Dashboard Plan Generated Yet")

                with tab10:
                    if gal_data.get("report_memory"):
                        rm_data = gal_data["report_memory"]
                        st.markdown(f"**Stakeholder Calibration:** {rm_data.get('stakeholder_calibration', 'N/A')}")
                        st.markdown(f"**Recorded at:** {rm_data.get('recorded_at', 'N/A')}")
                        st.markdown("---")
                        
                        st.subheader("Narrative Report")
                        st.markdown(rm_data.get("narrative", "No narrative generated."))
                        
                        st.markdown("---")
                        st.subheader("Citations")
                        for i, citation in enumerate(rm_data.get("citations", [])):
                            st.markdown(f"**[{i+1}]** {citation.get('reference', 'N/A')} - {citation.get('context', 'N/A')}")
                        
                        st.markdown("---")
                        st.subheader("Included Visualizations")
                        for viz in rm_data.get("included_visualizations", []):
                            st.markdown(f"- **{viz.get('chart_title', 'N/A')}** ({viz.get('chart_type', 'N/A')}): {viz.get('purpose_in_report', 'N/A')}")
                            
                        st.markdown("---")
                        st.subheader("Communicated Recommendations")
                        for rec in rm_data.get("communicated_recommendations", []):
                            st.markdown(f"- **Action:** {rec.get('action', 'N/A')}")
                            st.markdown(f"  **Target:** {rec.get('target_audience', 'N/A')}")
                            if rec.get("expected_impact"):
                                st.caption(f"Impact: {rec['expected_impact']}")
                    else:
                        st.info("No Narrative Report Generated Yet")
                        
            except Exception as e:
                st.error("Failed to read GAL (it may not be initialized).")
    else:
        st.info("Create a session to view the GAL.")

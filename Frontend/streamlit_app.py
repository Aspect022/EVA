import streamlit as st
import requests
import json

# Configuration
API_URL = "http://localhost:8000"

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

# --- UI Layout ---
col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Session Setup")

    # --- Resume existing session ---
    try:
        sessions_resp = requests.get(f"{API_URL}/session/list", timeout=5)
        sessions_list = sessions_resp.json() if sessions_resp.status_code == 200 else []
    except Exception:
        sessions_list = []

    if sessions_list:
        def _session_label(s):
            sid = s["session_id"][:8]
            csv = s.get("csv_file") or "no file"
            steps = []
            if s.get("has_hypotheses"): steps.append("IHE✅")
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
            st.session_state.pipeline_status = None
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

    # --- Phase 1a: Profile + Questions ---
    if st.session_state.csv_filename and not st.session_state.questions:
        st.header("3. Profile & Understand")
        st.markdown("Runs **DPSU** (profiling) + **QBII** (question generation)")
        
        if st.button("Start Analysis"):
            with st.spinner("EVA is profiling your dataset and generating questions..."):
                try:
                    params = {"csv_file_name": st.session_state.csv_filename, "rules_mode": rules_mode}
                    resp = requests.post(
                        f"{API_URL}/session/{st.session_state.session_id}/execute/phase1a",
                        params=params,
                        timeout=800,
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
                            timeout=800,
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
                        timeout=800,
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
                        timeout=800,
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
        st.info("Review the hypotheses in the GAL panel →  then approve to proceed to Feature Engineering.")

with col2:
    st.header("Global Analysis Ledger (GAL)")
    
    if st.session_state.session_id:
        if st.button("Refresh GAL State"):
            try:
                resp = requests.get(f"{API_URL}/session/{st.session_state.session_id}/gal")
                resp.raise_for_status()
                gal_data = resp.json()
                
                tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Overview", "Identity", "Intent", "Integrity", "Findings", "Hypotheses"])
                
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
                        
            except Exception as e:
                st.error("Failed to read GAL (it may not be initialized).")
    else:
        st.info("Create a session to view the GAL.")

import streamlit as st
import requests
import json
import plotly.graph_objects as go

API_URL = "http://localhost:8000"

st.set_page_config(page_title="EVA — Data Visualizer", layout="wide")

st.title("📊 EVA: Data Visualizer")
st.markdown("### Visualization Planner & Executor")

# --- Session selection ---
session_id = st.query_params.get("session_id", None)

if not session_id:
    st.warning("No session ID provided. Go back to the main app and click 'Open Data Visualizer'.")
    st.stop()

st.caption(f"Session: `{session_id[:12]}...`")

# --- Rules mode ---
rules_mode = st.radio(
    "Rules Mode",
    ["full", "lite"],
    format_func=lambda x: "🔥 Full" if x == "full" else "⚡ Lite",
    horizontal=True,
)

# --- Check if visualizations already exist ---
try:
    gal_resp = requests.get(f"{API_URL}/session/{session_id}/gal", timeout=10)
    gal_resp.raise_for_status()
    gal_data = gal_resp.json()
except Exception as e:
    st.error(f"Failed to load GAL: {e}")
    st.stop()

has_hypotheses = gal_data.get("hypotheses") is not None
has_viz = gal_data.get("visualization_plan") is not None

if not has_hypotheses:
    st.error("❌ Hypotheses not generated yet. Complete Phase 2 (IHE) in the main app first.")
    st.stop()


# --- Generate Visualizations ---
col_gen, col_status = st.columns([1, 2])

with col_gen:
    if st.button("🎨 Generate Visualizations", type="primary", use_container_width=True):
        with st.spinner("EVA is planning and rendering visualizations... This may take a minute."):
            try:
                resp = requests.post(
                    f"{API_URL}/session/{session_id}/execute/vpe",
                    params={"rules_mode": rules_mode},
                    timeout=800,
                )
                if resp.status_code != 200:
                    try:
                        err = resp.json().get("detail", resp.text)
                    except Exception:
                        err = resp.text
                    st.error(f"VPE Error ({resp.status_code}): {err}")
                else:
                    data = resp.json()
                    if data.get("error"):
                        st.error(f"VPE Error: {data['error']}")
                    else:
                        st.success(f"✅ Generated {data.get('visualizations_count', 0)} visualizations!")
                        st.rerun()
            except requests.exceptions.Timeout:
                st.error("VPE timed out.")
            except Exception as e:
                st.error(f"Execution failed: {str(e)}")

with col_status:
    if has_viz:
        viz_plan = gal_data["visualization_plan"]
        rendered = viz_plan.get("total_rendered", 0)
        failed = viz_plan.get("total_failed", 0)
        st.metric("Charts Rendered", rendered)
        if failed > 0:
            st.caption(f"⚠️ {failed} chart(s) failed validation")
    else:
        st.info("Click 'Generate Visualizations' to create charts from your analysis findings.")


# --- Display Visualizations ---
if has_viz:
    viz_plan = gal_data["visualization_plan"]

    if viz_plan.get("overall_reasoning"):
        st.markdown(f"**Strategy:** _{viz_plan['overall_reasoning']}_")

    st.markdown("---")

    visualizations = viz_plan.get("visualizations", [])
    passed_vizs = [v for v in visualizations if v.get("validation_result") == "passed"]
    failed_vizs = [v for v in visualizations if v.get("validation_result") != "passed"]

    if not passed_vizs:
        st.warning("No visualizations passed validation. Try regenerating with different data.")
    else:
        # Render charts in a 2-column grid
        for i in range(0, len(passed_vizs), 2):
            cols = st.columns(2)

            for j, col in enumerate(cols):
                idx = i + j
                if idx >= len(passed_vizs):
                    break

                viz = passed_vizs[idx]
                with col:
                    # Chart title (the question it answers)
                    st.markdown(f"#### 📈 {viz.get('question', 'Untitled Chart')}")

                    # Render the Plotly chart
                    plotly_config = viz.get("plotly_config")
                    if plotly_config and isinstance(plotly_config, dict) and "data" in plotly_config:
                        try:
                            fig = go.Figure(plotly_config)
                            fig.update_layout(
                                template="plotly_dark",
                                height=400,
                                margin=dict(l=40, r=40, t=50, b=40),
                            )
                            st.plotly_chart(fig, use_container_width=True, key=f"chart_{idx}")
                        except Exception as e:
                            st.error(f"Chart render error: {e}")
                    else:
                        st.warning("Chart data unavailable for this visualization.")

                    # Interpretation
                    if viz.get("interpretation"):
                        st.markdown(f"💡 **Insight:** {viz['interpretation']}")

                    # Confidence note
                    if viz.get("confidence_note"):
                        st.caption(f"⚠️ {viz['confidence_note']}")

                    # Expandable details
                    with st.expander("Details"):
                        st.markdown(f"**Chart Type:** {viz.get('chart_type', 'N/A')} — {viz.get('chart_type_reasoning', '')}")
                        st.markdown(f"**Related Finding:** {viz.get('related_finding', 'N/A')}")
                        st.markdown(f"**Variables:** {', '.join(viz.get('variables_used', [])) if isinstance(viz.get('variables_used'), list) else viz.get('variables_used', 'N/A')}")
                        st.markdown(f"**Audience:** {viz.get('audience_calibration', 'general')}")

                    st.markdown("---")

    # Show failed visualizations
    if failed_vizs:
        with st.expander(f"⚠️ {len(failed_vizs)} Visualization(s) Failed Validation"):
            for fv in failed_vizs:
                st.markdown(f"- **{fv.get('question', 'Unknown')}** — {fv.get('chart_type', '?')} chart")
                if fv.get("confidence_note"):
                    st.caption(f"  Reason: {fv['confidence_note']}")

    # GAL Section 7 raw data
    with st.expander("📋 Raw GAL Section 7 Data"):
        st.json(viz_plan)

else:
    st.markdown("---")
    st.info("👆 Generate visualizations to see your data come alive!")

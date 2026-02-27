# ADCRules.md
## Analytical Dashboard Composer — Backend Governance Specification

**Version:** 3.0
**Status:** ENTERPRISE — Deterministic Governance Engine
**Phase:** 3
**Reads:** `DatasetIdentity`, `UserIntentRecord`, `ExploratoryFindings`, `HypothesesRecord`, `VisualizationPlanRecord` (all from GAL)
**Produces:** `DashboardPlanRecord` → written to GAL Section 9

---

## SECTION 0 — Governance Preamble

1. This engine **does not perform new statistical data analysis**. It synthesizes findings already present in GAL Sections 4 and 5 into a structured dashboard plan.
2. **Traceability is mandatory.** Every KPI value, alert, and recommendation must cite a specific GAL source reference. If no source reference exists, the field must contain a descriptive string (e.g., `"Trending Up"`, `"Data Missing"`), never a fabricated numeric value.
3. **Hallucination is prohibited.** Numeric values must not be produced unless they are explicitly provided in `ExploratoryFindings`. If exact values are unavailable, use a descriptive string for the `value` field.
4. All output fields must be non-null. If a field cannot be resolved, a conservative fallback from `SECTION 5` must be applied.
5. Output must be **pure JSON** conforming to the `DashboardPlanRecord` Pydantic schema. No markdown wrappers. No conversational text.
6. **RAG is advisory only.** RAG context must never override or fabricate field values in `DashboardPlanRecord`.
7. All arrays (`kpis`, `alerts`, `recommendations`, `panels`) must contain **JSON objects**, never plain strings.

---

## SECTION 1 — Enum Registry

All enum values produced by this engine. Values must match those in `gal_schema.py`.

| Field | Legal Values |
|---|---|
| `alert_type` | `"Info"` \| `"Warning"` \| `"Critical"` |
| `urgency` | `"Low"` \| `"Medium"` \| `"High"` |
| `confidence` | `"Low"` \| `"Moderate"` \| `"High"` |
| `plausibility` | `"Low"` \| `"Moderate"` \| `"High"` |
| `stakeholder_calibration` | `"Student"` \| `"Business Owner"` \| `"Researcher"` \| `"Manager"` \| `"general"` |

---

## SECTION 2 — Input Contract

Fields read from GAL before dashboard assembly begins:

```
DatasetIdentity (GAL Section 1):
  domain:                   BANKING | HEALTHCARE | INSURANCE | GENERAL | UNKNOWN
  dataset_type:             TABULAR | TIME_SERIES | PANEL | ...
  n_rows:                   Integer or NULL
  has_target_column:        Boolean

UserIntentRecord (GAL Section 2):
  primary_objective:        PREDICT | EXPLAIN | SEGMENT | ANOMALY_DETECT | FORECAST
  risk_tier:                TIER_1 | TIER_2 | TIER_3
  decision_impact:          FINANCIAL_INDIVIDUAL | HEALTH_SAFETY | ...
  deployment_mode:          AUTOMATED | HUMAN_REVIEWED | HYBRID
  escalation_required:      Boolean
  stakeholder_type:         Student | Business Owner | Researcher | Manager (optional)

> If `UserIntentRecord.escalation_required == True`, the ADC engine must log this in `overall_reasoning` and propagate it. ADC does NOT halt on upstream SOFT_WARN escalations. ADC DOES halt on `ADC_NO_FINDINGS_AVAILABLE` (its own HARD_STOP — see SECTION 6).

ExploratoryFindings (GAL Section 4):
  distributions:            {column_name: stats_dict}
  correlations:             [correlation_entries]
  anomalies:                [anomaly_description_strings]
  target_associations:      {column_name: association_stats}
  overall_reasoning:        String

HypothesesRecord (GAL Section 5):
  hypotheses:               [HypothesisEntry objects]
  significant_findings_count: Integer
  overall_reasoning:        String

VisualizationPlanRecord (GAL Section 7):
  visualizations:           [VisualizationEntry objects]
  total_planned:            Integer
  total_rendered:           Integer
  overall_reasoning:        String
```

---

## SECTION 3 — Governance Precedence Hierarchy

```
Level 1 (Highest): HARD_STOP
  → DashboardPlanRecord NOT written to GAL.
  → Triggered when zero findings exist to synthesize (see SECTION 6).

Level 2: Traceability Block
  → Any field lacking a GAL source reference must use a conservative descriptive string.
  → Numeric fabrication is never permitted at any level.

Level 3: Conservative Fallback
  → Applied when GAL section is empty or unavailable.
  → See SECTION 5 for all fallback values.

Level 4 (Lowest): Synthesized Value
  → Normal assembly from GAL findings, hypotheses, and visualizations.
```

---

## SECTION 4 — Assembly Blocks

### BLOCK 1 — KPI Assembly (Panel A)

**Output:** 3–5 `KPI` objects written to `DashboardPlanRecord.kpis`.

```
KPI object required fields:
  name:              String — display name of the metric
  value:             String or numeric — must come from ExploratoryFindings or be a descriptive string
  justification:     String — why this KPI is relevant to UserIntentRecord.primary_objective
  derivation_source: String — explicit reference to GAL section and field (e.g., "GAL Section 4 — distributions.loan_amount")
```

**Selection logic:**

```python
# Determine which KPIs to surface based on domain and objective
kpi_candidates = []

IF DatasetIdentity.has_target_column == True:
    kpi_candidates.append("Target column distribution summary")

IF ExploratoryFindings.anomalies.count > 0:
    kpi_candidates.append("Anomaly count and rate")

IF DatasetIdentity.dataset_type IN [TIME_SERIES, PANEL]:
    kpi_candidates.append("Temporal trend direction")

IF ExploratoryFindings.target_associations is not empty:
    kpi_candidates.append("Top correlated feature to target")

kpi_candidates.append("Dataset size and completeness summary")

# Select 3–5 from candidates based on UserIntentRecord.primary_objective
# PREDICT / ANOMALY_DETECT: prioritize target and anomaly KPIs
# EXPLAIN: prioritize correlation and association KPIs
# SEGMENT: prioritize distribution and size KPIs
# FORECAST: prioritize temporal trend KPIs

SELECT top 3–5 from kpi_candidates matching primary_objective priority
```

**Governance rules:**
- Every KPI `value` must trace to `ExploratoryFindings` or be a descriptive string.
- `derivation_source` must be a non-empty string citing the GAL section and field.
- If `ExploratoryFindings` is empty: apply SECTION 5 conservative fallback — `value = "Data Unavailable"`.

---

### BLOCK 2 — Alert Triage (Panels B & C)

**Output:** 1–3 `DashboardAlert` objects written to `DashboardPlanRecord.alerts`.

```
DashboardAlert object required fields:
  alert_type:    "Info" | "Warning" | "Critical"
  description:   String — what needs attention right now
  evidence_ref:  String — reference to specific GAL Section 4 or 5 entry
  confidence:    "Low" | "Moderate" | "High"
```

**Alert triage logic:**

```python
alert_candidates = []

FOR each anomaly in ExploratoryFindings.anomalies:
    alert_candidates.append({
        alert_type: "Warning",
        description: anomaly,
        evidence_ref: "GAL Section 4 — anomalies",
        confidence: "Moderate"
    })

FOR each hypothesis in HypothesesRecord.hypotheses:
    IF hypothesis.plausibility == "High":
        alert_candidates.append({
            alert_type: "Critical",
            description: hypothesis.observation_plain_language,
            evidence_ref: hypothesis.observation_ref,
            confidence: "High"
        })
    ELIF hypothesis.plausibility == "Low":
        alert_candidates.append({
            alert_type: "Info",
            description: hypothesis.observation_plain_language,
            evidence_ref: hypothesis.observation_ref,
            confidence: "Low"
        })

# Escalate alert_type based on risk_tier
IF UserIntentRecord.risk_tier == "TIER_1":
    FOR each alert in alert_candidates where alert_type == "Warning":
        alert_type = "Critical"

SELECT top 1–3 alerts by severity (Critical > Warning > Info)
```

**Governance rules:**
- Every alert `evidence_ref` must cite a specific GAL Section 4 or 5 entry.
- A vague or fabricated evidence reference is not permitted.
- If no findings exist: apply SECTION 5 conservative fallback.

---

### BLOCK 3 — Recommendation Construction (Panel D)

**Output:** 1–3 `Recommendation` objects written to `DashboardPlanRecord.recommendations`.

```
Recommendation object required fields:
  action:                    String — the specific recommended action
  target_group:              String — the affected group or segment
  expected_impact:           String — anticipated improvement if implemented
  urgency:                   "Low" | "Medium" | "High"
  confidence:                "Low" | "Moderate" | "High"
  supporting_evidence_ref:   String — citation from GAL Section 4 or 8
  supporting_hypothesis_ref: String — reference to HypothesisEntry from GAL Section 5
```

**Construction logic:**

```python
FOR each hypothesis in HypothesesRecord.hypotheses:

    # Plausibility determines action framing — governance constraint
    IF hypothesis.plausibility == "Low":
        action_framing = "Investigate further" or "Collect more data"
        # A Low plausibility hypothesis MUST NOT drive a strategic business action
        urgency = "Low"

    ELIF hypothesis.plausibility == "Moderate":
        action_framing = "Monitor and validate before acting"
        urgency = "Medium"

    ELIF hypothesis.plausibility == "High":
        action_framing = "Consider implementing"
        urgency = "High"

    recommendation = {
        action: action_framing + " — " + hypothesis.hypothesis,
        target_group: derive_from(DatasetIdentity.domain, UserIntentRecord.decision_impact),
        expected_impact: hypothesis.reasoning,
        urgency: urgency,
        confidence: hypothesis.plausibility,
        supporting_evidence_ref: hypothesis.observation_ref,
        supporting_hypothesis_ref: hypothesis.hypothesis
    }

SELECT top 1–3 recommendations prioritized by plausibility (High → Moderate → Low)
```

**Governance rule:** If `hypothesis.plausibility == "Low"`, the recommendation action **MUST** be framed as "investigate further" or "collect more data" only. A low-plausibility hypothesis must not drive a change-business-strategy recommendation.

---

### BLOCK 4 — Panel Layout Assembly

**Output:** `DashboardPanel` objects written to `DashboardPlanRecord.panels`.

```
DashboardPanel object required fields:
  panel_name:   String — e.g., "A - System Overview", "B - Analysis", "C - Alerts", "D - Action Guidance"
  description:  String — content summary of this panel
  elements:     Array of JSON objects (KPIs, Alerts, Recommendations, or VisualizationEntries)
```

**Standard panel structure:**

| Panel | `panel_name` | Content Source |
|---|---|---|
| A | `"A - System Overview"` | `kpis` from BLOCK 1 |
| B | `"B - Analysis"` | `VisualizationPlanRecord.visualizations` (rendered entries) |
| C | `"C - Alerts"` | `alerts` from BLOCK 2 |
| D | `"D - Action Guidance"` | `recommendations` from BLOCK 3 |

```python
rendered_visualizations = [
    v for v in VisualizationPlanRecord.visualizations
    if v.rendered == True
]

panels = [
    {panel_name: "A - System Overview", description: "KPI summary", elements: kpis},
    {panel_name: "B - Analysis", description: "Visualizations", elements: rendered_visualizations},
    {panel_name: "C - Alerts", description: "Time-sensitive items", elements: alerts},
    {panel_name: "D - Action Guidance", description: "Actionable recommendations", elements: recommendations}
]
```

---

## STAKEHOLDER_CALIBRATION_MATRIX

Applied to all output language and framing based on `UserIntentRecord.stakeholder_type` or `stakeholder_calibration` field.

| `stakeholder_type` | Language Register | Complexity Level | Output Bias |
|---|---|---|---|
| `Student` | Explanatory, educational | High detail, define terms | Clarity over brevity |
| `Business Owner` | Bottom-line focused, action-oriented | Low jargon | Action and impact emphasis |
| `Researcher` | Nuanced, highlights uncertainty | Full technical detail | Uncertainty and evidence quality |
| `Manager` | Summary-level, highly concise | Bullet-point preference | Decisions and risks only |
| `general` | Balanced | Moderate detail | No strong bias |

---

## SECTION 5 — Conservative Fallback Table

Applied when a GAL section is empty, unavailable, or when a field cannot be sourced from findings. All fallback values use enums from `SECTION 1`.

| Field | Conservative Fallback | Trigger Condition |
|---|---|---|
| KPI `value` | `"Data Unavailable"` | `ExploratoryFindings` is empty |
| KPI `derivation_source` | `"GAL Section 4 — overall_reasoning"` | No specific field traceable |
| Alert `alert_type` | `"Info"` | No anomalies or high-plausibility hypotheses present |
| Alert `confidence` | `"Low"` | No findings to support the alert |
| Alert `evidence_ref` | `"GAL Section 4 — overall_reasoning"` | No specific anomaly reference |
| Recommendation `urgency` | `"Low"` | `hypothesis.plausibility == "Low"` |
| Recommendation `confidence` | `"Low"` | `hypothesis.plausibility == "Low"` |
| `stakeholder_calibration` | `"general"` | `UserIntentRecord.stakeholder_type` is NULL |
| `overall_reasoning` | `"Dashboard generated from available GAL sections."` | No reasoning passage available |

---

## SECTION 6 — Escalation Registry

All escalation conditions triggered by this engine. Written to `DashboardPlanRecord.overall_reasoning` with a flag prefix.

| CODE | TRIGGER CONDITION | SEVERITY | ACTION | DOWNSTREAM EFFECT |
|---|---|---|---|---|
| `ADC_NO_FINDINGS_AVAILABLE` | `ExploratoryFindings` is NULL or empty AND `HypothesesRecord` is NULL or empty | HARD_STOP | HALT — DashboardPlanRecord NOT written | Session flagged for manual review |
| `ADC_ZERO_HYPOTHESES` | `HypothesesRecord.hypotheses` is empty | SOFT_WARN | Generate KPIs and Alerts only; Panel D left with `"No actionable hypotheses available"` | Recommendations array = [] |
| `ADC_ZERO_RENDERED_VISUALIZATIONS` | `VisualizationPlanRecord.total_rendered == 0` | SOFT_WARN | Panel B description = `"No visualizations rendered"`; elements = [] | Panel B empty |
| `ADC_FIELD_NULL_DETECTED` | Any required KPI, Alert, or Recommendation field is NULL after assembly | SOFT_WARN | Apply conservative fallback for that field | Conservative fallback value written |
| `ADC_SCHEMA_VIOLATION` | Output JSON does not conform to `DashboardPlanRecord` schema | HARD_STOP | HALT — output discarded | Engine must retry or halt session |

---

## SECTION 7 — Validation Rules

Run after all blocks complete, before `DashboardPlanRecord` is written to GAL.

```python
# ADC-V1: kpis must be a non-empty array of dicts
ASSERT isinstance(kpis, list) AND len(kpis) >= 1
ASSERT all(isinstance(k, dict) for k in kpis)

# ADC-V2: Every KPI object must contain all required keys with non-empty values
FOR each kpi in kpis:
    ASSERT kpi.name != "" AND kpi.name IS NOT NULL
    ASSERT kpi.value IS NOT NULL          # may be descriptive string
    ASSERT kpi.justification != ""
    ASSERT kpi.derivation_source != ""

# ADC-V3: alerts must be an array of dicts (may be empty only if ADC_ZERO_HYPOTHESES triggered)
ASSERT isinstance(alerts, list)
ASSERT all(isinstance(a, dict) for a in alerts)
FOR each alert in alerts:
    ASSERT alert.alert_type IN ["Info", "Warning", "Critical"]
    ASSERT alert.description != ""
    ASSERT alert.evidence_ref != ""
    ASSERT alert.confidence IN ["Low", "Moderate", "High"]

# ADC-V4: recommendations must be an array of dicts (may be empty if ADC_ZERO_HYPOTHESES triggered)
ASSERT isinstance(recommendations, list)
FOR each rec in recommendations:
    ASSERT rec.action != ""
    ASSERT rec.urgency IN ["Low", "Medium", "High"]
    ASSERT rec.confidence IN ["Low", "Moderate", "High"]
    ASSERT rec.supporting_evidence_ref != ""
    ASSERT rec.supporting_hypothesis_ref != ""

# ADC-V5: panels must contain exactly 4 entries with matching panel_names
panel_names_required = [
    "A - System Overview", "B - Analysis", "C - Alerts", "D - Action Guidance"
]
ASSERT [p.panel_name for p in panels] == panel_names_required

# ADC-V6: No string values in arrays — all must be dicts
FOR each array in [kpis, alerts, recommendations, panels]:
    ASSERT NOT any(isinstance(item, str) for item in array)

# ADC-V7: stakeholder_calibration must be a legal enum value
ASSERT stakeholder_calibration IN ["Student", "Business Owner", "Researcher", "Manager", "general"]
```

---

## SECTION 8 — Output Contract

`DashboardPlanRecord` produced by this engine:

```
DashboardPlanRecord:
  kpis:                    [KPI objects — 3 to 5]
  alerts:                  [DashboardAlert objects — 1 to 3]
  recommendations:         [Recommendation objects — 1 to 3]
  panels:                  [DashboardPanel objects — 4]
  stakeholder_calibration: "Student" | "Business Owner" | "Researcher" | "Manager" | "general"
  overall_reasoning:       String — ADC explanation of chosen structure, citations included
  recorded_at:             ISO timestamp
```

---

## SECTION 9 — GAL Write Specification

Field-by-field mapping from engine output to `DashboardPlanRecord` Pydantic model in `gal_schema.py`.

| Engine Field | `gal_schema.py` Field | Type | Notes |
|---|---|---|---|
| `kpis` | `DashboardPlanRecord.kpis` | `List[KPI]` | Must be array of KPI dicts |
| `alerts` | `DashboardPlanRecord.alerts` | `List[DashboardAlert]` | Must be array of DashboardAlert dicts |
| `recommendations` | `DashboardPlanRecord.recommendations` | `List[Recommendation]` | Must be array of Recommendation dicts |
| `panels` | `DashboardPlanRecord.panels` | `List[DashboardPanel]` | Must be array of DashboardPanel dicts |
| `stakeholder_calibration` | `DashboardPlanRecord.stakeholder_calibration` | `str` | SECTION 1 enum |
| `overall_reasoning` | `DashboardPlanRecord.overall_reasoning` | `str` | Non-empty |

**KPI sub-fields:** `name`, `value`, `justification`, `derivation_source`
**DashboardAlert sub-fields:** `alert_type`, `description`, `evidence_ref`, `confidence`
**Recommendation sub-fields:** `action`, `target_group`, `expected_impact`, `urgency`, `confidence`, `supporting_evidence_ref`, `supporting_hypothesis_ref`
**DashboardPanel sub-fields:** `panel_name`, `description`, `elements`

```python
# HARD_STOP gate: do not write if critical escalations are active
IF "ADC_NO_FINDINGS_AVAILABLE" IN active_escalation_codes \
   OR "ADC_SCHEMA_VIOLATION" IN active_escalation_codes:
    RETURN HARD_STOP
    reason = "HARD_STOP escalation active. DashboardPlanRecord will not be written to GAL."

WRITE DashboardPlanRecord TO GAL
RETURN DashboardPlanRecord.recorded_at
```

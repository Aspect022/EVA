import type { VisualizationsData, DashboardData, ReportData } from "./api-client"

export const titanicQuestions: Array<Record<string, unknown>> = [
  {
    question: "What is the primary analytical goal for the Titanic dataset?",
    question_type: "goal",
    why_asked:
      "Clarifies whether EVA should focus on explaining survival, predicting outcomes, or understanding passenger segments.",
  },
  {
    question: "Which stakeholders care most about this analysis?",
    question_type: "stakeholder",
    why_asked:
      "Aligns the narrative and dashboards to the needs of leadership, operations, or product/analytics teams.",
  },
  {
    question: "What time frame or snapshot of the Titanic voyage is most relevant?",
    question_type: "time",
    why_asked: "Determines whether EVA should emphasize the full manifest or specific cohorts (e.g. embarkation ports).",
  },
  {
    question: "What constraints or business rules should EVA respect for this Titanic analysis?",
    question_type: "priority",
    why_asked:
      "Ensures recommendations (e.g. around safety policies) are realistic and aligned with operational constraints.",
  },
]

export const titanicVisualizationsData: VisualizationsData = {
  overall_reasoning:
    "Visualizations focus on how passenger class, sex, age, and fare jointly influence survival on the Titanic.",
  total_rendered: 4,
  total_failed: 0,
  total_planned: 4,
  visualizations: [
    {
      question: "How did survival differ by passenger class?",
      chart_type: "bar",
      interpretation:
        "Survival rates were substantially higher in 1st class and dropped sharply in 3rd class, reflecting access to lifeboats and cabins closer to deck.",
      confidence_note: "High confidence given clear separation between classes and well-documented historical accounts.",
      validation_result: "passed",
      variables_used: ["Pclass", "Survived"],
      related_finding: "Passenger class strongly correlates with survival outcomes.",
      chart_type_reasoning:
        "A grouped bar chart clearly compares survival vs non-survival proportions across discrete passenger classes.",
      audience_calibration:
        "Designed for business and operations leaders; color-coded bars make the survival gap obvious at a glance.",
      plotly_config: {
        data: [
          {
            x: ["1st", "2nd", "3rd"],
            y: [0.63, 0.47, 0.24],
            type: "bar",
            name: "Survival rate",
          },
        ],
        layout: {
          title: "Survival Rate by Passenger Class",
          xaxis: { title: "Passenger Class" },
          yaxis: { title: "Survival Rate", tickformat: ".0%", range: [0, 1] },
          legend: { orientation: "h" },
        },
      },
    },
    {
      question: "How did survival differ between male and female passengers?",
      chart_type: "bar",
      interpretation:
        "Female passengers had much higher survival rates than male passengers, consistent with 'women and children first' evacuation protocols.",
      confidence_note:
        "Very high confidence; the signal is strong and widely corroborated by the historical record.",
      validation_result: "passed",
      variables_used: ["Sex", "Survived"],
      related_finding: "Sex is a strong driver of survival probability.",
      chart_type_reasoning:
        "A simple bar chart emphasizes the magnitude of the difference between two groups without overcomplication.",
      audience_calibration:
        "Appropriate for executive and non-technical audiences; labels and percentages make interpretation trivial.",
      plotly_config: {
        data: [
          {
            x: ["Female", "Male"],
            y: [0.74, 0.19],
            type: "bar",
            marker: { color: ["#F97316", "#3B82F6"] },
          },
        ],
        layout: {
          title: "Survival Rate by Sex",
          xaxis: { title: "Sex" },
          yaxis: { title: "Survival Rate", tickformat: ".0%", range: [0, 1] },
        },
      },
    },
    {
      question: "What is the age distribution of passengers, split by survival?",
      chart_type: "histogram",
      interpretation:
        "Most passengers were adults between 20 and 40 years old, but younger children show relatively higher survival share compared to their share of the manifest.",
      confidence_note:
        "Moderate confidence; age imputation and missing values slightly reduce precision but the overall trend is stable.",
      validation_result: "passed",
      variables_used: ["Age", "Survived"],
      related_finding: "Age interacts with class and sex in shaping survival outcomes.",
      chart_type_reasoning:
        "Overlaid histograms show how the age distribution of survivors differs from non-survivors across the same bins.",
      audience_calibration:
        "Suitable for analytics and data teams; still readable by business stakeholders with the legend explanation.",
      plotly_config: {
        data: [
          {
            x: [
              5, 8, 12, 16, 18, 22, 25, 28, 30, 35, 40, 45, 50, 55, 60,
            ],
            type: "histogram",
            opacity: 0.5,
            name: "Survived",
            marker: { color: "#22C55E" },
          },
          {
            x: [
              18, 20, 23, 26, 29, 32, 36, 41, 44, 48, 52, 58, 63,
            ],
            type: "histogram",
            opacity: 0.5,
            name: "Did not survive",
            marker: { color: "#EF4444" },
          },
        ],
        layout: {
          title: "Age Distribution by Survival Outcome",
          barmode: "overlay",
          xaxis: { title: "Age" },
          yaxis: { title: "Passenger Count" },
        },
      },
    },
    {
      question: "How does fare relate to passenger class and survival?",
      chart_type: "box",
      interpretation:
        "Higher fares (concentrated in 1st class) are associated with better survival outcomes, indicating a socio-economic gradient in safety.",
      confidence_note:
        "High confidence in the pattern, though fares are also influenced by cabin location and booking details.",
      validation_result: "passed",
      variables_used: ["Fare", "Pclass", "Survived"],
      related_finding: "Fare is a proxy for socio-economic status and cabin quality, both tied to survival.",
      chart_type_reasoning:
        "Box plots summarize the distribution of fares within each class while highlighting outliers and medians.",
      audience_calibration:
        "Targets analytics and strategy teams; box plots are more technical but convey rich distribution information.",
      plotly_config: {
        data: [
          {
            y: [80, 72, 90, 120, 150],
            type: "box",
            name: "1st Class",
          },
          {
            y: [20, 18, 25, 30, 40],
            type: "box",
            name: "2nd Class",
          },
          {
            y: [5, 7, 10, 12, 15],
            type: "box",
            name: "3rd Class",
          },
        ],
        layout: {
          title: "Fare Distribution by Passenger Class",
          yaxis: { title: "Fare (GBP equivalent)" },
        },
      },
    },
  ],
}

export const titanicDashboardData: DashboardData = {
  overall_reasoning:
    "The dashboard emphasizes who survived, from which classes and segments, and highlights operational lessons around evacuation and capacity.",
  stakeholder_calibration: "Calibrated for executive and operations leadership with a focus on safety and capacity planning.",
  kpis: [
    {
      name: "Overall Survival Rate",
      value: "38%",
      justification: "Share of passengers in the manifest who survived.",
      derivation_source: "Aggregated Survived flag across the full Titanic manifest.",
    },
    {
      name: "Female Survival Rate",
      value: "74%",
      justification: "Female passengers had significantly higher survival probability than males.",
      derivation_source: "Survival rate conditional on Sex = female.",
    },
    {
      name: "1st Class Survival Rate",
      value: "63%",
      justification: "First-class passengers were closer to lifeboats and had better access to crew.",
      derivation_source: "Survival rate conditional on Pclass = 1.",
    },
    {
      name: "3rd Class Survival Rate",
      value: "24%",
      justification: "Passengers in 3rd class were physically further from lifeboats and more constrained by layout.",
      derivation_source: "Survival rate conditional on Pclass = 3.",
    },
  ],
  alerts: [
    {
      alert_type: "Critical",
      description: "Survival rate for 3rd class males is extremely low compared to other groups.",
      evidence_ref: "Survival by Pclass & Sex visualization and contingency table.",
      confidence: "High",
    },
    {
      alert_type: "Warning",
      description: "Significant disparity between male and female survival indicates policy and access bias.",
      evidence_ref: "Survival by Sex bar chart.",
      confidence: "High",
    },
  ],
  recommendations: [
    {
      action: "Design evacuation protocols that guarantee minimum lifeboat access for all cabins, not just upper classes.",
      target_group: "Maritime safety & operations teams",
      expected_impact: "High reduction in survival disparity across socio-economic segments.",
      urgency: "High",
      confidence: "High",
      supporting_evidence_ref: "Differences in survival by Pclass and cabin location.",
      supporting_hypothesis_ref: "Higher classes had earlier and less-congested access to lifeboats.",
    },
    {
      action: "Simulate alternative lifeboat allocation strategies using this manifest as a counterfactual baseline.",
      target_group: "Analytics & simulation teams",
      expected_impact: "Medium improvement in future evacuation planning robustness.",
      urgency: "Medium",
      confidence: "Moderate",
      supporting_evidence_ref: "Concentration of fatalities in specific decks and cabins.",
      supporting_hypothesis_ref:
        "Different allocation rules would materially change survival outcomes for 3rd class passengers.",
    },
    {
      action: "Update stakeholder communication templates to explicitly call out risk to under-served segments.",
      target_group: "Communications & compliance",
      expected_impact: "Improved transparency and accountability in safety reporting.",
      urgency: "Medium",
      confidence: "Moderate",
      supporting_evidence_ref: "Gap between overall survival rate and worst-affected cohorts.",
      supporting_hypothesis_ref:
        "Transparent reporting leads to stronger incentives to address structural safety gaps.",
    },
  ],
  panels: [
    {
      panel_name: "Survival Overview",
      description: "High-level survival metrics by class and sex.",
      elements: [],
    },
    {
      panel_name: "Cohort Drilldown",
      description: "Drill into specific age, fare, and embarkation segments.",
      elements: [],
    },
  ],
}

export const titanicReportData: ReportData = {
  narrative:
    "The Titanic manifest reveals a stark pattern of survival shaped by class, gender, and physical access to lifeboats. " +
    "First-class passengers and women enjoyed markedly higher survival rates, while third-class males faced the most extreme risk. " +
    "Age and fare act as secondary drivers: younger passengers and those paying higher fares were more likely to survive, " +
    "largely because these factors correlate with cabin location and priority during evacuation.\n\n" +
    "From an operational perspective, the analysis underscores how capacity constraints and layout decisions translate directly into human outcomes. " +
    "Lifeboat capacity was insufficient relative to passenger volume, forcing harsh prioritization rules that amplified existing social hierarchies. " +
    "Simulated dashboards indicate that small design changes—such as more distributed lifeboat access and clearer route signage—could have meaningfully " +
    "rebalanced survival odds across classes and genders.\n\n" +
    "For modern safety and compliance teams, the Titanic serves as a historical case study in systemic risk. " +
    "It highlights the importance of stress-testing evacuation plans, auditing how different cohorts experience safety protocols, " +
    "and designing policies that guarantee baseline access to safety equipment for all passengers, regardless of ticket class or cabin location.",
  citations: [
    "Board of Trade Inquiry Report on the Loss of the Titanic (1912)",
    "EVA internal aggregation of survival outcomes by class, sex, and age.",
  ],
  included_visualizations: [
    "Survival Rate by Passenger Class",
    "Survival Rate by Sex",
    "Age Distribution by Survival Outcome",
    "Fare Distribution by Passenger Class",
  ],
  communicated_recommendations: [
    "Guarantee equitable lifeboat access across all cabin classes.",
    "Run regular evacuation simulations that stress-test cohort-specific risk.",
    "Report survival and incident metrics stratified by key demographic and booking attributes.",
  ],
  stakeholder_calibration: "Executive & safety leadership; high-level narrative with clear operational implications.",
}


# **EVA**
## Autonomous Data Analysis Assistant
### Product Requirements Document

#### **From Raw Data to Real Decisions — Automatically.**

Version 1.0 | Confidential


## **1. Product Vision**

EVA is a fully local, autonomous data science assistant that mirrors how a skilled data analyst
thinks and works — from the moment a dataset is received, through understanding, cleaning,
analysis, modeling, and finally to decisions and recommendations.


The core promise is simple:


**A person should be able to upload any dataset and walk away with a clear**
**understanding of what it means, what will happen next, and what to do about it —**
**without knowing a single line of code or a single statistical term.**


EVA does not function as a tool that requires the user to drive every decision. It functions as a
reasoning analyst — one that thinks first, computes second, and always explains what it did and
why.

## **2. The Core Design Insight**


Most automated data tools assume the following workflow:

```
   Upload → Clean → Model → Output

```

This is not how real data scientists work. A skilled analyst spends the first portion of their time
not touching the data at all — they spend it asking questions about reality.


What system produced this data? What does each row actually represent? What decision is this
dataset supposed to help make? What could go wrong if I misread it?


EVA is built around this insight. Every module in EVA — from cleaning to modeling to insight
generation — is downstream of a reasoning step that happens before any computation begins.


EVA's workflow, therefore, mirrors a real analyst:

```
   Understand Reality → Clean → Explore → Engineer → Model
   → Explain → Decide

```

Each arrow in this chain passes structured context from one stage to the next. No stage is a
black box. Every conclusion traces back to a reason.


## **3. Problem Statement**

Working with data today has three compounding barriers that prevent non-technical users from
deriving value on their own.

### **3.1 Time Is Wasted Before Intelligence Begins**


The majority of a data analyst's time is consumed before any insight is produced. Data cleaning,
formatting correction, handling missing values, removing duplicates, and resolving column
inconsistencies account for 40 to 80 percent of total analysis time. Users are trapped doing
maintenance work when they need answers.

### **3.2 The Knowledge Barrier**


To answer even straightforward questions — why are sales falling, which patients are high risk,
which customers will leave — a user must understand feature selection, statistical modeling,
evaluation metrics, and interpretation. This eliminates students, business owners, healthcare
analysts, and most non-technical professionals from accessing data intelligence on their own.

### **3.3 The Privacy and Trust Barrier**


Users with sensitive data — medical records, client datasets, proprietary business information

- are unwilling or legally unable to upload their data to external cloud platforms. They are left
without options: either compromise on privacy or remain without insight.

## **4. Target Users**






|User|Primary Need|What EVA Does For Them|
|---|---|---|
|Student|Understand their dataset for a<br>project without knowing what<br>analysis to run|Explains data in plain language,<br>suggests analysis direction,<br>teaches as it works|
|Freelance Analyst|Process messy client CSVs<br>quickly without losing hours to<br>cleaning|Autonomously cleans and<br>prepares data, delivers findings<br>ready to present|
|Business Owner|Understand what their customer or<br>sales data is saying without hiring<br>a data scientist|Translates data into<br>plain-language decisions with<br>specific recommended actions|


|Healthcare Researcher|Analyze patient data without it<br>leaving a secure environment|Runs entirely on-device,<br>HIPAA-compatible by design,<br>explains clinical patterns|
|---|---|---|
|Non-Technical Founder|Make data-driven decisions<br>without depending on a technical<br>team for every question|Surfaces what matters, explains<br>why, and recommends what to do<br>next|


## **5. The Analyst Workflow — EVA's Operating Sequence**

Every stage EVA performs maps directly to what a skilled human data scientist would do. The
stages are ordered deliberately. No stage begins until the previous one has produced its output.
Each stage passes structured context to the next.


Before any processing begins, EVA reads the dataset and constructs a real-world understanding
of it. This is the most critical stage. It determines everything that follows.


A real analyst receiving a new dataset does not immediately clean it or run a model. They first
ask: What is this? What system generated these rows? What decision is this meant to inform?
Who will act on the answer?


EVA performs this reasoning automatically. It inspects the raw structure of the dataset —
column names, data types, value distributions, unique counts, null ratios, sample records — and
from these signals infers what the dataset actually represents.


**What EVA determines at this stage:**

•​ What each row represents — a transaction, a patient visit, a sensor reading, a daily
summary, an employee record
•​ The time behavior of the data — is it static, a time series, an event log, or panel data
tracking the same entity across time
•​ The likely analytical goal — prediction, diagnosis, monitoring, segmentation, anomaly
detection, or factor analysis
•​ The probable stakeholder — who will use the output and what decision they need to
make
•​ Risks of misinterpretation — which columns are identifiers and must not be used as
features, which columns may contain post-outcome information


EVA produces a structured Dataset Narrative that is passed to every subsequent stage. This
narrative is the foundation of all downstream reasoning. Cleaning decisions reference it. Feature
engineering uses it. Model selection is guided by it.


EVA will not proceed to any further stage without having completed this understanding step.
This is a deliberate product rule: intelligence before computation, always.


Once EVA understands the dataset, it cleans it — but not generically. Cleaning decisions are
informed by the Dataset Narrative from Stage 0. A date column in a time series dataset is
treated differently from a date column in a static snapshot. A numeric field in a medical dataset
is handled with different assumptions than the same field in an e-commerce log.


**What EVA does at this stage:**

•​ Handles missing values using contextually appropriate strategies — mean imputation,
forward-fill for time series, domain-specific defaults, or flagging where imputation would
distort results
•​ Resolves inconsistent categorical entries — normalizing variations in spelling, case, and
encoding into clean unified values
•​ Removes exact duplicates and flags near-duplicates for review
•​ Corrects data type mismatches — columns stored as text that should be numeric or
datetime
•​ Detects and flags suspicious values — entries that fall outside statistically or
domain-plausible ranges
•​ Identifies and preserves identifier columns as non-analytical fields


EVA does not ask the user to make manual decisions about cleaning. It handles all of this
autonomously and produces a plain-language explanation of every change it made and why.
The user can review what happened; they do not need to drive it.


With clean data and a clear understanding of what it represents, EVA moves into structured
exploration. This stage does not produce charts for the sake of charts. Every output connects
back to the analytical goal identified in Stage 0.


**What EVA does at this stage:**

•​ Calculates distributions and identifies skew, outliers, and concentration in key variables


•​ Identifies correlations between variables — including which relationships are likely
meaningful versus coincidental
•​ Detects natural groupings or segments within the data
•​ Surfaces anomalies and unusual patterns that warrant attention
•​ Identifies temporal trends for time-dependent datasets — seasonality, cycles, drift, step
changes


All outputs from this stage are expressed in plain English. EVA does not present a matrix of
correlation coefficients and leave the user to interpret it. It explains: "Age and monthly purchase
frequency are strongly linked to whether a customer stays or leaves. Customers who haven't
purchased in 90 days are significantly more likely to churn."


This is the stage where EVA begins teaching — not just analyzing. Users come away
understanding not just what the data shows, but why certain patterns matter.


Raw columns are rarely the best representation of what matters. A skilled analyst who works in
healthcare builds different derived variables than one who works in finance or e-commerce. EVA
performs this same domain-aware transformation automatically.


Using the domain and analytical goal established in Stage 0, EVA identifies what derived
features would be meaningful, why they matter in this specific context, and how they should be
constructed.


**Examples of how domain changes the engineering:**














|Domain|Raw Columns|Derived Feature|Why It Matters|
|---|---|---|---|
|Healthcare|age, height, weight|BMI category|Captures nonlinear<br>health risk thresholds|
|E-commerce|order_date,<br>last_order_date|Days since last<br>purchase|Core signal for churn<br>likelihood|
|Finance|daily_close_price|7-day rolling average|Smooths noise, reveals<br>trend direction|
|HR|hire_date, today|Tenure in months|Tenure correlates with<br>attrition risk|
|Manufacturing|sensor_readings over<br>time|Rolling variance|Early indicator of<br>equipment failure|


EVA explains every feature it proposes in two ways: the statistical reason it was created, and
the real-world business meaning it carries. This is not optional — every feature suggestion
includes both.


EVA also identifies what it will not do: it will not use identifier columns as features, it will not
create features that encode information only available after the outcome has occurred, and it will
not produce features that have no interpretable meaning in the domain.


EVA selects a modeling approach based on the problem type determined in Stage 0 and the
features engineered in Stage 3. It does not default to a single algorithm. It reasons through the
choice.


**How EVA approaches model selection:**

•​ Identifies the problem type — binary classification, multi-class classification, regression,
time series forecasting, clustering, or anomaly detection
•​ Selects candidate approaches appropriate to the data size, feature types, and
interpretability requirements of the stakeholder
•​ Explains why each candidate approach is being considered and what its tradeoffs are
•​ Trains and evaluates multiple approaches where appropriate
•​ Selects the final model based on performance and interpretability, not complexity


For users who need to explain their results — to a manager, a professor, a client, a medical
team — EVA prioritizes interpretable models and supplements them with explanation tools. A
model that cannot be explained is not useful to most of EVA's users.


EVA will not present model results before it has presented what the dataset represents. This
rule is enforced at every stage.


Model output in raw form — accuracy scores, feature importance arrays, coefficient tables — is
not useful to EVA's users. EVA translates every result into plain language that connects back to
the real-world context established in Stage 0.


**What EVA produces at this stage:**

•​ A narrative explanation of what the model found — not statistical jargon, but a story
about the data


•​ The top factors that drive the outcome, explained in terms the stakeholder understands
•​ Confidence levels for predictions, expressed in plain language
•​ Specific flagged cases — which customers, which patients, which products — are high
priority and why
•​ A clear explanation of model limitations and where the results should be trusted with
caution


EVA is designed to teach as it analyzes. A student using EVA to analyze a dataset for a class
project should come away not just with results, but with a better understanding of why those
results make sense.


Analysis is only valuable when it leads to action. EVA does not stop at insight — it translates
insight into specific, actionable recommendations.


This is the stage where EVA acts as a business consultant, not just a statistician. Given what
the data shows, given what the model predicts, given who the stakeholder is — what should
happen next?


**Examples of decision guidance EVA produces:**

•​ For a business owner: "These 47 customers show strong churn indicators. Prioritize
them for a retention outreach in the next 14 days. Customers in this group who have
been inactive for more than 60 days have the highest urgency."
•​ For a healthcare researcher: "These patient profiles match the risk factors associated
with readmission. Flag them for follow-up scheduling before discharge."
•​ For a student: "Your strongest predictor is study hours per week. Increasing it from 5 to
10 hours is associated with an average grade improvement of one letter grade in this
dataset."


EVA always distinguishes between what the data shows and what it recommends as action. It is
transparent about the difference between correlation and causation, and it makes clear when a
recommendation is a strong signal versus a weaker probabilistic suggestion.


After the full analysis is complete, the user can ask follow-up questions in plain English. EVA
retains the full context of the session — the dataset narrative, the cleaning decisions, the


features created, the model results, and the insights generated — and uses all of it to answer
questions precisely.


**Examples of what users ask at this stage:**

•​ "Why did sales drop in Q3?" — EVA traces the answer through the data, not just the
model
•​ "What would happen if we discount this product category?" — EVA reasons from the
patterns it found
•​ "Explain this to me like I'm not a data person" — EVA rewrites its explanation in simpler
terms
•​ "Which variable matters most for predicting churn?" — EVA answers with both the
statistical answer and the business meaning
•​ "Can I use this for my report?" — EVA produces a formatted summary ready for
presentation


Every answer traces back to something EVA actually found in the data. EVA does not generate
plausible-sounding responses that are disconnected from the dataset. It grounds every answer
in evidence it can point to.

## **6. Multi-Agent Reasoning Architecture**


EVA's analytical pipeline is powered by a council of specialized AI agents, not a single model.
This architecture is motivated by a simple principle: single models hallucinate. A council of
agents that reason independently and reach consensus produces more reliable results.


Each agent in the council has a defined role, a defined scope, and a defined output format. No
agent operates outside its domain. The Council Chairman synthesizes their outputs and
resolves disagreements before any result is passed to the user.












|Agent|Role|Scope|
|---|---|---|
|The Analyzer|The Statistician — performs deep<br>structural and distributional analysis<br>of the data|Distribution analysis, correlation<br>detection, pattern identification,<br>outlier detection|
|The Cleaner|The Janitor — generates and<br>executes cleaning operations with<br>justification|Missing value handling, type<br>correction, deduplication, formatting<br>normalization|
|The Feature<br>Engineer|The Creative — proposes<br>domain-appropriate derived features<br>with formulas and rationale|Feature derivation, transformation<br>suggestions, domain-specific<br>variable creation|
|The Model Architect|The Engineer — selects algorithms,<br>configures training, evaluates results|Model selection, hyperparameter<br>reasoning, evaluation interpretation|


The Chairman The Decision-Maker — synthesizes
confidence scores from all agents,
resolves conflicts, produces the final
output



Consensus synthesis, conflict
resolution, quality gating before
output



Agents analyze independently to avoid confirmation bias. Where agents disagree — for
example, on whether to impute or drop a missing-value column — the Chairman receives both
positions with confidence scores and resolves the conflict. The resolution and the reasoning
behind it are visible to the user.

## **7. Functional Requirements**

### **7.1 Dataset Cognition (Stage 0)**


•​ EVA must identify what each row in a dataset represents
•​ EVA must classify the time behavior of the dataset — static, time series, event log, or
panel
•​ EVA must infer the likely analytical goal from structure and content alone
•​ EVA must detect identifier columns and prevent them from being used as model features
•​ EVA must produce a Dataset Narrative in plain English before any further processing
begins
•​ EVA must not proceed to cleaning until Stage 0 is complete

### **7.2 Data Cleaning (Stage 1)**


•​ EVA must handle missing values autonomously using contextually appropriate strategies
•​ EVA must resolve categorical inconsistencies without manual user input
•​ EVA must detect and remove exact duplicates
•​ EVA must correct data type mismatches
•​ EVA must flag suspicious values with explanations
•​ EVA must explain every cleaning decision in plain language

### **7.3 Exploratory Analysis (Stage 2)**


•​ EVA must identify the most important variables relative to the analytical goal
•​ EVA must surface correlations and explain their practical significance
•​ EVA must detect anomalies and unusual patterns
•​ EVA must identify temporal trends for time-dependent datasets
•​ All exploratory outputs must be expressed in plain English, not statistical notation


### **7.4 Feature Engineering (Stage 3)**

•​ EVA must infer the dataset domain and retrieve domain-specific feature engineering
knowledge
•​ EVA must propose derived features with formulas, statistical justification, and business
meaning
•​ EVA must not propose features that use identifier columns
•​ EVA must not propose features that encode post-outcome information
•​ Every proposed feature must include its expected impact on model performance

### **7.5 Modeling (Stage 4)**


•​ EVA must select modeling approaches based on problem type, not defaults
•​ EVA must explain why each approach was selected or rejected
•​ EVA must evaluate multiple candidate approaches where appropriate
•​ EVA must prioritize interpretable models for stakeholders who need to explain their
results
•​ EVA must not present model results before presenting what the dataset represents

### **7.6 Insight Generation (Stage 5)**


•​ EVA must translate all model outputs into plain-language explanations
•​ Every conclusion must include a reason, a confidence level, and an interpretation
•​ EVA must identify and flag specific high-priority cases — not just aggregate patterns
•​ EVA must clearly state limitations and where results should be treated with caution

### **7.7 Decision Guidance (Stage 6)**


•​ EVA must produce specific, actionable recommendations — not general observations
•​ EVA must tailor recommendations to the identified stakeholder type
•​ EVA must distinguish between correlation-based observations and causal claims
•​ EVA must indicate the confidence level behind each recommendation

### **7.8 Conversational Refinement (Stage 7)**


•​ EVA must retain full session context across the conversation
•​ EVA must answer follow-up questions grounded in the actual data it analyzed
•​ EVA must be able to explain any conclusion in simpler language on request


•​ EVA must be able to produce a formatted summary suitable for presentation or reporting

## **8. Non-Functional Requirements**

### **8.1 Privacy — Local First**


EVA is designed to run entirely on the user's own machine. No data, no query, no intermediate
result is transmitted to any external server. This is not a feature; it is a design constraint that
governs every architectural decision.


•​ All AI inference runs locally
•​ All data processing runs locally
•​ No external API calls for any core functionality
•​ Compatible with air-gapped environments

### **8.2 Transparency**


EVA must be able to account for every decision it makes. Users can always ask why EVA did
something, and EVA must provide a traceable, honest explanation.


•​ Every cleaning decision is logged and explained
•​ Every feature suggestion includes its rationale
•​ Every model choice includes the reasoning behind it
•​ Confidence levels are always surfaced, not hidden

### **8.3 Usability**


The benchmark for usability is a 10th-grade student with no data science background. If such a
user cannot complete an analysis session and understand what they found, EVA has not met its
usability standard.


•​ No technical prerequisites required
•​ No configuration required to begin an analysis
•​ All outputs are expressed in plain language by default
•​ Technical detail is available on request but never imposed

### **8.4 Speed**


EVA should feel responsive and interactive, not like a batch process. The user should not be
waiting passively for long periods.


•​ Initial dataset cognition and structural analysis: under 30 seconds for typical datasets
•​ Feature engineering suggestions: under 15 seconds
•​ Model training and evaluation: proportional to dataset size, with progress indication
•​ Conversational responses: under 10 seconds

## **9. Definition of Success**


EVA succeeds when a completely non-technical person can upload a spreadsheet and say, with
genuine understanding:

#### **"Now I understand my data and I know what to do."**


This is not a metric. It is the standard against which every product decision should be evaluated.

### **9.1 Operational Metrics**













|Metric|Target|
|---|---|
|Users who complete a full analysis on first<br>attempt|Over 80%|
|Time from upload to first meaningful insight|Under 5 minutes|
|Users who report understanding their data after<br>session|Over 85%|
|Users who can present results without additional<br>processing|Over 70%|
|Feature suggestions rated as relevant by domain<br>experts|Over 75%|
|Hallucination rate in feature or insight generation|Under 5%|

## **10. Future Directions**

The following capabilities are explicitly out of scope for the current milestone but represent the
natural evolution of EVA as the core pipeline matures.


•​ Continuous data monitoring — EVA watches a connected dataset over time and
surfaces changes automatically
•​ Scenario simulation — users ask "what if" questions and EVA reasons through the
implications
•​ Automated feature validation — EVA tests proposed features against model
improvement before recommending them
•​ SQL and database integration — EVA connects directly to structured data sources rather
than requiring CSV upload
•​ Multi-dataset reasoning — EVA understands how two related datasets connect and what
can be learned from their relationship
•​ Collaborative sessions — multiple users can work with the same EVA analysis
simultaneously
•​ Deep learning support — for image, audio, and unstructured text datasets

## **11. Product Rules**


These are non-negotiable constraints on EVA's behavior. They exist to protect the quality and
integrity of every user interaction.


1.​ EVA will never present model results before explaining what the dataset represents.
2.​ EVA will never use identifier columns as model features, regardless of what other

systems might do.
3.​ EVA will never produce a conclusion without a reason that traces back to the data.
4.​ EVA will never pretend to be more confident than it is — every output includes an honest

confidence signal.
5.​ EVA will never transmit user data outside the user's device.
6.​ EVA will never require the user to make a technical decision to proceed — all technical

choices are EVA's responsibility.
7.​ EVA will always explain what it did, in plain language, after doing it.


**EVA — Stop Cleaning. Start Understanding.**



# **EVA**
## **Machine Learning Reasoning Layer**
#### Master Product Requirements Document

Version 1.0 | Internal Engineering Reference


### **Table of Contents**

This document is the master reference for EVA's Machine Learning Reasoning Layer (MLRL). It
defines the system's design philosophy, pipeline architecture, Global Analysis Ledger structure,
cross-module rules, and links to each module's individual specification.

Module documents referenced by this master:

   - PFTDC — Problem Framing & Training Data Construction

   - MCG — Model Candidate Generator

   - TEM — Training & Evaluation Module

   - RVEM — Reliability & Validation (Explainability) Module

   - PMDD — Prediction, Monitoring & Dockerized Deployment


### **1. Purpose & Scope**

The Machine Learning Reasoning Layer (MLRL) is EVA's capability for learning predictive
patterns from data when analytical reasoning alone cannot answer the user's objective. It is a
supporting layer — not the primary intelligence.

EVA's reasoning order is fixed:

_Understanding → Reasoning → Hypothesis → Evidence → Then Learning_

The MLRL activates only when the Global Analysis Ledger determines that a future outcome
must be predicted, a classification decision is required, or pattern generalization cannot be
achieved through descriptive analysis alone. If these conditions are not met, EVA completes the
analysis without building a model.

### **2. Design Philosophy**


Traditional ML systems begin with models and search for meaning later. EVA reverses this.
Machine learning in EVA is contextual, explainable, and evidence-bound. The model is treated
as an instrument used by the analyst — not as the analyst itself.




#### **2.1 What This Means in Practice**

   - A slightly less accurate but explainable model may be preferred over a marginally better
opaque one.

   - Modeling is rejected when it would not influence a real decision.

   - The system prefers no model over a misleading model.

   - Machine learning is never activated for pure explanation, simple segmentation,
descriptive reporting, or trend visualization.

### **3. When Machine Learning Is Activated**

#### **3.1 Activation Conditions**

The MLRL activates only after all prior EVA layers have completed: Dataset Profiler & Semantic
Understanding, Question Builder / Intent Inference, Data Repair & Integrity Layer, Feature
Intelligence Engine, and Investigation & Hypothesis Engine.

Machine learning is triggered when the User Intent Record specifies any of the following:

   - Prediction of a future outcome

   - Forecasting over time


   - Automated classification

   - Risk scoring

   - Detection of unseen or anomalous cases

#### **3.2 Exclusion Conditions**

Machine learning is explicitly not activated for:

   - Pure explanation tasks

   - Descriptive segmentation with no decision objective

   - Descriptive reporting

   - Trend visualization




### **4. Global Analysis Ledger (GAL)**

The Global Analysis Ledger is the single source of truth for the entire MLRL pipeline. No module
communicates directly with another. All state, decisions, and reasoning flow through the GAL.

#### **4.1 Purpose**

   - Makes every decision traceable and reproducible from one location

   - Prevents modules from making assumptions not grounded in prior analysis

   - Enables full audit of any modeling decision

   - Allows individual modules to be re-run without breaking pipeline state

#### **4.2 GAL Top-Level Structure**

The following keys define the GAL's structure. Each module reads from and writes to specific
keys only.


|GAL Key|Contents|
|---|---|
|**dataset_identity**|Row meaning, domain, time behavior classification|
|**user_intent_record**|Objective, decision type, stakeholder type, interpretability<br>priority|
|**restricted_columns**|Columns excluded from modeling (leakage, identifiers,<br>post-outcome)|


|hypotheses|Key findings from the Investigation & Hypothesis Engine|
|---|---|
|**feature_registry**|Validated engineered features with reasoning|
|**model_definition_record**|Written by PFTDC — problem type, target, learning view<br>schema, split strategy|
|**candidate_model_record**|Written by MCG — candidate approaches, metric,<br>reasoning|
|**model_evaluation_record**|Written by TEM — performance, stability, generalization,<br>selected model|
|**model_validation_record**|Written by RVEM — feature influence, hypothesis<br>alignment, leakage check, validation status|
|**prediction_deployment_record**|Written by PMDD — deployment status, monitoring<br>results, retraining flags|
|**session_log**|Timestamped record of all decisions, rejections, and<br>reasoning across all modules|

#### **4.3 Read/Write Permissions by Module**

|Module|GAL Permissions|
|---|---|
|**PFTDC**|Reads: dataset_identity, user_intent_record,<br>restricted_columns, hypotheses, feature_registry. Writes:<br>model_definition_record|
|**MCG**|Reads: model_definition_record, user_intent_record,<br>hypotheses. Writes: candidate_model_record|
|**TEM**|Reads: model_definition_record, candidate_model_record.<br>Writes: model_evaluation_record|
|**RVEM**|Reads: model_evaluation_record, hypotheses,<br>feature_registry. Writes: model_validation_record|
|**PMDD**|Reads: model_validation_record. Writes:<br>prediction_deployment_record|


### **5. Pipeline Architecture**

#### **5.1 Module Sequence**

The MLRL consists of five coordinated modules that execute in sequence. Each module
performs a reasoning task, not purely a computational one.


**Module** **Responsibility**


|1. Problem Framing &<br>Training Data<br>Construction (PFTDC)|Determines if ML is appropriate. Defines the prediction task.<br>Constructs the Learning View.|
|---|---|
|**2. Model Candidate**<br>**Generator (MCG)**|Selects 2–4 appropriate modeling approaches based on<br>problem type, data characteristics, and interpretability needs.|
|**3. Training & Evaluation**<br>**Module (TEM)**|Trains each candidate. Evaluates performance, stability, and<br>generalization. Selects the most reliable model.|
|**4. Reliability & Validation**<br>**(Explainability) Module**<br>**(RVEM)**|Verifies model reasoning aligns with prior evidence and<br>hypotheses. Detects leakage. Assigns validation status.|
|**5. Prediction & Monitoring**<br>**(PMDD)**|Deploys validated models as containerized services. Logs<br>predictions. Monitors for drift and degradation.|

#### **5.2 Data Flow**





_GAL → PFTDC (Learning View) → MCG → TEM → RVEM → PMDD → Dashboard &_
_Report_


The pipeline operates on a Learning View — not the raw dataset. The Learning View is
constructed from the repaired dataset, engineered features, and permitted columns only.

### **6. Pipeline Failure & Recovery**


If any module rejects its output, the pipeline halts at that stage. The following recovery
behaviors apply:


|Failure Point|Recovery Behavior|
|---|---|
|**PFTDC rejects modeling**|Pipeline ends. Reason logged to GAL. EVA falls back to<br>descriptive analysis. User is notified with explanation.|
|**TEM rejects all candidates**|Pipeline halts. GAL logs rejection reasons. PFTDC is notified<br>to re-evaluate problem framing or adjust feature set before<br>retry.|
|**RVEM rejects model**|Model is not deployed. RVEM logs contradiction. MCG and<br>TEM may be re-run with revised constraints. If leakage is<br>detected, PFTDC must re-run.|
|**PMDD detects severe drift**|Prediction service is flagged unreliable. Dashboard displays<br>warning. New analysis session is requested. Automatic<br>retraining does not occur.|




### **7. Class Imbalance Handling**

Class imbalance is one of the most common real-world ML problems and must be handled
explicitly. When the PFTDC detects severe class imbalance in the target variable, it must:

   - Flag the imbalance in the model_definition_record

   - Alert the MCG to adjust metric selection (e.g., prefer precision/recall over accuracy)

   - Ensure the split strategy preserves class distribution across training, validation, and
holdout sets

The MCG and TEM must acknowledge the imbalance flag and reflect it in candidate selection
and evaluation criteria respectively.

### **8. Human Review & Override Touchpoints**


EVA is a decision-support system. Human analysts retain authority over modeling decisions at
the following points:







|Touchpoint|Behavior|
|---|---|
|**Conditional Validation**|When RVEM assigns Conditionally Validated status, a human<br>reviewer must acknowledge limitations before the model is<br>used in high-stakes decisions. Dashboard displays a<br>persistent caution indicator.|
|**Contradiction Flag**|When a model contradicts a strong prior hypothesis, it is<br>flagged for human review. The system explains the<br>contradiction but does not resolve it automatically.|
|**Retraining**<br>**Recommendation**|PMDD recommends retraining but does not trigger it. A human<br>must initiate a new analysis session.|
|**Model Override**|An analyst may override a model's prediction for a specific<br>record. The override is logged in the session_log with reason.|

### **9. Monitoring & Retraining Thresholds**

The PMDD monitors deployed models continuously. The following thresholds define when alerts
and retraining recommendations are triggered:


**Drift Type** **Threshold for Alert / Retraining Recommendation**


|Confidence Drift|Average prediction confidence drops more than 15% relative<br>to baseline over a rolling 100-prediction window.|
|---|---|
|**Data Drift**|Input feature distribution diverges from training distribution by<br>a threshold equivalent to a population stability index (PSI) ><br>0.2 for any key feature.|
|**Behavior Drift**|The distribution of predicted outcomes shifts more than 20%<br>relative to the baseline prediction distribution.|
|**Error Pattern**|If ground truth outcomes are available, model error rate<br>exceeds 2x the holdout test error rate over any 200-prediction<br>window.|


These thresholds are defaults and may be adjusted in the session configuration by the analyst
before deployment.

### **10. Conditional Validation — Operational Behavior**


The RVEM assigns one of three validation statuses. The Conditionally Validated status requires
specific operational behavior that must be enforced downstream:

|Component|Behavior for Conditionally Validated Models|
|---|---|
|**Dashboard**|Displays a persistent orange caution banner on all predictions<br>from this model. High-confidence predictions are still surfaced<br>but marked.|
|**Report Generator**|Must include a dedicated section explaining what conditions<br>are unresolved and what risks they pose.|
|**Monitoring**|PMDD runs monitoring checks at 2x the standard frequency<br>for conditionally validated models.|
|**Human Acknowledgement**|For high-stakes use cases (as defined in user_intent_record),<br>a human reviewer must log acknowledgement before<br>predictions are acted upon.|


### **11. Global Operational Rules**


These rules apply across all modules and cannot be overridden at the module level:


1. ML cannot run without a defined target variable.
2. Restricted columns cannot be used at any stage of the pipeline.
3. All training steps, decisions, and rejections must be recorded in the GAL.
4. Models must pass Reliability & Validation before deployment.
5. Every prediction must include a confidence estimate.
6. No model may be deployed with a Rejected validation status.


7. The Learning View — not the raw dataset — is the only permitted training input.
8. Time-ordered datasets must use chronological splits. Random mixing is forbidden.
9. A simpler, reliable model is preferred over a complex, marginally better one.
10. If the pipeline fails, EVA must notify the user with a clear explanation.

### **12. Dockerized Service Architecture**


Each MLRL module operates as an independent containerized service. This ensures
reproducibility, failure isolation, independent re-execution, and scalability.

Services communicate through structured artifacts written to and read from the GAL. No module
shares memory directly with another.

#### **12.1 Session Artifact Structure**

_eva-session-data/sessions/<session_id>/dataset_snapshot/ | repaired_dataset/ |_
_feature_view/ | learning_view/ | model_candidates/ | evaluation_results/ | selected_model/ |_
_prediction_logs/ | ledger_snapshot/_


All artifacts must be preserved to ensure full reproducibility. A model cannot be separated from
its training metadata, feature schema, evaluation metrics, and reliability report.

### **13. Module Document Index**


Each module is specified in a dedicated document. The following table maps modules to their
documents and the GAL keys they own:






|Module|Document|
|---|---|
|**PFTDC — Problem**<br>**Framing & Training Data**<br>**Construction**|EVA-ML-PFTDC.docx|
|**MCG — Model Candidate**<br>**Generator**|EVA-ML-MCG.docx|
|**TEM — Training &**<br>**Evaluation Module**|EVA-ML-TEM.docx|
|**RVEM — Reliability &**<br>**Validation (Explainability)**<br>**Module**|EVA-ML-RVEM.docx|
|**PMDD — Prediction,**<br>**Monitoring & Dockerized**<br>**Deployment**|EVA-ML-PMDD.docx|


All module documents reference this master. In case of conflict between a module document
and this master, this master takes precedence.


EVA — Machine Learning Reasoning Layer Master PRD | Internal Use Only



# **MCG**
## **Model Candidate Generator**

EVA Machine Learning Reasoning Layer — Module Specification


Version 1.0 | References: EVA-ML-Master.docx


## **1. Purpose**

The Model Candidate Generator determines which learning approaches EVA should consider
for the defined prediction problem. Instead of blindly testing many algorithms, this module
reasons about what types of models are appropriate given the problem type, dataset size,
feature characteristics, user interpretability requirements, and stability needs.




## **2. Inputs from Global Analysis Ledger**


   - model_definition_record — problem type, learning view schema, split strategy, class
imbalance flag

   - user_intent_record — stakeholder type, interpretability requirement, decision objective

   - hypotheses — prior analytical findings about feature relationships

## **3. Candidate Selection Strategy**


The module selects modeling families, not specific implementations. Selection depends on four
factors: data size, feature structure, noise level, and explanation requirement.

The module creates a balanced portfolio including an interpretable baseline, a flexible learner,
and a robustness-oriented method. This ensures meaningful comparison rather than random
experimentation.

### **3.1 Candidate Count**

The module outputs between 2 and 4 modeling approaches. If fewer than 2 approaches survive
pre-selection filters, the module logs a warning in the session_log and proceeds with a single
candidate only if it passes all downstream reliability checks. It must not silently reduce scope.

## **4. Interpretable Baseline Requirement**


Every modeling session must include at least one interpretable candidate. This is mandatory
and cannot be skipped.


   - Provides a reference performance benchmark

   - Provides understandable feature relationships for hypothesis checking

   - Acts as a sanity check against complex models


_If a complex model outperforms the baseline only marginally, the baseline is preferred per_
_the Master PRD's reliability-over-complexity principle._

## **5. Complexity Control**

### **5.1 Prefer Simpler Models When**

   - Dataset is small

   - Features are few

   - Noise level is high

   - User requires explanation

### **5.2 Allow Higher Flexibility When**

   - Large dataset exists

   - Complex nonlinear patterns have been detected

   - Predictive accuracy is critical and stakeholder type permits reduced interpretability

## **6. Metric Selection**


Evaluation metrics are chosen based on user intent and must be recorded with justification.
Defaults by use case:







|User Intent|Metric Guidance|
|---|---|
|**Risk detection**|Minimize missed risky cases — prioritize recall|
|**Decision automation**|Minimize false actions — prioritize precision|
|**Estimation tasks**|Minimize prediction deviation — prioritize RMSE or MAE|
|**High interpretability**<br>**requirement**|Emphasize explainability; accuracy is secondary|
|**Class imbalance flagged**|Use F1, precision/recall, or AUC-ROC. Never use raw<br>accuracy.|

## **7. Hypothesis Alignment Check**

The module compares candidate model assumptions with previously generated hypotheses
from the GAL. If hypotheses suggest strong linear relationships, simpler models are prioritized.
If relationships appear nonlinear or interaction-heavy, flexible candidates are included. Modeling
assumptions that contradict observed data behavior are not permitted.

## **8. Output: candidate_model_record**


|Field|Contents|
|---|---|
|**Candidate List**|2–4 selected learning approaches|
|**Reasoning**|Why each candidate was chosen, referencing dataset<br>characteristics|
|**Expected Behavior**|What patterns each candidate should capture|
|**Expected Weaknesses**|Known limitations of each candidate|
|**Chosen Evaluation Metric**|How success will be measured, with justification|
|**Interpretability**<br>**Expectation**|Level of explanation possible for each candidate|


## **9. Operational Rules**

1. At least one interpretable candidate is mandatory in every session.
2. Candidate count must be between 2 and 4. Log a warning if fewer than 2 survive.
3. Candidate reasoning must reference dataset characteristics from the

model_definition_record.
4. Metric choice must align with user intent and be justified.
5. Candidates cannot use modeling assumptions that contradict hypothesis findings.
6. Class imbalance flag must influence metric selection if present.

## **10. Relationship to Other Modules**

|Module|Relationship|
|---|---|
|**PFTDC**|Provides model_definition_record including problem type and<br>class imbalance flag|
|**TEM**|Trains and evaluates the candidate set|
|**RVEM**|Verifies candidate behavior against hypotheses|
|**Master PRD**|Defines reliability-over-complexity preference and global rules|



EVA — MCG Module Specification | Internal Use Only



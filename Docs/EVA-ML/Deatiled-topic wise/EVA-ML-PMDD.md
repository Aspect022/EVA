# **PMDD**
## **Prediction, Monitoring & Dockerized Deployment**

EVA Machine Learning Reasoning Layer — Module Specification


Version 1.0 | References: EVA-ML-Master.docx


## **1. Purpose**

The Prediction, Monitoring & Dockerized Deployment Module converts a validated model into a
reusable prediction service and continuously evaluates whether its predictions remain reliable
over time. This module allows EVA to move from analysis to operational assistance.




## **2. Preconditions**

This module activates only if the RVEM has assigned a validation status of Validated or
Conditionally Validated. Rejected models cannot be deployed under any circumstances.




## **3. Dockerized Model Service**

The selected model is packaged as an isolated containerized service. The purpose of
containerization is reproducibility, independence from the main EVA system, consistent
behavior across machines, and safe execution.

The container holds the trained model, feature schema, preprocessing rules, prediction logic,
and explanation interface. The model must never rely on external state at prediction time.

## **4. Prediction Interface**


The deployed service accepts new input records that follow the Learning View schema. For
each record, the system returns:

   - Predicted outcome

   - Confidence estimate (mandatory — predictions without confidence are not permitted)

   - Risk category

   - Explanation reference pointing to the RVEM case-level explanation

For Conditionally Validated models, all predictions are accompanied by a caution indicator in the
response payload and in the dashboard.

## **5. Feature Consistency Check**


Before generating a prediction, the module verifies that required features are present, feature
formats are valid, and values fall within expected ranges. If input is inconsistent, the system
must either reject the prediction with a logged reason, or serve the result flagged as unreliable
with an explanation.

## **6. Prediction Logging**


Every prediction request is recorded in the prediction_logs session artifact. The log includes
timestamp, input summary, prediction, confidence level, and any flags raised during feature
consistency check. This log supports monitoring and later review.

## **7. Drift Monitoring**


The module continuously checks for model degradation using the thresholds defined in the
Master PRD. The following drift types are monitored:

|Drift Type|Alert Threshold|
|---|---|
|**Confidence Drift**|Average prediction confidence drops more than 15% relative<br>to baseline over a rolling 100-prediction window.|
|**Data Drift**|Input feature distribution diverges from training distribution<br>beyond a PSI threshold of 0.2 for any key feature.|
|**Behavior Drift**|Distribution of predicted outcomes shifts more than 20%<br>relative to the baseline prediction distribution.|
|**Error Pattern Drift**|If ground truth is available, error rate exceeds 2x the holdout<br>test error rate over any 200-prediction window.|



These thresholds are defaults and may be adjusted by the analyst in the session configuration
before deployment.

For Conditionally Validated models, monitoring runs at 2x the standard frequency for all drift
types.

## **8. Retraining Recommendation**


When drift thresholds are exceeded, the module recommends retraining by writing a retraining
flag to the prediction_deployment_record and alerting the Dashboard Composer. The system
does not automatically retrain. A new analysis session must be initiated by a human reviewer.




## **9. Human Review Touchpoints**







|Touchpoint|Behavior|
|---|---|
|**Drift Alert**|Dashboard displays alert. Human must acknowledge and<br>decide whether to initiate a new session.|
|**Conditionally Validated**<br>**Predictions**|For high-stakes decisions, a human must log<br>acknowledgement before acting on predictions.|
|**Model Override**|An analyst may override a specific prediction. The override is<br>logged in the session_log with reason.|
|**Retraining Decision**|Human must initiate new session. System does not retrain<br>autonomously.|

## **10. Integration with Dashboard Composer**

The Dashboard Composer receives high-risk predictions, uncertain cases, drift alerts, and
Conditionally Validated model indicators. The dashboard must visibly indicate when model
reliability is weakening. For conditionally validated models, a persistent orange caution banner
is shown on all predictions.

## **11. Integration with Report Generator**


The Report Generator includes how predictions are produced, reliability limitations, current
monitoring status, and any retraining recommendations. The report must never present
predictions without explaining uncertainty. For Conditionally Validated models, the report must
include a dedicated section on unresolved conditions and associated risks.

## **12. Output: prediction_deployment_record**






|Field|Contents|
|---|---|
|**Deployment Status**|Model active or inactive|
|**Validation Status**|Validated or Conditionally Validated|
|**Prediction Schema**|Required input features and formats|
|**Confidence Behavior**|Typical prediction confidence profile at deployment|
|**Monitoring Results**|Detected drift types and current status|
|**Retraining**<br>**Recommendation**|Flag and reason if triggered|


## **13. Operational Rules**

1. Only Validated or Conditionally Validated models may be deployed.


2. Every prediction must include a confidence estimate.
3. Every prediction must be logged with timestamp and input summary.
4. Drift must be monitored continuously using the defined thresholds.
5. Users must be warned when model reliability is declining.
6. Automatic retraining is prohibited. Human review is required.
7. Conditionally Validated models run monitoring at 2x standard frequency.
8. Model overrides must be logged with reason.

## **14. Relationship to Other Modules**

|Module / Component|Relationship|
|---|---|
|**RVEM**|Approves model and provides validation status|
|**Dashboard Composer**|Receives predictions, alerts, and caution indicators|
|**Report Generator**|Receives monitoring status and limitation explanations|
|**GAL (session_log)**|Stores full monitoring history and override log|
|**Master PRD**|Defines drift thresholds, conditional validation behavior, and<br>retraining rules|



EVA — PMDD Module Specification | Internal Use Only



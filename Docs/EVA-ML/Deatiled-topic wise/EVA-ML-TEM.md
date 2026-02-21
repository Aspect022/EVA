# **TEM**
## **Training & Evaluation Module**

EVA Machine Learning Reasoning Layer — Module Specification


Version 1.0 | References: EVA-ML-Master.docx


## **1. Purpose**

The Training & Evaluation Module trains the candidate learning approaches selected by the
MCG and evaluates their performance, stability, and generalization reliability. The module does
not aim to maximize performance metrics alone. Its objective is to determine which model can
be safely trusted to support decisions.




## **2. Three Evaluation Criteria**

Every model must be evaluated across three dimensions simultaneously. A model that fails any
one of them is rejected.

|Criterion|Definition|
|---|---|
|**Performance**|How accurately does the model predict on unseen validation<br>data using the chosen metric?|
|**Stability**|Does the model produce consistent predictions across<br>different training splits and small input variations?|
|**Generalization**|Does the model maintain reasonable performance on the<br>completely held-out test set?|


## **3. Inputs from Global Analysis Ledger**


   - model_definition_record — learning view, split strategy, class imbalance flag

   - candidate_model_record — modeling approaches, evaluation metric

## **4. Training Procedure**


For each candidate: train on the training set, evaluate on the validation set, perform repeat
validation checks across different splits, and record all behavior. Training must be fully
reproducible using the same data and configuration stored in the GAL.

## **5. Performance Evaluation**


The module calculates performance using the metric specified in the candidate_model_record.
Performance evaluation includes validation performance, holdout test performance, and
comparison to the interpretable baseline.


A candidate is rejected if its performance is worse than the baseline or performance is
inconsistent across validation runs.




## **6. Overfitting Detection**

The module checks whether a model memorizes instead of learning. Indicators include a large
gap between training and validation performance, and a sudden performance drop on unseen
data. If detected, the model is marked unreliable and rejected.

## **7. Stability Testing**


The module evaluates how sensitive a model is to small changes by testing across different
training splits and small input variations. A stable model should produce similar predictions
across reasonable variations. Highly unstable models are rejected even if they are accurate.

## **8. Generalization Assessment**


The module evaluates model performance on the holdout test set — data the model has never
seen. A model must maintain reasonable performance without drastic degradation. If a model
only works on known data, it is rejected.




## **9. Model Comparison & Selection**

After evaluation, all candidates are compared across performance, stability, generalization, and
interpretability. The highest score alone does not win. The selected model is the most reliable
model, not the most complex. A simpler reliable model is preferred over a marginally better
complex one.

### **9.1 When All Candidates Fail**

If all candidates are rejected, the module logs the reasons in the session_log and halts the
pipeline. The MCG and PFTDC are notified to re-evaluate the problem framing or feature set.
The pipeline does not retry automatically — a new analysis session is required.


## **10. Output: model_evaluation_record**

|Field|Contents|
|---|---|
|**Training Results**|Performance metrics per candidate on validation set|
|**Overfitting Assessment**|Whether memorization occurred and evidence|
|**Stability Assessment**|Sensitivity to variation across splits|
|**Generalization Results**|Performance on holdout test set|
|**Selected Model**|Chosen candidate and full reasoning|
|**Rejected Models**|Why each was rejected, with evidence|


## **11. Operational Rules**

1. A model cannot be selected using performance score alone.
2. The holdout test set must not be used during training or tuning.
3. All evaluations must be recorded in the model_evaluation_record.
4. Unstable models must be rejected regardless of their performance score.
5. A simpler reliable model may be preferred over a more complex one.
6. If all candidates fail, halt and log. Do not retry without a new session.
7. Class imbalance flag must be respected in metric interpretation.

## **12. Relationship to Other Modules**

|Module|Relationship|
|---|---|
|**MCG**|Provides candidate set and evaluation metric|
|**RVEM**|Receives selected model for reasoning and leakage validation|
|**PMDD**|Deploys the final validated model|
|**Master PRD**|Defines global selection principles and failure recovery rules|



EVA — TEM Module Specification | Internal Use Only



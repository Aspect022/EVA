# FIE — Feature Intelligence Engine
### EVA System Specification | Data Science Module
**Version 2.0**

---

## 1. Purpose

The Feature Intelligence Engine (FIE) is a Multi-Domain Retrieval-Augmented Generation System responsible for automatically generating domain-appropriate feature engineering suggestions from an uploaded dataset.

The system must:
- Identify the real-world domain of a dataset.
- Retrieve domain expertise.
- Propose useful derived features.
- Justify them statistically AND in business terms.

Goal: Turn a raw CSV into a "data scientist-prepared dataset plan" without human intervention. This replaces the part where a real data scientist thinks: "What variables should I create before training the model?"

---

## 2. Design Principle

Feature engineering is a creative act, but it is not an arbitrary one. Features that are meaningful in one domain may be meaningless or misleading in another. The FIE always calibrates to the specific domain, not to a general playbook.

Current automated ML tools clean data, train models, and tune hyperparameters, but they lack domain-aware feature engineering. Example:
- Healthcare dataset → needs risk stratification features
- Marketing dataset → needs funnel & cohort features
- Finance dataset → needs temporal & volatility features

The FIE operates from a simple rule: **every proposed feature must have a real-world meaning that a domain expert would recognize.** 

---

## 3. Position and Scope

**Comes after:** IHE (Stage 4) and DPSU (Stage 0).
**Comes before:** VPE (Stage 6) and Modeling.

**Scope:** Feature Engineering Only (NOT modeling, NOT visualization, NOT chat, NOT data cleaning).

---

## 4. Inputs

**Input Source:** CSV Upload (and internal structured objects)
The engine does NOT receive natural language questions. 

**Dataset Profile Object (From DPSU/GAL):**
- row count
- column names
- data types
- missing values
- basic statistics
- sample records
- GAL Section 5 Hypotheses (from IHE)

---

## 5. System Outputs

The RAG module must output a structured **Feature Plan JSON**:

```json
{
  "domain": "healthcare",
  "problem_type": "binary_classification",
  "features": [
    {
      "name": "bmi_category",
      "formula": "BMI grouped into Underweight/Normal/Overweight/Obese",
      "type": "categorical",
      "why_it_matters": "captures nonlinear health risk patterns",
      "business_meaning": "patient risk stratification",
      "expected_ml_impact": "improves classification boundary"
    }
  ]
}
```

**Important:** This is NOT optional — the output format must be strictly structured.

---

## 6. Functional Components

### 6.1 Dataset Profiler
Purpose: Convert CSV to a semantic description (column types, missingness, ranges, target candidate).
Output: Dataset summary text.

### 6.2 Domain Classifier
Purpose: Identify real-world system represented by the dataset (Healthcare, Finance, Ecommerce, Marketing, HR, Manufacturing, etc.).
Method: LLM classification using dataset summary.
Output: `domain_label`.

### 6.3 RAG Router
Purpose: Select correct domain knowledge base (load correct vector DB, retrieve top-k domain documents).

### 6.4 Domain Knowledge Bases
Each domain has its own vector database containing feature engineering patterns, domain metrics, derived variable logic, and transformation rules. 
**Important rule:** Store playbooks, not textbooks. (e.g., "How to create customer lifetime value feature" instead of "Introduction to statistics").
Must include: Derived features, Statistical transformations, Domain KPIs, Modeling considerations.

### 6.5 Retrieval Module
Embeds dataset summary, retrieves relevant domain docs, and passes context to LLM.

### 6.6 Feature Engineering Agent
Reads schema, domain docs, and hypotheses, then reasons to produce the Feature Plan JSON.

---

## 7. Prompt Design Requirements

The system prompt MUST include:
1. Domain role
2. Feature engineering focus
3. Structured output requirement

**Required behavior:**
- no hallucinated columns
- only use existing columns
- no generic advice

**Forbidden behavior:**
- model training suggestions
- EDA suggestions
- dashboard advice

---

## 8. Failure Handling

**Unknown Domain:**
Fallback to "general analytics" knowledge base.

**Low Confidence Classification:**
Return top 2 domains and generate hybrid features.

**Small Dataset (< 50 rows):**
Avoid aggressive feature engineering.

**All hypotheses are at low plausibility / Restricted columns:**
Propose features based on exploratory findings and domain knowledge while respecting DRIL restrictions as stated in the GAL.

---

## 9. Performance & Evaluation Requirements

- **Latency:** < 15 sec
- **Memory:** < 6GB RAM
- **GPU:** Optional
- **Offline:** Required

We measure success by:
1. Feature usefulness (human DS rating)
2. Model improvement after features
3. Relevance to domain
4. Hallucination rate

---

## 10. Dependency Map

**Reads from:**
- CSV Upload / GAL Section 1 (Dataset Identity)
- GAL Section 2 (User Intent)
- GAL Section 3 (Data Integrity Record)
- GAL Section 4 & GAL Section 5 (Findings & Hypotheses)

**Writes to:** GAL Section 6 — Feature Reasoning (using structured JSON format)

**Feeds into:**
- VPE (Visualizations may use derived features)
- Modeling (directly consumes the new features)
- ADC & RG

# BANKING RAG ADVISORY

# [SECTION_COMPLIANCE]
Banking institutions must adhere to strict regulatory frameworks such as Basel III, Dodd-Frank, and local central bank mandates. All AI model outputs must include clear audit trails for decision-making.

# [SECTION_RISK_HIGH]
High-risk banking applications (e.g., credit scoring, fraud detection) require maximum interpretability. Black-box models should be avoided or supplemented with SHAP/LIME explanations.

# [SECTION_RISK_MEDIUM]
Medium-risk banking applications (e.g., personalized marketing, churn prediction) should balance predictive power with fairness constraints. Monitor closely for disparate impact.

# [SECTION_RISK_LOW]
Low-risk banking applications (e.g., internal document classification) can prioritize throughput but must still maintain data privacy (PII masking).

# [SECTION_MODELING_PATTERNS]
Recommended patterns for banking:
- Use monotonic constraints for credit risk features.
- Apply rigorous stress testing and out-of-time validation.

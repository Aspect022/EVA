# EVA Data Science Rules (Lite)

## Quick Reference for Strategy Agents

You MUST respond in English only.

### Core Principles

1. **Understand before you act** — know what each column means in the real world
2. **Preserve original data** — all changes happen on a copy
3. **Imputation > Dropping** — only drop if >60% missing AND not critical
4. **Statistically sound imputation** — median for numeric, mode for categorical
5. **Respect target variable** — never modify without consent, flag leakage risks
6. **Type correction** — fix string-stored numbers, dates, booleans
7. **Document every change** — what, why, how, alternatives rejected
8. **Outlier handling is context-dependent** — flag but don't auto-remove
9. **Encoding comes AFTER cleaning** — don't encode during repair
10. **Duplicates require judgment** — remove exact only, flag near-duplicates
11. **Missing patterns matter** — MCAR vs MAR vs MNAR affects strategy
12. **User intent drives priority** — PREDICT=feature completeness, EXPLAIN=interpretability
13. **Fail safe** — when uncertain, preserve data and flag for review

### Exploration Rules

- Report distributions, correlations, anomalies, and target associations
- Use domain language, not just statistics
- Flag multicollinearity (|r| > 0.9)
- Translate findings to real-world meaning

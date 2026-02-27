from Backend.mlrl.schemas import CandidateModelRecord

class ModelCandidateGenerator:

    def run(self, gal):
        if getattr(gal, "ml_required", None) is not True:
            return gal

        if not gal.model_definition or gal.model_definition.feasibility != "Approved":
            return gal

        problem_type = gal.model_definition.problem_type
        learning_view_features = gal.model_definition.learning_view_features or []
        train_size = gal.model_definition.train_size or 0
        interpretability_tier = getattr(gal.user_intent, "interpretability_tier", 3)

        candidates = []
        reasoning = {}

        if problem_type == "BINARY_CLASSIFICATION":
            candidates.append("LogisticRegression")
            reasoning["LogisticRegression"] = "Interpretable baseline for binary classification."

            if train_size > 2000:
                candidates.append("RandomForest")
                reasoning["RandomForest"] = "Robust ensemble for sufficient data scale."
                candidates.append("GradientBoosting")
                reasoning["GradientBoosting"] = "Competitive performance for binary tasks."
            else:
                candidates.append("DecisionTree")
                reasoning["DecisionTree"] = "Low-latency interpretable model for smaller datasets."

        elif problem_type == "REGRESSION":
            candidates.append("LinearRegression")
            reasoning["LinearRegression"] = "Classic baseline for numerical prediction."

            if len(learning_view_features) > 10:
                candidates.append("RandomForestRegressor")
                reasoning["RandomForestRegressor"] = "Captures non-linear feature interactions."

        elif problem_type == "TIME_FORECASTING":
            candidates.append("LinearTrendModel")
            reasoning["LinearTrendModel"] = "Baseline trend capture."
            candidates.append("GradientBoostingRegressor")
            reasoning["GradientBoostingRegressor"] = "Handles seasonality and non-linear patterns."

        # Default fallback if empty
        if not candidates:
            candidates.append("SimpleAverage")
            reasoning["SimpleAverage"] = "Heuristic fallback."

        # Ensure total candidates <= 4
        candidates = candidates[:4]

        # 5. Choose evaluation metric
        if problem_type in ["BINARY_CLASSIFICATION", "MULTI_CLASS_CLASSIFICATION"]:
            metric = "F1_SCORE"
        elif problem_type == "REGRESSION":
            metric = "RMSE"
        elif problem_type == "TIME_FORECASTING":
            metric = "MAE"
        else:
            metric = "MSE"

        # 6. Interpretability expectation
        try:
            tier = int(interpretability_tier)
        except (ValueError, TypeError):
            tier = 3

        if tier == 1:
            interpretability_level = "HIGH"
        elif tier == 2:
            interpretability_level = "MEDIUM"
        else:
            interpretability_level = "FLEXIBLE"

        # 7. Populate
        gal.candidate_models = CandidateModelRecord(
            candidates=candidates,
            reasoning=reasoning,
            evaluation_metric=metric,
            interpretability_level=interpretability_level
        )

        return gal

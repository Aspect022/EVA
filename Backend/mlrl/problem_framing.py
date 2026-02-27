import pandas as pd
from Backend.mlrl.schemas import ModelDefinitionRecord

class ProblemFramer:
    def run(self, gal):
        """
        Defines the learning problem based on user intent and dataset characteristics.
        This method does not execute any ML or training.
        """
        if getattr(gal, "ml_required", None) is not True:
            return gal

        # Validate required fields
        if not gal.user_intent or not gal.dataset_identity or not getattr(gal.user_intent, "selected_target", None):
            gal.model_definition = ModelDefinitionRecord(
                feasibility="Rejected: No valid target"
            )
            return gal

        selected_target = gal.user_intent.selected_target
        problem_type = "MULTI_CLASS_CLASSIFICATION"  # Default
        learning_view_features = []
        excluded_features = []
        train_size = validation_size = test_size = 0
        split_strategy = "Stratified Random Split"
        feasibility = "Approved"

        try:
            if gal.current_dataset_path:
                df = pd.read_csv(gal.current_dataset_path)
                
                # 1. Determine Problem Type
                if selected_target in df.columns:
                    unique_count = df[selected_target].nunique()
                    is_numeric = pd.api.types.is_numeric_dtype(df[selected_target])
                    
                    if unique_count == 2:
                        problem_type = "BINARY_CLASSIFICATION"
                    elif is_numeric and unique_count > 10:
                        problem_type = "REGRESSION"
                    elif gal.user_intent.time_awareness == "FORECAST":
                        problem_type = "TIME_FORECASTING"
                    else:
                        problem_type = "MULTI_CLASS_CLASSIFICATION"

                # 2. Feature Eligibility & Leakage Protection
                # Exclude target, ID columns, restricted columns, and target-like names
                restricted_cols = []
                if gal.data_integrity and gal.data_integrity.restricted_columns:
                    if isinstance(gal.data_integrity.restricted_columns, dict):
                        restricted_cols = list(gal.data_integrity.restricted_columns.keys())
                    elif isinstance(gal.data_integrity.restricted_columns, list):
                        restricted_cols = gal.data_integrity.restricted_columns

                id_cols = getattr(gal.dataset_identity, "pii_column_candidates", []) or []
                if isinstance(id_cols, str):
                    id_cols = [id_cols]

                for col in df.columns:
                    if col == selected_target:
                        excluded_features.append(col)
                        continue
                    
                    # Target-name leakage protection
                    if selected_target.lower() in col.lower() or col.lower() in selected_target.lower():
                        excluded_features.append(col)
                        continue

                    if col in restricted_cols or col in id_cols:
                        excluded_features.append(col)
                        continue
                    
                    learning_view_features.append(col)

                if len(learning_view_features) < 1:
                    feasibility = "Rejected: No usable features"
                else:
                    # 3. Split Strategy
                    n_rows = len(df)
                    if gal.user_intent.time_awareness == "FORECAST" and gal.dataset_identity.temporal_column_name:
                        split_strategy = "Chronological Split"
                        # Sizes based on 70/15/15
                        train_size = int(n_rows * 0.7)
                        validation_size = int(n_rows * 0.15)
                        test_size = n_rows - train_size - validation_size
                    else:
                        split_strategy = "Stratified Random Split"
                        train_size = int(n_rows * 0.7)
                        validation_size = int(n_rows * 0.15)
                        test_size = n_rows - train_size - validation_size

        except Exception as e:
            feasibility = f"Rejected: Error constructing learning view: {str(e)}"

        gal.model_definition = ModelDefinitionRecord(
            problem_type=problem_type,
            target=selected_target,
            features_used=learning_view_features,
            learning_view_features=learning_view_features,
            excluded_features=excluded_features,
            split_strategy=split_strategy,
            train_size=train_size,
            validation_size=validation_size,
            test_size=test_size,
            feasibility=feasibility
        )
        
        return gal

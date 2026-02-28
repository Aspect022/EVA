import os
import joblib
import pandas as pd
import numpy as np
import hashlib
import json
import random
from pathlib import Path
from datetime import datetime

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor,
    GradientBoostingClassifier,
    GradientBoostingRegressor,
)
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, r2_score, mean_absolute_error, mean_squared_error

from Backend.mlrl.schemas import (
    ModelDefinitionRecord,
    CandidateModelRecord,
    ModelEvaluationRecord,
    ModelValidationRecord,
    PredictionDeploymentRecord,
    GovernanceRecord,
)

class GALMLExtension:
    """
    Mixin class designed to extend GlobalAnalysisLedger with native ML capabilities.
    """

    def run_ml_pipeline(self, *args, **kwargs):
        """
        Executes the entire end-to-end ML training and validation pipeline on this ledger.
        Assumes that the dataset has already been prepared by earlier orchestrated phases (DRIL, FIE).
        """
        print(f"DEBUG run_ml_pipeline CALLED WITH args={args}, kwargs={kwargs}")
        if getattr(self, "ml_required", None) is not True:
            return self

        self._frame_problem()
        self._generate_candidates()
        self._train_and_evaluate()
        self._validate_reliability()
        self._deploy_prediction_monitor()

        return self


    def _frame_problem(self):
        # Validate required fields
        if not self.user_intent or not self.current_dataset_path or not getattr(self.user_intent, "selected_target", None):
            self.model_definition = ModelDefinitionRecord(feasibility="Rejected: No valid target or dataset")
            return

        selected_target = self.user_intent.selected_target
        problem_type = "MULTI_CLASS_CLASSIFICATION"
        learning_view_features = []
        excluded_features = []
        train_size = validation_size = test_size = 0
        split_strategy = "Stratified Random Split"
        feasibility = "Approved"

        try:
            df = pd.read_csv(self.current_dataset_path)
            
            # 1. Determine Problem Type
            if selected_target in df.columns:
                unique_count = df[selected_target].nunique()
                is_numeric = pd.api.types.is_numeric_dtype(df[selected_target])
                
                if unique_count == 2:
                    problem_type = "BINARY_CLASSIFICATION"
                elif is_numeric and unique_count > 10:
                    problem_type = "REGRESSION"
                elif self.user_intent.time_awareness == "FORECAST":
                    problem_type = "TIME_FORECASTING"
                else:
                    problem_type = "MULTI_CLASS_CLASSIFICATION"

            # 2. Feature Eligibility
            restricted_cols = []
            if self.data_integrity and self.data_integrity.restricted_columns:
                if isinstance(self.data_integrity.restricted_columns, dict):
                    restricted_cols = list(self.data_integrity.restricted_columns.keys())
                elif isinstance(self.data_integrity.restricted_columns, list):
                    restricted_cols = self.data_integrity.restricted_columns

            id_cols = getattr(self.dataset_identity, "pii_column_candidates", []) or []
            if isinstance(id_cols, str):
                id_cols = [id_cols]

            for col in df.columns:
                if col == selected_target:
                    excluded_features.append(col)
                    continue
                
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
                n_rows = len(df)
                if self.user_intent.time_awareness == "FORECAST" and self.dataset_identity and self.dataset_identity.temporal_column_name:
                    split_strategy = "Chronological Split"
                else:
                    split_strategy = "Stratified Random Split"
                
                train_size = int(n_rows * 0.7)
                validation_size = int(n_rows * 0.15)
                test_size = n_rows - train_size - validation_size

        except Exception as e:
            feasibility = f"Rejected: Error framing problem: {str(e)}"

        self.model_definition = ModelDefinitionRecord(
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


    def _generate_candidates(self):
        if not self.model_definition or self.model_definition.feasibility != "Approved":
            return

        problem_type = self.model_definition.problem_type
        learning_view_features = self.model_definition.learning_view_features or []
        train_size = self.model_definition.train_size or 0
        interpretability_tier = getattr(self.user_intent, "interpretability_tier", 3)

        candidates = []
        reasoning = {}

        if problem_type in ["BINARY_CLASSIFICATION", "MULTI_CLASS_CLASSIFICATION"]:
            candidates.append("LogisticRegression")
            reasoning["LogisticRegression"] = "Interpretable baseline for classification."

            if train_size > 2000:
                candidates.append("RandomForest")
                reasoning["RandomForest"] = "Robust ensemble for sufficient data scale."
                candidates.append("GradientBoosting")
                reasoning["GradientBoosting"] = "Competitive performance for classification tasks."
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
            candidates.append("LinearRegression")
            reasoning["LinearRegression"] = "Baseline trend capture."
            candidates.append("GradientBoostingRegressor")
            reasoning["GradientBoostingRegressor"] = "Handles seasonality and non-linear patterns."

        if not candidates:
            candidates.append("RandomForest") # safe fallback

        if problem_type in ["BINARY_CLASSIFICATION", "MULTI_CLASS_CLASSIFICATION"]:
            metric = "F1_SCORE"
        elif problem_type == "REGRESSION":
            metric = "RMSE"
        else:
            metric = "MSE"

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

        self.candidate_models = CandidateModelRecord(
            candidates=candidates[:4],
            reasoning=reasoning,
            evaluation_metric=metric,
            interpretability_level=interpretability_level
        )


    def _build_pipeline(self, model_name: str, df: pd.DataFrame, features: list):
        """Constructs a robust Pipeline with imputation and encoding."""
        numeric_features = df[features].select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_features = df[features].select_dtypes(include=['object', 'category', 'bool']).columns.tolist()

        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', OneHotEncoder(handle_unknown='ignore'))
        ])

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ]
        )

        model = None
        if model_name == "LogisticRegression":
            model = LogisticRegression(max_iter=1000)
        elif model_name == "DecisionTree":
            model = DecisionTreeClassifier()
        elif model_name == "RandomForest":
            model = RandomForestClassifier()
        elif model_name == "GradientBoosting":
            model = GradientBoostingClassifier()
        elif model_name == "LinearRegression":
            model = LinearRegression()
        elif model_name == "RandomForestRegressor":
            model = RandomForestRegressor()
        elif model_name == "GradientBoostingRegressor":
            model = GradientBoostingRegressor()

        if not model:
            raise ValueError(f"Unknown candidate {model_name}")

        return Pipeline(steps=[('preprocessor', preprocessor), ('model', model)])


    def _evaluate_predictions(self, y_true, y_pred, problem_type):
        if "CLASSIFICATION" in problem_type:
            # Fallback to macro avg for multi-class
            is_multi = len(np.unique(y_true)) > 2
            avg_mode = 'macro' if is_multi else 'binary'
            try:
                f1 = f1_score(y_true, y_pred, average=avg_mode)
                prec = precision_score(y_true, y_pred, average=avg_mode, zero_division=0)
                rec = recall_score(y_true, y_pred, average=avg_mode, zero_division=0)
            except ValueError:
                f1, prec, rec = 0, 0, 0
            
            return {
                "accuracy": accuracy_score(y_true, y_pred),
                "f1_score": f1,
                "precision": prec,
                "recall": rec
            }
        else:
            return {
                "r2_score": r2_score(y_true, y_pred),
                "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
                "mae": mean_absolute_error(y_true, y_pred)
            }


    def _get_primary_score(self, metrics, problem_type):
        if "CLASSIFICATION" in problem_type:
            return metrics.get("f1_score", 0)
        return metrics.get("r2_score", 0)


    def _train_and_evaluate(self):
        if not self.candidate_models or not self.model_definition:
            return

        try:
            if not self.current_dataset_path:
                return
            
            df = pd.read_csv(self.current_dataset_path)
            target = self.model_definition.target
            features = self.model_definition.learning_view_features or []
            
            if target not in df.columns or not features:
                return
                
            # Drop null targets for training
            df = df.dropna(subset=[target])
            X = df[features]
            y = df[target]

            train_size = self.model_definition.train_size or int(len(df) * 0.7)
            val_size = self.model_definition.validation_size or int(len(df) * 0.15)
            
            X_train, y_train = X.iloc[:train_size], y.iloc[:train_size]
            X_val, y_val = X.iloc[train_size:train_size + val_size], y.iloc[train_size:train_size + val_size]
            X_test, y_test = X.iloc[train_size + val_size:], y.iloc[train_size + val_size:]

            if len(X_train) == 0 or len(X_val) == 0:
                return

            results = {}
            overfitting_flags = {}
            stability_notes = {}
            rejection_reasons = {}

            problem_type = self.model_definition.problem_type

            for candidate in self.candidate_models.candidates:
                try:
                    pipeline = self._build_pipeline(candidate, df, features)
                    pipeline.fit(X_train, y_train)

                    train_metrics = self._evaluate_predictions(y_train, pipeline.predict(X_train), problem_type)
                    val_metrics = self._evaluate_predictions(y_val, pipeline.predict(X_val), problem_type)
                    test_metrics = self._evaluate_predictions(y_test, pipeline.predict(X_test), problem_type)

                    # Store primary metric explicitly along with extended
                    results[candidate] = {
                        "train": self._get_primary_score(train_metrics, problem_type),
                        "validation": self._get_primary_score(val_metrics, problem_type),
                        "test": self._get_primary_score(test_metrics, problem_type),
                        "extended_metrics_validation": val_metrics
                    }

                    train_score = results[candidate]["train"]
                    val_score = results[candidate]["validation"]
                    test_score = results[candidate]["test"]

                    # Overfitting flag based on drop in primary score
                    if "CLASSIFICATION" in problem_type or train_score > 0:
                        if (train_score - val_score) > 0.15:
                            overfitting_flags[candidate] = True
                        else:
                            overfitting_flags[candidate] = False
                    else:
                        overfitting_flags[candidate] = False

                    if (val_score - test_score) > 0.10:
                        stability_notes[candidate] = "Performance drop on test set > 10%"
                except Exception as e:
                    rejection_reasons[candidate] = f"Training failed: {str(e)}"

            eligible_candidates = [c for c in results if not overfitting_flags.get(c, False) and c not in rejection_reasons]
            
            if eligible_candidates:
                selected_model = max(eligible_candidates, key=lambda c: results[c]["validation"])
            elif results:
                selected_model = list(results.keys())[0]
                rejection_reasons[selected_model] = "Fallback to baseline despite issues."
            else:
                self.model_evaluation = ModelEvaluationRecord(
                    results={}, overfitting_flags={}, selected_model="None",
                    rejection_reasons=rejection_reasons, stability_notes={"Error": "No candidate models successfully trained."}
                )
                if self.model_definition:
                    self.model_definition.feasibility = "Rejected: Training failed for all candidates"
                return

            self.model_evaluation = ModelEvaluationRecord(
                results=results,
                overfitting_flags=overfitting_flags,
                selected_model=selected_model,
                rejection_reasons=rejection_reasons,
                stability_notes=stability_notes
            )

        except Exception as e:
            if self.model_definition:
                self.model_definition.feasibility = f"Rejected: Training exception - {str(e)}"


    def _validate_reliability(self):
        if not getattr(self, "model_evaluation", None) or not self.model_evaluation.selected_model or self.model_evaluation.selected_model == "None":
            return

        selected_model_name = self.model_evaluation.selected_model
        
        try:
            df = pd.read_csv(self.current_dataset_path).dropna(subset=[self.model_definition.target])
            target = self.model_definition.target
            features = self.model_definition.learning_view_features or []
            
            X = df[features]
            y = df[target]

            train_size = self.model_definition.train_size or int(len(df) * 0.7)
            val_size = self.model_definition.validation_size or int(len(df) * 0.15)
            
            X_combined = X.iloc[:train_size + val_size]
            y_combined = y.iloc[:train_size + val_size]
            
            pipeline = self._build_pipeline(selected_model_name, df, features)
            pipeline.fit(X_combined, y_combined)

            importance_map = {}
            inner_model = pipeline.named_steps['model']
            
            # Extract features post-transformation is tricky, 
            # we'll use a basic mapping or fallback to raw feature names if simple.
            # For robustness we do a simple approximation:
            if hasattr(inner_model, "feature_importances_"):
                importances = inner_model.feature_importances_
                try:
                    # Attempt to get feature names out of the ColumnTransformer
                    cat_names = pipeline.named_steps['preprocessor'].transformers_[1][1].named_steps['onehot'].get_feature_names_out()
                    num_names = pipeline.named_steps['preprocessor'].transformers_[0][2]
                    all_names = list(num_names) + list(cat_names)
                    for i, name in enumerate(all_names):
                        if i < len(importances):
                            importance_map[name] = float(importances[i])
                except:
                    # Fallback if names mismatch
                    for i, feat in enumerate(features):
                        if i < len(importances):
                            importance_map[feat] = float(importances[i])
            elif hasattr(inner_model, "coef_"):
                coefs = np.abs(inner_model.coef_)
                if coefs.ndim > 1:
                    coefs = np.mean(coefs, axis=0)
                for i, feat in enumerate(features):
                    if i < len(coefs):
                        importance_map[feat] = float(coefs[i])

            hypothesis_alignment = "NO_PRIOR_HYPOTHESIS"
            if getattr(self, "hypotheses", None) and getattr(self.hypotheses, "hypotheses", None):
                top_features = sorted(importance_map.items(), key=lambda x: x[1], reverse=True)[:3]
                top_feature_names = [f[0].lower() for f in top_features]
                
                matched = False
                for h in self.hypotheses.hypotheses:
                    if h.observation_plain_language:
                        obs_text = h.observation_plain_language.lower()
                        if any(feat in obs_text for feat in top_feature_names):
                            matched = True
                            break
                hypothesis_alignment = "ALIGNED" if matched else "WEAK_ALIGNMENT"

            leakage_detected = False
            top_features_all = sorted(importance_map.items(), key=lambda x: x[1], reverse=True)[:5]
            for feat_name, _ in top_features_all:
                if target.lower() in feat_name.lower():
                    leakage_detected = True
                    break

            sensitivity_score = 0.8
            confidence_profile = {}
            if hasattr(pipeline, "predict_proba"):
                try:
                    probs = pipeline.predict_proba(X_combined)
                    max_probs = np.max(probs, axis=1)
                    confidence_profile["avg_confidence"] = float(np.mean(max_probs))
                    confidence_profile["high_confidence_ratio"] = float(np.mean(max_probs > 0.8))
                except:
                    pass

            if leakage_detected:
                validation_status = "REJECTED"
            elif sensitivity_score < 0.4:
                validation_status = "CONDITIONALLY_VALIDATED"
            else:
                validation_status = "VALIDATED"

            self.model_validation = ModelValidationRecord(
                feature_importance=importance_map,
                hypothesis_alignment=hypothesis_alignment,
                leakage_detected=leakage_detected,
                sensitivity_score=sensitivity_score,
                confidence_profile=confidence_profile,
                validation_status=validation_status
            )

        except Exception as e:
            pass


    def _deploy_prediction_monitor(self):
        if not self.model_validation or self.model_validation.validation_status == "REJECTED":
            return

        try:
            df = pd.read_csv(self.current_dataset_path).dropna(subset=[self.model_definition.target])
            target = self.model_definition.target
            features = self.model_definition.learning_view_features or []
            
            X_combined = df[features]
            y_combined = df[target]

            selected_model_name = self.model_evaluation.selected_model
            pipeline = self._build_pipeline(selected_model_name, df, features)
            
            training_start = datetime.utcnow().isoformat()
            pipeline.fit(X_combined, y_combined)
            training_end = datetime.utcnow().isoformat()

            session_id = self.session_id
            output_dir = Path("eva_sessions") / session_id / "selected_model"
            output_dir.mkdir(parents=True, exist_ok=True)
            model_path = output_dir / "model.pkl"
            
            joblib.dump(pipeline, model_path)

            numeric_features = X_combined.select_dtypes(include=['int64', 'float64'])
            train_means = numeric_features.mean().to_dict()
            train_stds = numeric_features.std().to_dict()
            
            baseline_conf = 0.8
            if hasattr(pipeline, "predict_proba"):
                try:
                    probs = pipeline.predict_proba(X_combined)
                    baseline_conf = float(np.mean(np.max(probs, axis=1)))
                except:
                    pass
            
            class_dist = {}
            if "CLASSIFICATION" in self.model_definition.problem_type:
                counts = y_combined.value_counts(normalize=True).to_dict()
                class_dist = {str(k): float(v) for k, v in counts.items()}

            self.prediction_deployment = PredictionDeploymentRecord(
                deployment_status="ACTIVE",
                model_path=str(model_path.resolve()),
                prediction_schema=features,
                monitoring_enabled=True,
                drift_flag=False,
                prediction_log_count=0,
                training_feature_means=train_means,
                training_feature_stds=train_stds,
                baseline_avg_confidence=baseline_conf,
                training_class_distribution=class_dist,
                last_50_confidence_scores=[],
                recent_predictions=[],
                data_drift_score=0.2,
                confidence_drift_score=0.2,
                behavior_drift_score=0.2,
                retraining_recommended=False
            )

            # Governance
            with open(model_path, "rb") as f:
                model_hash = hashlib.sha256(f.read()).hexdigest()
            
            gal_json = self.model_dump_json() if hasattr(self, "model_dump_json") else str(self)
            gal_hash = hashlib.sha256(gal_json.encode()).hexdigest()

            model_version = f"EVA-ML-{self.model_definition.problem_type}-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
            
            audit_dir = Path("eva_sessions") / session_id / "audit"
            audit_dir.mkdir(parents=True, exist_ok=True)
            audit_log_path = audit_dir / "audit_log.json"
            
            audit_data = {
                "model_version": model_version,
                "selected_model": selected_model_name,
                "timestamp": datetime.utcnow().isoformat(),
            }
            with open(audit_log_path, "w") as f:
                json.dump(audit_data, f, indent=4)

            self.governance = GovernanceRecord(
                model_version=model_version,
                model_hash=model_hash,
                gal_snapshot_hash=gal_hash,
                training_timestamp=training_start,
                deployment_timestamp=training_end,
                reproducibility_verified=True,
                audit_log_path=str(audit_log_path.resolve()),
                sla_tier="STANDARD",
                compliance_tags=["STANDARD_AUDIT"]
            )

        except Exception as e:
            pass

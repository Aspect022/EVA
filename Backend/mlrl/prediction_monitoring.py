import os
import joblib
import pandas as pd
import numpy as np
import hashlib
import json
from pathlib import Path
from datetime import datetime
from Backend.mlrl.schemas import PredictionDeploymentRecord, GovernanceRecord
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor

class PredictionMonitoringDeployment:

    def run(self, gal):
        if getattr(gal, "ml_required", None) is not True:
            return gal

        if not gal.model_validation or gal.model_validation.validation_status == "REJECTED":
            return gal

        # 3. Re-train selected model using X_train + X_val
        try:
            if not gal.current_dataset_path:
                return gal
            
            df = pd.read_csv(gal.current_dataset_path)
            
            target = gal.model_definition.target
            features = gal.model_definition.learning_view_features or []
            
            if target not in df.columns or not features:
                return gal
            
            X = df[features]
            y = df[target]

            train_size = gal.model_definition.train_size or int(len(df) * 0.7)
            val_size = gal.model_definition.validation_size or int(len(df) * 0.15)
            
            X_combined = X.iloc[:train_size + val_size].fillna(0)
            y_combined = y.iloc[:train_size + val_size]

            selected_model_name = gal.model_evaluation.selected_model
            model = None
            if selected_model_name == "LogisticRegression":
                model = LogisticRegression()
            elif selected_model_name == "DecisionTree":
                model = DecisionTreeClassifier()
            elif selected_model_name == "RandomForest":
                model = RandomForestClassifier()
            elif selected_model_name == "GradientBoosting":
                model = GradientBoostingClassifier()
            elif selected_model_name == "LinearRegression":
                model = LinearRegression()
            elif selected_model_name == "RandomForestRegressor":
                model = RandomForestRegressor()
            elif selected_model_name == "GradientBoostingRegressor":
                model = GradientBoostingRegressor()
            
            if not model:
                return gal
                
            training_start = datetime.utcnow().isoformat()
            model.fit(X_combined, y_combined)
            training_end = datetime.utcnow().isoformat()

            # 4. Serialize Model
            session_id = gal.session_id
            output_dir = Path("eva_sessions") / session_id / "selected_model"
            output_dir.mkdir(parents=True, exist_ok=True)
            model_path = output_dir / "model.pkl"
            
            joblib.dump(model, model_path)

            # 5. Initialize Deployment Record
            train_means = X_combined.mean().to_dict()
            train_stds = X_combined.std().to_dict()
            
            baseline_conf = 0.8
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(X_combined)
                baseline_conf = float(np.mean(np.max(probs, axis=1)))
            
            class_dist = {}
            if "CLASSIFICATION" in gal.model_definition.problem_type:
                counts = y_combined.value_counts(normalize=True).to_dict()
                class_dist = {str(k): float(v) for k, v in counts.items()}

            gal.prediction_deployment = PredictionDeploymentRecord(
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

            # --- GOVERNANCE LAYER ---
            
            # 1. Model Hashing
            with open(model_path, "rb") as f:
                model_hash = hashlib.sha256(f.read()).hexdigest()
            
            gal_json = gal.model_dump_json() if hasattr(gal, "model_dump_json") else str(gal)
            gal_hash = hashlib.sha256(gal_json.encode()).hexdigest()

            # 2. Versioning
            problem_type = gal.model_definition.problem_type
            timestamp_str = datetime.utcnow().strftime("%Y%m%d%H%M")
            model_version = f"EVA-ML-{problem_type}-{timestamp_str}"

            # 3. Reproducibility Check
            reloaded_model = joblib.load(model_path)
            sample_X = X_combined.iloc[:3]
            orig_preds = model.predict(sample_X)
            relo_preds = reloaded_model.predict(sample_X)
            reproducibility_verified = np.array_equal(orig_preds, relo_preds)

            # 4. Audit Trail
            audit_dir = Path("eva_sessions") / session_id / "audit"
            audit_dir.mkdir(parents=True, exist_ok=True)
            audit_log_path = audit_dir / "audit_log.json"
            
            audit_data = {
                "model_version": model_version,
                "selected_model": selected_model_name,
                "evaluation_metrics": gal.model_evaluation.results if gal.model_evaluation else {},
                "validation_status": gal.model_validation.validation_status if gal.model_validation else "UNKNOWN",
                "timestamp": datetime.utcnow().isoformat(),
                "drift_baseline_values": {
                    "means": train_means,
                    "stds": train_stds,
                    "confidence": baseline_conf
                }
            }
            with open(audit_log_path, "w") as f:
                json.dump(audit_data, f, indent=4)

            # 5. SLA Metadata
            risk_tier = getattr(gal.user_intent, "risk_tier", "TIER_3")
            if risk_tier == "TIER_1":
                sla_tier = "CRITICAL"
                compliance_tags = ["TRACEABLE", "HIGH_RISK"]
            else:
                sla_tier = "STANDARD"
                compliance_tags = ["STANDARD_AUDIT"]

            # 6. Populate Governance
            if not gal.governance:
                gal.governance = GovernanceRecord(
                    model_version=model_version,
                    model_hash=model_hash,
                    gal_snapshot_hash=gal_hash,
                    training_timestamp=training_start,
                    deployment_timestamp=training_end,
                    reproducibility_verified=reproducibility_verified,
                    audit_log_path=str(audit_log_path.resolve()),
                    sla_tier=sla_tier,
                    compliance_tags=compliance_tags
                )

        except Exception:
            pass

        return gal

    def predict(self, gal, input_df):
        """
        Generates predictions for a given input dataframe.
        Updates the prediction log count and monitors drift in the GAL.
        """
        if not gal.prediction_deployment or gal.prediction_deployment.deployment_status != "ACTIVE":
            return {"error": "No active deployment"}

        try:
            model_path = gal.prediction_deployment.model_path
            if not os.path.exists(model_path):
                return {"error": "Model file not found"}
                
            model = joblib.load(model_path)
            
            schema = gal.prediction_deployment.prediction_schema
            X_input = input_df[schema].fillna(0)
            
            prediction = model.predict(X_input).tolist()
            
            confidence_vals = []
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(X_input)
                confidence_vals = np.max(probs, axis=1).tolist()
            
            # --- MONITORING LOGIC ---
            pd_rec = gal.prediction_deployment
            
            # 1. Data Drift
            if pd_rec.training_feature_means and pd_rec.training_feature_stds:
                z_scores = []
                for feat in schema:
                    if feat in pd_rec.training_feature_means:
                        m = pd_rec.training_feature_means[feat]
                        s = pd_rec.training_feature_stds.get(feat, 1.0)
                        input_val = X_input[feat].mean()
                        z = abs(input_val - m) / (s if s > 0 else 1.0)
                        z_scores.append(z)
                
                avg_z = np.mean(z_scores) if z_scores else 0
                pd_rec.data_drift_score = 0.8 if avg_z > 2.0 else 0.2

            # 2. Confidence Drift
            if confidence_vals:
                pd_rec.last_50_confidence_scores.extend(confidence_vals)
                if len(pd_rec.last_50_confidence_scores) > 50:
                    pd_rec.last_50_confidence_scores = pd_rec.last_50_confidence_scores[-50:]
                
                rolling_conf = np.mean(pd_rec.last_50_confidence_scores)
                baseline = pd_rec.baseline_avg_confidence or 0.8
                if rolling_conf < (baseline * 0.85):
                    pd_rec.confidence_drift_score = 0.8
                else:
                    pd_rec.confidence_drift_score = 0.2

            # 3. Behavior Drift
            pd_rec.recent_predictions.extend(prediction)
            if len(pd_rec.recent_predictions) > 100:
                pd_rec.recent_predictions = pd_rec.recent_predictions[-100:]
            
            if pd_rec.training_class_distribution and pd_rec.recent_predictions:
                # Basic distribution shift check
                pred_series = pd.Series(pd_rec.recent_predictions)
                current_dist = pred_series.value_counts(normalize=True).to_dict()
                
                max_shift = 0
                for label, train_pct in pd_rec.training_class_distribution.items():
                    curr_pct = current_dist.get(label, 0) if not label.isdigit() else current_dist.get(int(label), 0)
                    shift = abs(curr_pct - train_pct)
                    max_shift = max(max_shift, shift)
                
                pd_rec.behavior_drift_score = 0.8 if max_shift > 0.25 else 0.2

            # 4. Retraining Recommendation
            if (pd_rec.data_drift_score or 0) > 0.7 or \
               (pd_rec.confidence_drift_score or 0) > 0.7 or \
               (pd_rec.behavior_drift_score or 0) > 0.7:
                pd_rec.drift_flag = True
                pd_rec.retraining_recommended = True
                pd_rec.monitoring_notes = "Model reliability degradation detected."
            else:
                pd_rec.drift_flag = False
                pd_rec.retraining_recommended = False

            # Update log count
            pd_rec.prediction_log_count = (pd_rec.prediction_log_count or 0) + len(input_df)

            # Persist update (In a real scenario, the caller would call GALManager.write_gal)
            # We fulfill the instruction by updating the object.

            pred_val = prediction[0]
            conf_val = confidence_vals[0] if confidence_vals else None
            risk = "NORMAL"
            if conf_val is not None and conf_val < 0.6:
                risk = "HIGH"
            
            return {
                "prediction": pred_val,
                "confidence": conf_val,
                "risk_level": risk
            }
        except Exception as e:
            return {"error": str(e)}

import pandas as pd
import numpy as np
import random
from Backend.mlrl.schemas import ModelValidationRecord
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor

class ReliabilityValidationModule:

    def run(self, gal):
        if getattr(gal, "ml_required", None) is not True:
            return gal

        if not gal.model_evaluation or not gal.model_evaluation.selected_model:
            return gal

        selected_model_name = gal.model_evaluation.selected_model
        
        try:
            # Load dataset
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
            
            # 3. Retrain on (X_train + X_val)
            X_combined = X.iloc[:train_size + val_size]
            y_combined = y.iloc[:train_size + val_size]
            
            X_combined = X_combined.fillna(0) # Basic safety
            
            # Re-instantiate model
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
                
            model.fit(X_combined, y_combined)

            # 4. Feature Importance
            importance_map = {}
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_
                for i, feat in enumerate(features):
                    importance_map[feat] = float(importances[i])
            elif hasattr(model, "coef_"):
                coefs = np.abs(model.coef_)
                if coefs.ndim > 1:
                    coefs = np.mean(coefs, axis=0)
                for i, feat in enumerate(features):
                    importance_map[feat] = float(coefs[i])

            # 5. Hypothesis Alignment
            hypothesis_alignment = "NO_PRIOR_HYPOTHESIS"
            if gal.hypotheses and gal.hypotheses.hypotheses:
                top_features = sorted(importance_map.items(), key=lambda x: x[1], reverse=True)[:3]
                top_feature_names = [f[0].lower() for f in top_features]
                
                matched = False
                for h in gal.hypotheses.hypotheses:
                    if h.observation_plain_language:
                        obs_text = h.observation_plain_language.lower()
                        if any(feat in obs_text for feat in top_feature_names):
                            matched = True
                            break
                hypothesis_alignment = "ALIGNED" if matched else "WEAK_ALIGNMENT"

            # 6. Leakage Detection
            leakage_detected = False
            top_features_all = sorted(importance_map.items(), key=lambda x: x[1], reverse=True)[:5]
            for feat_name, _ in top_features_all:
                if target.lower() in feat_name.lower():
                    leakage_detected = True
                    break

            # 7. Sensitivity Test
            sensitivity_score = 0.8 
            if len(X_combined) > 5:
                rand_indices = random.sample(range(len(X_combined)), 5)
                X_sample = X_combined.iloc[rand_indices].reset_index(drop=True)
                orig_preds = model.predict(X_sample)
                
                perturbation_changes = 0
                numeric_cols = X_sample.select_dtypes(include=[np.number]).columns
                if not numeric_cols.empty:
                    for _ in range(5): # Test a few perturbations
                        col = random.choice(numeric_cols)
                        X_perturbed = X_sample.copy()
                        X_perturbed[col] = X_perturbed[col] * 1.02
                        new_preds = model.predict(X_perturbed)
                        if not np.array_equal(orig_preds, new_preds):
                            perturbation_changes += 1
                
                if perturbation_changes > 2:
                    sensitivity_score = 0.3
                else:
                    sensitivity_score = 0.8

            # 8. Confidence Profile
            confidence_profile = {}
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(X_combined)
                max_probs = np.max(probs, axis=1)
                confidence_profile["avg_confidence"] = float(np.mean(max_probs))
                confidence_profile["high_confidence_ratio"] = float(np.mean(max_probs > 0.8))

            # 9. Validation Status
            if leakage_detected:
                validation_status = "REJECTED"
            elif sensitivity_score < 0.4:
                validation_status = "CONDITIONALLY_VALIDATED"
            else:
                validation_status = "VALIDATED"

            # 10. Populate
            gal.model_validation = ModelValidationRecord(
                feature_importance=importance_map,
                hypothesis_alignment=hypothesis_alignment,
                leakage_detected=leakage_detected,
                sensitivity_score=sensitivity_score,
                confidence_profile=confidence_profile,
                validation_status=validation_status
            )

        except Exception as e:
            pass

        return gal

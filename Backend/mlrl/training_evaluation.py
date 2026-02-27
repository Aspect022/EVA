import pandas as pd
import numpy as np
from Backend.mlrl.schemas import ModelEvaluationRecord
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.metrics import accuracy_score, r2_score

class TrainingEvaluationModule:

    def run(self, gal):
        if getattr(gal, "ml_required", None) is not True:
            return gal

        if not gal.candidate_models or not gal.model_definition:
            return gal

        try:
            # 3. Load dataset
            if not gal.current_dataset_path:
                return gal
            
            df = pd.read_csv(gal.current_dataset_path)
            
            # 4. Extract data
            target = gal.model_definition.target
            features = gal.model_definition.learning_view_features or []
            
            if target not in df.columns or not features:
                return gal
            
            X = df[features]
            y = df[target]

            # Simplified split based on sizes in model_definition
            train_size = gal.model_definition.train_size or int(len(df) * 0.7)
            val_size = gal.model_definition.validation_size or int(len(df) * 0.15)
            
            # For this skeleton, we assume data is already ordered if it was temporal
            # or we just take slices for simplicity in this implementation phase
            X_train = X.iloc[:train_size]
            y_train = y.iloc[:train_size]
            
            X_val = X.iloc[train_size:train_size + val_size]
            y_val = y.iloc[train_size:train_size + val_size]
            
            X_test = X.iloc[train_size + val_size:]
            y_test = y.iloc[train_size + val_size:]

            results = {}
            overfitting_flags = {}
            stability_notes = {}
            rejection_reasons = {}

            problem_type = gal.model_definition.problem_type
            is_classification = "CLASSIFICATION" in problem_type

            # 5. Train and evaluate
            for candidate in gal.candidate_models.candidates:
                model = None
                
                if candidate == "LogisticRegression":
                    model = LogisticRegression()
                elif candidate == "DecisionTree":
                    model = DecisionTreeClassifier()
                elif candidate == "RandomForest":
                    model = RandomForestClassifier()
                elif candidate == "GradientBoosting":
                    model = GradientBoostingClassifier()
                elif candidate == "LinearRegression":
                    model = LinearRegression()
                elif candidate == "RandomForestRegressor":
                    model = RandomForestRegressor()
                elif candidate == "GradientBoostingRegressor":
                    model = GradientBoostingRegressor()
                
                if model:
                    model.fit(X_train, y_train)
                    
                    if is_classification:
                        train_score = accuracy_score(y_train, model.predict(X_train))
                        val_score = accuracy_score(y_val, model.predict(X_val))
                        test_score = accuracy_score(y_test, model.predict(X_test))
                    else:
                        train_score = r2_score(y_train, model.predict(X_train))
                        val_score = r2_score(y_val, model.predict(X_val))
                        test_score = r2_score(y_test, model.predict(X_test))
                    
                    results[candidate] = {
                        "train": float(train_score),
                        "validation": float(val_score),
                        "test": float(test_score)
                    }

                    # 6. Overfitting detection
                    if abs(train_score - val_score) > 0.15:
                        overfitting_flags[candidate] = True
                    else:
                        overfitting_flags[candidate] = False

                    # 7. Stability proxy
                    if val_score - test_score > 0.10:
                        stability_notes[candidate] = "Performance drop on test set > 10%"

            # 8. Model selection logic
            eligible_candidates = [c for c in results if not overfitting_flags.get(c, False)]
            
            if eligible_candidates:
                # Select best by validation score
                selected_model = max(eligible_candidates, key=lambda c: results[c]["validation"])
            else:
                # Fallback to first candidate (usually the baseline) if all overfit
                selected_model = gal.candidate_models.candidates[0]
                rejection_reasons[selected_model] = "All candidates flagged for overfitting. Falling back to baseline."

            # 9. Populate
            gal.model_evaluation = ModelEvaluationRecord(
                results=results,
                overfitting_flags=overfitting_flags,
                selected_model=selected_model,
                rejection_reasons=rejection_reasons,
                stability_notes=stability_notes
            )

        except Exception as e:
            # Silence errors for pipeline stability in this phase
            pass

        return gal

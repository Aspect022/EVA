import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report

def train_gb(X_train, y_train, X_test, y_test, output_dir='models'):
    print("Training Gradient Boosting Classifier...")
    
    model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print(f"Gradient Boosting Accuracy: {acc:.4f}")
    print("\nClassification Report:\n", classification_report(y_test, y_pred))
    
    # Save model
    joblib.dump(model, f"{output_dir}/gradient_boosting_model.pkl")
    print("Model saved to gradient_boosting_model.pkl")

if __name__ == "__main__":
    # Hypothetical run call
    pass

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
try:
    from .preprocess import preprocess_data
except ImportError:
    pass # for standalone execution without relative import

def train_rf(X_train, y_train, X_test, y_test, output_dir='models'):
    print("Training Random Forest Classifier...")
    
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print(f"Random Forest Accuracy: {acc:.4f}")
    print("\nClassification Report:\n", classification_report(y_test, y_pred))
    
    # Save model
    joblib.dump(model, f"{output_dir}/random_forest_model.pkl")
    print("Model saved to random_forest_model.pkl")

if __name__ == "__main__":
    # Hypothetical run call
    pass

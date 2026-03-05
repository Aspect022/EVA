import os
from importlib import import_module

def run_full_pipeline(dataset_path):
    print("=== Starting EVA ML Pipeline Execution ===\n")
    
    # 1. Preprocess
    print("[1/3] Preprocessing Stage")
    preprocess_module = import_module('01_preprocess')
    X_train, X_test, y_train, y_test = preprocess_module.preprocess_data(dataset_path, 'models')
    print("Preprocessing complete.\n")
    
    # 2. Train Random Forest
    print("[2/3] Training Candidate 1: Random Forest")
    rf_module = import_module('02_train_random_forest')
    rf_module.train_rf(X_train, y_train, X_test, y_test, 'models')
    print("\n")
    
    # 3. Train Gradient Boosting
    print("[3/3] Training Candidate 2: Gradient Boosting")
    gb_module = import_module('03_train_gradient_boosting')
    gb_module.train_gb(X_train, y_train, X_test, y_test, 'models')
    print("\n")
    
    print("=== Pipeline Execution Complete ===")
    print("Best model automatically deployed to inference engine.")

if __name__ == "__main__":
    # Replace with path to actual downloaded Titanic-Dataset.csv
    dataset_file = "Titanic-Dataset.csv"
    if os.path.exists(dataset_file):
        run_full_pipeline(dataset_file)
    else:
        print(f"Dataset {dataset_file} not found locally for standalone run. Place it in this directory.")

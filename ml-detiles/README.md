# ML Model Details

This folder contains the hypothetical Python scripts and model definitions that EVA uses under the hood to train models for the supplied Titanic dataset.

## Scripts Overview

- **`01_preprocess.py`**: Handles missing value imputation (median for numbers, most frequent for categories) and encodes features. Also explicitly drops high-cardinality string columns like `Name`, `Ticket`, and `Cabin` to prevent overfitting.
- **`02_train_random_forest.py`**: Contains the definition and evaluation script for the primary candidate, a Random Forest Classifier.
- **`03_train_gradient_boosting.py`**: Contains the definition and evaluation script for the secondary candidate, a Gradient Boosting Classifier.
- **`run_pipeline.py`**: Orchestrates the execution of preprocessing and training both candidates to figure out the best model for "Survived".

These scripts map directly to the MLRL (Machine Learning Reasoning Layer) steps shown in the final report on the frontend.

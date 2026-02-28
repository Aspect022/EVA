import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import os

def preprocess_data(data_path, output_dir):
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    # Define target and features
    target = 'Survived'
    drop_cols = ['PassengerId', 'Name', 'Ticket', 'Cabin']
    
    X = df.drop(columns=[target] + drop_cols)
    y = df[target]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Identify column types
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X.select_dtypes(include=['object', 'category']).columns
    
    print("Building preprocessing pipeline...")
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    # Fit and transform
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    
    # Save artifacts
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    joblib.dump(preprocessor, os.path.join(output_dir, 'preprocessor.pkl'))
    
    # Return processed data for training
    return X_train_processed, X_test_processed, y_train, y_test

if __name__ == "__main__":
    preprocess_data('../Backend/eva_sessions/Titanic-Dataset.csv', 'models')

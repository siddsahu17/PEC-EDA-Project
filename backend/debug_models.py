import pandas as pd
import numpy as np
from ml_models import PharmacyML
from app import load_data

def debug():
    print("Loading data...")
    data = load_data()
    
    print("Initializing ML System...")
    ml = PharmacyML(data)
    
    print("\n--- Regression Data Check ---")
    X, y = ml.prepare_regression_data()
    print(f"Data Shape: {X.shape}")
    print("Feature Correlations with Target:")
    df_check = X.copy()
    df_check['target'] = y
    print(df_check.corr(numeric_only=True)['target'])
    
    print("\n--- Model Training Status ---")
    for name, model in ml.models.items():
        print(f"Model: {name} - Trained")
        
    print("\n--- Metrics ---")
    print(ml.metrics)

if __name__ == "__main__":
    debug()

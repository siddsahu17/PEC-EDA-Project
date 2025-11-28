import pandas as pd
from ml_models import PharmacyML

# Mock data loading similar to app.py
DATA_DIR = "data"
def load_data():
    d = {}
    files = {
        "customers": "Customers.csv",
        "medicine": "Medicine.csv",
        "pharmacy": "PharmacyShops.csv",
        "prescriptions": "Prescriptions.csv",
        "purchases": "Purchases.csv",
        "sales_bills": "SalesBills.csv",
        "stocks": "Stocks.csv",
        "med_type": "TypesofMedicine.csv"
    }
    for k, fname in files.items():
        try:
            d[k] = pd.read_csv(f"{DATA_DIR}/{fname}")
        except Exception as e:
            d[k] = pd.DataFrame()
            print(f"Warning: couldn't load {fname}: {e}")
    return d

print("Loading data...")
data = load_data()
print("Data loaded. Keys:", data.keys())

if not data['sales_bills'].empty:
    print("\nSales Bills Head:")
    print(data['sales_bills'][['quantity', 'discount', 'final_price']].head())
    print("\nSales Bills Info:")
    print(data['sales_bills'][['quantity', 'discount', 'final_price']].info())

print("\nInitializing PharmacyML...")
ml = PharmacyML(data)

print("\nMetrics:")
print(ml.get_metrics())

print("\nTesting Linear Prediction:")
try:
    pred = ml.predict_linear(1, 0)
    print("Prediction:", pred)
except Exception as e:
    print("Prediction Error:", e)

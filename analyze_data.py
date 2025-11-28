import pandas as pd
import numpy as np

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
    return d

data = load_data()
sales = data['sales_bills']
meds = data['medicine']
cust = data['customers']

# 1. Linear Regression Analysis (Final Price)
print("--- Linear Regression Data ---")
# Merge sales with medicine to get unit price
sales_full = sales.merge(meds, on='medicine_id', how='left')
print("Correlation with final_price:")
print(sales_full[['quantity', 'discount', 'price', 'final_price']].corr()['final_price'])

# 2. Logistic Regression Analysis (Status)
print("\n--- Logistic Regression Data ---")
print("Status Value Counts:")
print(sales['status'].value_counts())
# Check correlation with numeric features
sales['status_binary'] = sales['status'].apply(lambda x: 1 if x == 'Completed' else 0)
print("Correlation with Status (Binary):")
print(sales[['final_price', 'quantity', 'discount', 'status_binary']].corr()['status_binary'])

# 3. Decision Tree Analysis (Quantity)
print("\n--- Decision Tree Data ---")
print("Correlation with Quantity:")
print(sales_full[['price', 'final_price', 'quantity']].corr()['quantity'])

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import json
from ml_models import PharmacyML

app = FastAPI(title="Pharmacy EDA Dashboard (FastAPI)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "data"

# Attempt to load datasets
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

DATA = load_data()
ML_SYSTEM = PharmacyML(DATA)

# Helper - safe parse date column
def ensure_date(df, col):
    if col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        except Exception:
            pass
    return df

# Helper to return Plotly JSON with Inference
def response_with_inference(fig, inference_text):
    return {
        "graph": json.loads(fig.to_json()),
        "inference": inference_text
    }

# Pydantic Models for ML Inputs
class LinearInput(BaseModel):
    quantity: float
    discount: float
    price: float = 100.0  # Default price if not provided

class LogisticInput(BaseModel):
    final_price: float
    payment_mode: str

class TreeInput(BaseModel):
    price: float
    type_id: str

@app.get("/")
def index():
    return {"message": "Pharmacy EDA API is running. Access endpoints for data."}

@app.get("/heads")
def heads():
    out = {}
    for name, df in DATA.items():
        if df.empty:
            out[name] = "Empty"
        else:
            out[name] = df.head().to_dict(orient="records")
    return out

# --- ML Endpoints ---

@app.get("/api/ml/regression/compare")
def compare_regression_models():
    return ML_SYSTEM.get_regression_metrics()

@app.get("/api/ml/regression/plot/{model_name}")
def get_regression_plot(model_name: str):
    plot = ML_SYSTEM.get_regression_plot(model_name)
    if plot is None:
        return {"error": "Plot not available"}
    return plot

@app.get("/api/ml/classification/metrics")
def get_classification_metrics():
    return ML_SYSTEM.get_classification_metrics()

@app.get("/api/ml/confusion_matrix/{model_name}")
def get_model_confusion_matrix(model_name: str):
    # Support both regression (binned) and classification CMs
    cm = ML_SYSTEM.get_confusion_matrix(model_name)
    if cm is None:
        # Try fetching from classification dict if not found (backward compatibility)
        if model_name == "Status Classifier":
             cm = ML_SYSTEM.get_confusion_matrix("Status Classifier")
    
    if cm is None:
        return {"error": f"Confusion matrix not available for {model_name}"}
    return cm

# Prediction Endpoints (Simplified for now, focusing on comparison)
# We can add specific prediction endpoints if needed, but the user asked for comparison.


# --- Visualization Endpoints ---

# 1. Sales over time (Line)
@app.get("/sales_over_time")
def sales_over_time():
    sales = DATA.get("sales_bills", pd.DataFrame()).copy()
    if "sale_date" not in sales.columns or sales.empty:
        return {"error": "Data missing"}
    sales = ensure_date(sales, "sale_date")
    sales_over_time = sales.groupby("sale_date", dropna=True)["final_price"].sum().reset_index()
    fig = px.line(sales_over_time, x="sale_date", y="final_price", title="Total Sales Over Time")
    
    total_sales = sales_over_time["final_price"].sum()
    peak_day = sales_over_time.loc[sales_over_time["final_price"].idxmax()]["sale_date"].strftime('%Y-%m-%d')
    inference = f"Total sales recorded are {total_sales:,.2f}. The highest sales occurred on {peak_day}, indicating a potential peak in demand or a specific event."
    
    return response_with_inference(fig, inference)

# 2. Payment mode vs status (Bar)
@app.get("/payment_mode_status")
def payment_mode_status():
    sales = DATA.get("sales_bills", pd.DataFrame())
    if sales.empty or "payment_mode" not in sales.columns:
        return {"error": "Data missing"}
    counts = sales.groupby(["payment_mode", "status"]).size().reset_index(name="count")
    fig = px.bar(counts, x="payment_mode", y="count", color="status", title="Payment Modes vs Status", barmode="group")
    
    top_mode = counts.groupby("payment_mode")["count"].sum().idxmax()
    inference = f"The most popular payment mode is {top_mode}. Analyzing the status distribution helps identify if certain payment methods have higher cancellation rates."
    
    return response_with_inference(fig, inference)

# 3. Customer age distribution (Histogram)
@app.get("/customer_age_dist")
def customer_age_dist():
    cust = DATA.get("customers", pd.DataFrame())
    if cust.empty or "age" not in cust.columns:
        return {"error": "Data missing"}
    fig = px.histogram(cust, x="age", nbins=20, title="Customer Age Distribution", color_discrete_sequence=["skyblue"])
    
    avg_age = cust["age"].mean()
    inference = f"The average customer age is {avg_age:.1f} years. The distribution highlights the primary demographic group, aiding in targeted marketing."
    
    return response_with_inference(fig, inference)

# 4. Purchase cost distribution (Histogram)
@app.get("/purchase_cost_dist")
def purchase_cost_dist():
    purchases = DATA.get("purchases", pd.DataFrame())
    if purchases.empty or "cost_price" not in purchases.columns:
        return {"error": "Data missing"}
    fig = px.histogram(purchases, x="cost_price", nbins=20, title="Distribution of Purchase Cost", color_discrete_sequence=["purple"])
    
    inference = "This histogram shows the spread of purchase costs. Skewness towards lower values suggests frequent small-scale purchases."
    return response_with_inference(fig, inference)

# 5. Quantity Purchased per Supplier (Bar)
@app.get("/supplier_qty")
def supplier_qty():
    purchases = DATA.get("purchases", pd.DataFrame())
    if purchases.empty or "supplier_name" not in purchases.columns:
        return {"error": "Data missing"}
    sup_qty = purchases.groupby("supplier_name", dropna=True)["quantity"].sum().reset_index()
    sup_qty = sup_qty.sort_values("quantity", ascending=False)
    fig = px.bar(sup_qty, x="supplier_name", y="quantity", title="Quantity Purchased per Supplier")
    
    top_sup = sup_qty.iloc[0]["supplier_name"]
    inference = f"{top_sup} is the leading supplier by quantity. Reliance on a single supplier for bulk stock might pose a supply chain risk."
    return response_with_inference(fig, inference)

# 6. Available Stock Units per Shop (Box)
@app.get("/stock_box")
def stock_box():
    stocks = DATA.get("stocks", pd.DataFrame())
    if stocks.empty or "shop_id" not in stocks.columns:
        return {"error": "Data missing"}
    fig = px.box(stocks, x="shop_id", y="available_units", title="Available Stock Units per Shop")
    
    inference = "The box plot reveals variability in stock levels across shops. Outliers indicate shops with significantly higher or lower inventory than average."
    return response_with_inference(fig, inference)

# 7. Sales correlation heatmap (Heatmap)
@app.get("/sales_corr_heatmap")
def sales_corr_heatmap():
    sales = DATA.get("sales_bills", pd.DataFrame())
    cols = ["quantity", "discount", "final_price"]
    if sales.empty or not all(c in sales.columns for c in cols):
        return {"error": "Data missing"}
    corr = sales[cols].corr()
    fig = px.imshow(corr, text_auto=True, title="Correlation between Sales Variables", color_continuous_scale="RdBu_r")
    
    inference = "The heatmap displays relationships between sales variables. A strong correlation between Quantity and Final Price is expected."
    return response_with_inference(fig, inference)

# 8. Top doctors by prescriptions (Bar)
@app.get("/top_doctors")
def top_doctors():
    pres = DATA.get("prescriptions", pd.DataFrame())
    if pres.empty or "doctor_name" not in pres.columns:
        return {"error": "Data missing"}
    doc_count = pres["doctor_name"].value_counts().head(10).reset_index()
    doc_count.columns = ["doctor_name", "count"]
    fig = px.bar(doc_count, x="doctor_name", y="count", title="Top 10 Doctors by Prescriptions")
    
    top_doc = doc_count.iloc[0]["doctor_name"]
    inference = f"{top_doc} prescribes the most medications. Building a relationship with top prescribers could be beneficial."
    return response_with_inference(fig, inference)

# 9. Prescription trends by year (Line)
@app.get("/prescription_trend")
def prescription_trend():
    pres = DATA.get("prescriptions", pd.DataFrame()).copy()
    if pres.empty or "date" not in pres.columns:
        return {"error": "Data missing"}
    pres = ensure_date(pres, "date")
    presc_trend = pres.groupby(pres["date"].dt.year)["prescription_id"].count().reset_index()
    presc_trend.columns = ["year", "count"]
    fig = px.line(presc_trend, x="year", y="count", markers=True, title="Prescriptions Over the Years")
    
    inference = "The trend line shows the volume of prescriptions over time. An upward trend indicates business growth or increased market reach."
    return response_with_inference(fig, inference)

# 10. Discount vs Final Price (Scatter)
@app.get("/discount_vs_price")
def discount_vs_price():
    sales = DATA.get("sales_bills", pd.DataFrame())
    if sales.empty:
        return {"error": "Data missing"}
    fig = px.scatter(sales, x="discount", y="final_price", 
                     color="payment_mode" if "payment_mode" in sales.columns else None,
                     size="quantity" if "quantity" in sales.columns else None,
                     hover_data=["status"] if "status" in sales.columns else None,
                     title="Discount vs Final Price by Payment Mode")
    
    inference = "This scatter plot explores if higher discounts correlate with higher final prices (bulk buys). Color coding reveals payment preferences."
    return response_with_inference(fig, inference)

# 11. Top 10 medicines by revenue (Bar)
@app.get("/top_meds")
def top_meds():
    sales = DATA.get("sales_bills", pd.DataFrame())
    meds = DATA.get("medicine", pd.DataFrame())
    if sales.empty or meds.empty:
        return {"error": "Data missing"}
    top = sales.groupby("medicine_id", dropna=True)["final_price"].sum().nlargest(10).reset_index()
    top = top.merge(meds[["medicine_id", "medicine_name"]], on="medicine_id", how="left")
    fig = px.bar(top, x="medicine_name", y="final_price", title="Top 10 Medicines by Revenue", color="final_price")
    
    top_med = top.iloc[0]["medicine_name"]
    inference = f"{top_med} generates the highest revenue. Ensuring consistent stock of this item is critical for profitability."
    return response_with_inference(fig, inference)

# 12. Shop ratings by location (Box)
@app.get("/shop_ratings_box")
def shop_ratings_box():
    shops = DATA.get("pharmacy", pd.DataFrame())
    if shops.empty:
        return {"error": "Data missing"}
    fig = px.box(shops, x="location", y="rating", color="location", title="Shop Ratings by Location")
    
    inference = "Ratings vary by location. Locations with lower median ratings may require operational improvements or staff training."
    return response_with_inference(fig, inference)

# 13. Shop ratings histogram (Histogram)
@app.get("/shop_ratings_hist")
def shop_ratings_hist():
    shops = DATA.get("pharmacy", pd.DataFrame())
    if shops.empty:
        return {"error": "Data missing"}
    fig = px.histogram(shops, x="rating", nbins=10, title="Shop Ratings Distribution", color_discrete_sequence=["orange"])
    
    inference = "The distribution of ratings gives an overview of customer satisfaction. A left-skewed distribution would indicate mostly positive feedback."
    return response_with_inference(fig, inference)

@app.get("/api/data/{dataset}")
def get_dataset(dataset: str):
    if dataset not in DATA:
        return {"error": "Dataset not found"}
    df = DATA[dataset]
    return df.to_dict(orient="records")

@app.get("/api/summary")
def get_summary():
    summary = {}
    for name, df in DATA.items():
        summary[name] = {
            "shape": df.shape,
            "columns": list(df.columns),
            "empty": df.empty
        }
    return summary

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

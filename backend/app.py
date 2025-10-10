# app.py
from fastapi import FastAPI, Response, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.io as pio

sns.set(style="whitegrid", palette="Set2")
plt.rcParams["figure.figsize"] = (10,5)

app = FastAPI(title="Pharmacy EDA Dashboard (FastAPI)")

# CORS (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "data"

# Attempt to load datasets - adjust filenames if different
def load_data():
    d = {}
    # filenames expected from your examples
    files = {
        "customers": "Customers.csv",
        "medicine": "Medicine.csv",
        "pharmacy": "Shops.csv",
        "prescriptions": "Prescriptions.csv",
        "purchases": "Purchases.csv",
        "sales_bills": "SalesBills.csv",
        "stocks": "Stocks.csv",
        "med_type": "TypesOfMedicine.csv"
    }
    for k, fname in files.items():
        try:
            d[k] = pd.read_csv(f"{DATA_DIR}/{fname}")
        except Exception as e:
            # give an empty DataFrame if file missing
            d[k] = pd.DataFrame()
            print(f"Warning: couldn't load {fname}: {e}")
    return d

DATA = load_data()

# Helper - safe parse date column if exists
def ensure_date(df, col):
    if col in df.columns:
        try:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        except Exception:
            pass
    return df

# Render matplotlib/seaborn figure to PNG streaming response
def fig_to_png_response(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

# Index page with links
@app.get("/", response_class=HTMLResponse)
def index():
    links = [
        ("/heads", "DataFrame Heads"),
        ("/sales_over_time", "Total Sales Over Time (line)"),
        ("/payment_mode_status", "Payment Modes vs Status (countplot)"),
        ("/customer_age_dist", "Customer Age Distribution (hist)"),
        ("/purchase_cost_dist", "Purchase Cost Distribution (hist)"),
        ("/supplier_qty", "Quantity Purchased per Supplier (bar)"),
        ("/stock_box", "Available Stock Units per Shop (box)"),
        ("/sales_corr_heatmap", "Sales Correlation Heatmap"),
        ("/top_doctors", "Top 10 Doctors by Prescriptions (bar)"),
        ("/prescription_trend", "Prescriptions Over Years (line)"),
        ("/discount_vs_price", "Discount vs Final Price (scatter)"),
        ("/top_meds", "Top 10 Medicines by Revenue (bar)"),
        ("/shop_ratings_box", "Shop Ratings by Location (box)"),
        ("/shop_ratings_hist", "Shop Ratings Distribution (hist)")
    ]
    html = "<h2>Pharmacy EDA Dashboard (FastAPI)</h2><ul>"
    for href, label in links:
        html += f'<li><a href="{href}" target="_blank">{label}</a></li>'
    html += "</ul><p>Note: interactive Plotly charts open in a separate tab.</p>"
    return HTMLResponse(html)

# Heads route: show first rows and info as HTML
@app.get("/heads", response_class=HTMLResponse)
def heads():
    out = "<h2>Dataframe Heads</h2>"
    for name, df in DATA.items():
        out += f"<h3>{name} (shape: {df.shape})</h3>"
        if df.empty:
            out += "<p><b>Not loaded / empty dataframe</b></p>"
            continue
        out += df.head().to_html(index=False, classes="table table-striped")
    return HTMLResponse(out)

# 1. Sales over time (Plotly -> interactive)
@app.get("/sales_over_time", response_class=HTMLResponse)
def sales_over_time():
    sales = DATA.get("sales_bills", pd.DataFrame()).copy()
    if "sale_date" not in sales.columns or sales.empty:
        return HTMLResponse("<p>sales_bills missing or no sale_date column</p>")
    sales = ensure_date(sales, "sale_date")
    sales_over_time = sales.groupby("sale_date", dropna=True)["final_price"].sum().reset_index()
    fig = px.line(sales_over_time, x="sale_date", y="final_price", title="Total Sales Over Time")
    html = pio.to_html(fig, full_html=True, include_plotlyjs="cdn")
    return HTMLResponse(html)

# 2. Payment mode vs status (matplotlib/seaborn -> PNG)
@app.get("/payment_mode_status")
def payment_mode_status():
    sales = DATA.get("sales_bills", pd.DataFrame())
    if sales.empty or ("payment_mode" not in sales.columns):
        return HTMLResponse("<p>sales_bills missing or payment_mode column not found</p>")
    fig, ax = plt.subplots(figsize=(8,5))
    try:
        sns.countplot(data=sales, x="payment_mode", hue="status", palette="Set2", ax=ax)
        ax.set_title("Payment Modes vs Status")
    except Exception as e:
        plt.close(fig)
        return HTMLResponse(f"<p>Error plotting: {e}</p>")
    return fig_to_png_response(fig)

# 3. Customer age distribution (matplotlib -> PNG)
@app.get("/customer_age_dist")
def customer_age_dist():
    cust = DATA.get("customers", pd.DataFrame())
    if cust.empty or "age" not in cust.columns:
        return HTMLResponse("<p>customers missing or age column not found</p>")
    fig, ax = plt.subplots(figsize=(8,4))
    sns.histplot(cust["age"].dropna(), bins=20, kde=True, color="skyblue", ax=ax)
    ax.set_title("Customer Age Distribution")
    return fig_to_png_response(fig)

# 4. Purchase cost distribution (matplotlib -> PNG)
@app.get("/purchase_cost_dist")
def purchase_cost_dist():
    purchases = DATA.get("purchases", pd.DataFrame())
    if purchases.empty or "cost_price" not in purchases.columns:
        return HTMLResponse("<p>purchases missing or cost_price column not found</p>")
    fig, ax = plt.subplots(figsize=(8,4))
    sns.histplot(purchases["cost_price"].dropna(), bins=20, kde=True, color="purple", ax=ax)
    ax.set_title("Distribution of Purchase Cost")
    return fig_to_png_response(fig)

# 5. Quantity Purchased per Supplier (Plotly)
@app.get("/supplier_qty", response_class=HTMLResponse)
def supplier_qty():
    purchases = DATA.get("purchases", pd.DataFrame())
    if purchases.empty or "supplier_name" not in purchases.columns:
        return HTMLResponse("<p>purchases missing or supplier_name column not found</p>")
    sup_qty = purchases.groupby("supplier_name", dropna=True)["quantity"].sum().reset_index()
    sup_qty = sup_qty.sort_values("quantity", ascending=False)
    fig = px.bar(sup_qty, x="supplier_name", y="quantity", title="Quantity Purchased per Supplier")
    return HTMLResponse(pio.to_html(fig, full_html=True, include_plotlyjs="cdn"))

# 6. Available Stock Units per Shop (Plotly box)
@app.get("/stock_box", response_class=HTMLResponse)
def stock_box():
    stocks = DATA.get("stocks", pd.DataFrame())
    if stocks.empty or ("shop_id" not in stocks.columns or "available_units" not in stocks.columns):
        return HTMLResponse("<p>stocks missing or required columns not found</p>")
    fig = px.box(stocks, x="shop_id", y="available_units", title="Available Stock Units per Shop")
    return HTMLResponse(pio.to_html(fig, full_html=True, include_plotlyjs="cdn"))

# 7. Sales correlation heatmap (matplotlib -> PNG)
@app.get("/sales_corr_heatmap")
def sales_corr_heatmap():
    sales = DATA.get("sales_bills", pd.DataFrame())
    cols = ["quantity", "discount", "final_price"]
    if sales.empty or not all(c in sales.columns for c in cols):
        return HTMLResponse("<p>sales_bills missing or required columns not found</p>")
    corr = sales[cols].corr()
    fig, ax = plt.subplots(figsize=(6,5))
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
    ax.set_title("Correlation between Sales Variables")
    return fig_to_png_response(fig)

# 8. Top doctors by prescriptions (Plotly bar)
@app.get("/top_doctors", response_class=HTMLResponse)
def top_doctors():
    pres = DATA.get("prescriptions", pd.DataFrame())
    if pres.empty or "doctor_name" not in pres.columns:
        return HTMLResponse("<p>prescriptions missing or doctor_name not found</p>")
    doc_count = pres["doctor_name"].value_counts().head(10).reset_index()
    doc_count.columns = ["doctor_name", "count"]
    fig = px.bar(doc_count, x="doctor_name", y="count", title="Top 10 Doctors by Prescriptions")
    return HTMLResponse(pio.to_html(fig, full_html=True, include_plotlyjs="cdn"))

# 9. Prescription trends by year (matplotlib -> PNG)
@app.get("/prescription_trend")
def prescription_trend():
    pres = DATA.get("prescriptions", pd.DataFrame()).copy()
    if pres.empty or "date" not in pres.columns:
        return HTMLResponse("<p>prescriptions missing or date column not found</p>")
    pres = ensure_date(pres, "date")
    presc_trend = pres.groupby(pres["date"].dt.year)["prescription_id"].count().reset_index()
    presc_trend.columns = ["year", "count"]
    fig, ax = plt.subplots(figsize=(8,4))
    sns.lineplot(data=presc_trend, x="year", y="count", marker="o", ax=ax)
    ax.set_title("Prescriptions Over the Years")
    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    return fig_to_png_response(fig)

# 10. Discount vs Final Price (Plotly scatter)
@app.get("/discount_vs_price", response_class=HTMLResponse)
def discount_vs_price():
    sales = DATA.get("sales_bills", pd.DataFrame())
    if sales.empty or not all(c in sales.columns for c in ["discount", "final_price"]):
        return HTMLResponse("<p>sales_bills missing or required columns not found</p>")
    fig = px.scatter(sales, x="discount", y="final_price", color="payment_mode" if "payment_mode" in sales.columns else None,
                     size="quantity" if "quantity" in sales.columns else None,
                     hover_data=["status"] if "status" in sales.columns else None,
                     title="Discount vs Final Price by Payment Mode")
    return HTMLResponse(pio.to_html(fig, full_html=True, include_plotlyjs="cdn"))

# 11. Top 10 medicines by revenue (Plotly bar)
@app.get("/top_meds", response_class=HTMLResponse)
def top_meds():
    sales = DATA.get("sales_bills", pd.DataFrame())
    meds = DATA.get("medicine", pd.DataFrame())
    if sales.empty or meds.empty or "medicine_id" not in sales.columns:
        return HTMLResponse("<p>sales_bills or medicine missing or medicine_id not found</p>")
    top = sales.groupby("medicine_id", dropna=True)["final_price"].sum().nlargest(10).reset_index()
    top = top.merge(meds[["medicine_id", "medicine_name"]], on="medicine_id", how="left")
    fig = px.bar(top, x="medicine_name", y="final_price", title="Top 10 Medicines by Revenue", color="final_price")
    return HTMLResponse(pio.to_html(fig, full_html=True, include_plotlyjs="cdn"))

# 12. Shop ratings by location (Plotly box)
@app.get("/shop_ratings_box", response_class=HTMLResponse)
def shop_ratings_box():
    shops = DATA.get("pharmacy", DATA.get("pharmacy", pd.DataFrame()))
    if shops.empty or not all(c in shops.columns for c in ["location", "rating"]):
        return HTMLResponse("<p>shops missing or required columns not found</p>")
    fig = px.box(shops, x="location", y="rating", color="location", title="Shop Ratings by Location")
    return HTMLResponse(pio.to_html(fig, full_html=True, include_plotlyjs="cdn"))

# 13. Shop ratings histogram (matplotlib -> PNG)
@app.get("/shop_ratings_hist")
def shop_ratings_hist():
    shops = DATA.get("pharmacy", pd.DataFrame())
    if shops.empty or "rating" not in shops.columns:
        return HTMLResponse("<p>shops missing or rating column not found</p>")
    fig, ax = plt.subplots(figsize=(8,4))
    sns.histplot(shops["rating"].dropna(), bins=10, kde=True, color="orange", ax=ax)
    ax.set_title("Shop Ratings Distribution")
    return fig_to_png_response(fig)

# fallback health
@app.get("/health")
def health():
    return {"status": "ok"}

# If you want to run with `python app.py` (for dev)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

# Pharmacy Data Analytics & Prediction System

## 📌 Project Overview
This project is a comprehensive **Exploratory Data Analysis (EDA) and Machine Learning (ML) platform** designed for a Pharmacy Retail chain. It integrates a robust backend for data processing and modeling with a modern, interactive frontend dashboard.

The system allows stakeholders to:
- **Visualize** key business metrics (Sales, Inventory, Customer Demographics).
- **Predict** medicine prices using advanced Machine Learning models.
- **Understand** the data journey through detailed EDA documentation.

## 🚀 Key Features

### 1. Interactive Dashboard
- **Real-time Visualizations**: Built with **Plotly.js**, offering interactive charts for Sales Trends, Top Medicines, and Customer Age Distribution.
- **Responsive Design**: A premium dark-themed UI optimized for clarity and aesthetics.

### 2. Machine Learning Module
- **Random Forest Regressor**: A tuned model to predict medicine prices based on features like `type`, `brand`, and `quantity`.
- **Performance Metrics**: Displays R2 Score, MAE, MSE, and RMSE.
- **Visual Validation**: Includes "Actual vs Predicted" scatter plots and Binned Confusion Matrices.

### 3. EDA Documentation Tab
- **Star Schema Visualization**: Schematic representation of Fact and Dimension tables.
- **Data Previews**: Interactive tabs to explore raw data (Customers, Sales, Medicine).
- **Step-by-Step Journey**: Detailed documentation of the EDA process, including:
    - Data Quality Checks (with code snippets).
    - Missing Value Handling (Median Imputation).
    - Feature Engineering.

## 🛠️ Tech Stack

### Frontend
- **Framework**: React (Vite)
- **Styling**: CSS Modules (Dark Theme)
- **Visualization**: Plotly.js, React-Plotly.js
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn
- **Server**: Uvicorn

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js & npm

### 1. Backend Setup
Navigate to the project root and set up the Python environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install fastapi uvicorn pandas numpy scikit-learn plotly
```

Start the Backend Server:
```bash
cd backend
uvicorn app:app --reload
```
*The backend will run at `http://127.0.0.1:8000`*

### 2. Frontend Setup
Open a new terminal and navigate to the frontend directory:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```
*The frontend will run at `http://localhost:5173`*

## 📂 Project Structure

```
├── backend/
│   ├── app.py              # FastAPI application & endpoints
│   ├── ml_models.py        # ML Model logic (Random Forest)
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx       # Main Analytics View
│   │   │   ├── MLDashboard.jsx     # ML Model View
│   │   │   ├── EDADashboard.jsx    # EDA Documentation View
│   │   │   └── ...
│   │   ├── App.jsx                 # Main Routing & Layout
│   │   └── index.css               # Global Styling
│   └── ...
├── data/                   # CSV Datasets
├── eda.ipynb               # Original Exploratory Data Analysis Notebook
└── README.md               # Project Documentation
```

## 📊 Data Pipeline
1.  **Raw Data**: CSV files (Customers, Medicine, SalesBills, etc.).
2.  **Processing**: Pandas is used for cleaning, merging, and feature engineering.
3.  **Modeling**: Scikit-learn pipelines handle preprocessing (OneHotEncoding) and training.
4.  **Serving**: FastAPI endpoints serve JSON data to the React frontend.

---
*Developed for EDA & PEC Project - Sem 5 TY-Btech*

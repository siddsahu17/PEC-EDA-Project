import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, confusion_matrix, accuracy_score
import plotly.express as px
import json

class PharmacyML:
    def __init__(self, data_dict):
        self.data = data_dict
        self.models = {}
        self.metrics = {}
        self.confusion_matrices = {}
        self.regression_plots = {}
        
        # Train models
        self.train_classification_model()
        self.train_regression_models()

    def prepare_regression_data(self):
        """
        Joins Sales, Medicine, and Customers to create a rich dataset for Price Prediction.
        Target: final_price
        Features: quantity, discount, price (unit), category, age, gender, payment_mode
        """
        sales = self.data.get("sales_bills", pd.DataFrame()).copy()
        meds = self.data.get("medicine", pd.DataFrame()).copy()
        cust = self.data.get("customers", pd.DataFrame()).copy()

        if sales.empty or meds.empty or cust.empty:
            return None

        # Merge Sales + Medicine
        df = sales.merge(meds, on="medicine_id", how="left")
        
        # Merge + Customers
        if "customer_id" in df.columns:
             df = df.merge(cust, on="customer_id", how="left")
        
        required_cols = ["final_price", "quantity", "discount", "price", "payment_mode"]
        if not all(col in df.columns for col in required_cols):
            return None

        # Drop NaNs
        df = df.dropna(subset=required_cols)
        
        # Feature Engineering: Interaction Term for Linear Models
        # final_price ~ quantity * price * (1 - discount/100)
        # Linear Regression needs 'quantity * price' as a feature to model this well.
        df["expected_amount"] = df["quantity"] * df["price"]
        
        # Define Features
        features = ["quantity", "discount", "price", "expected_amount", "payment_mode"]
        if "category" in df.columns: features.append("category")
        if "age" in df.columns: features.append("age")
        if "gender" in df.columns: features.append("gender")

        X = df[features]
        y = df["final_price"]
        
        return X, y

    def train_regression_models(self):
        data = self.prepare_regression_data()
        if data is None:
            print("Insufficient data for regression models.")
            return

        X, y = data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Preprocessing
        numeric_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
        categorical_features = X.select_dtypes(include=["object"]).columns.tolist()

        from sklearn.impute import SimpleImputer

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", Pipeline(steps=[
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler())
                ]), numeric_features),
                ("cat", Pipeline(steps=[
                    ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
                    ("encoder", OneHotEncoder(handle_unknown="ignore"))
                ]), categorical_features),
            ]
        )

        regressors = {
            "Random Forest": RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42)
        }

        for name, model in regressors.items():
            try:
                pipeline = Pipeline(steps=[("preprocessor", preprocessor), ("regressor", model)])
                pipeline.fit(X_train, y_train)
                
                y_pred = pipeline.predict(X_test)
                
                # Metrics
                r2 = r2_score(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)
                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                
                self.models[name] = pipeline
                self.metrics[name] = {
                    "R2 Score": round(r2, 4),
                    "MAE": round(mae, 2),
                    "MSE": round(mse, 2),
                    "RMSE": round(rmse, 2)
                }
                
                # Generate Binned Confusion Matrix for Regression
                try:
                    labels = ["Low", "Medium", "High"]
                    # robust binning using qcut on the training set target to define edges
                    # We use the entire y distribution to define "global" low/med/high for consistency
                    quantiles = y.quantile([0.33, 0.66]).values
                    bins = [-np.inf, quantiles[0], quantiles[1], np.inf]
                    
                    def bin_values(vals):
                        return np.digitize(vals, bins=bins) - 1
                    
                    y_test_binned = bin_values(y_test)
                    y_pred_binned = bin_values(y_pred)
                    
                    cm = confusion_matrix(y_test_binned, y_pred_binned)
                    self.confusion_matrices[name] = {"matrix": cm.tolist(), "labels": labels}
                except Exception as e:
                    print(f"Error generating regression CM for {name}: {e}")

                # Generate Plot Data (Actual vs Predicted)
                plot_df = pd.DataFrame({"Actual": y_test, "Predicted": y_pred}).sample(min(100, len(y_test)))
                # Check if statsmodels is installed for trendline
                try:
                    import statsmodels
                    trendline = "ols"
                except ImportError:
                    trendline = None
                
                fig = px.scatter(plot_df, x="Actual", y="Predicted", title=f"{name}: Actual vs Predicted", 
                                 trendline=trendline, labels={"Actual": "Actual Price", "Predicted": "Predicted Price"})
                self.regression_plots[name] = json.loads(fig.to_json())
                
            except Exception as e:
                print(f"Error training {name}: {e}")

    def train_classification_model(self):
        """
        Random Forest Classifier for Status Prediction.
        """
        try:
            df = self.data.get("sales_bills", pd.DataFrame()).copy()
            if df.empty: return

            df = df.dropna(subset=["status", "final_price", "quantity", "discount", "payment_mode"])
            X = df[["final_price", "quantity", "discount", "payment_mode"]]
            y = df["status"]

            numeric_features = ["final_price", "quantity", "discount"]
            categorical_features = ["payment_mode"]

            from sklearn.impute import SimpleImputer

            preprocessor = ColumnTransformer(
                transformers=[
                    ("num", Pipeline(steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler())
                    ]), numeric_features),
                    ("cat", Pipeline(steps=[
                        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore"))
                    ]), categorical_features),
                ]
            )

            clf = Pipeline(steps=[("preprocessor", preprocessor), ("classifier", RandomForestClassifier(n_estimators=50, random_state=42))])
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            clf.fit(X_train, y_train)
            
            y_pred = clf.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            cm = confusion_matrix(y_test, y_pred)
            labels = sorted(y.unique())

            self.models["Status Classifier"] = clf
            self.metrics["Status Classifier"] = {"Accuracy": round(acc, 4)}
            self.confusion_matrices["Status Classifier"] = {"matrix": cm.tolist(), "labels": labels}

        except Exception as e:
            print(f"Error training Classification Model: {e}")

    def get_regression_metrics(self):
        # Filter metrics for regression models
        reg_names = ["Linear Regression", "Decision Tree", "Random Forest", "Gradient Boosting"]
        return {k: v for k, v in self.metrics.items() if k in reg_names}

    def get_regression_plot(self, model_name):
        return self.regression_plots.get(model_name, None)

    def get_classification_metrics(self):
        return self.metrics.get("Status Classifier", {})

    def get_confusion_matrix(self, model_name="Status Classifier"):
        return self.confusion_matrices.get(model_name, None)

    # Prediction methods (simplified for demo)
    def predict_price(self, model_name, input_data):
        if model_name not in self.models: return None
        # Input data must be a dict matching feature names
        df = pd.DataFrame([input_data])
        return self.models[model_name].predict(df)[0]

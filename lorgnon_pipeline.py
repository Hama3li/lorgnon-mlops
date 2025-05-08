import pandas as pd
import numpy as np
import pickle
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor
from sklearn.ensemble import ExtraTreesRegressor

def load_data(csv_path):
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=["Throughput"])
    df = df.reset_index(drop=True)
    return df

def engineer_features(df):
    for lag in range(1, 5):
        df[f"throughput_lag_{lag}"] = df["Throughput"].shift(lag)
    df["throughput_delta"] = df["Throughput"].diff()

    df["pixel_x"] = ((df["longitude"] + 180) * 100).astype(int)
    df["pixel_y"] = ((df["latitude"] + 90) * 100).astype(int)

    df["mobility_mode"] = df["mobility_mode"].map({"walking": 0, "vehicle": 1, "stationary": 2}).fillna(0)
    df["handoff"] = df["tower_id"].diff().ne(0).astype(int)

    df = df.dropna().reset_index(drop=True)
    return df

def train_model(df, model_type="xgboost"):
    features_L = ["lte_rsrp", "lte_rsrq", "nr_ssRsrp", "nr_ssRsrq", "nr_ssSinr"]
    features_M = ["mobility_mode", "movingSpeed", "compassDirection", "handoff"]
    features_C = ["pixel_x", "pixel_y"]
    features_lag = [f"throughput_lag_{i}" for i in range(1, 5)] + ["throughput_delta"]

    features = features_L + features_M + features_C + features_lag

    X = df[features]
    y = df["Throughput"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    if model_type == "xgboost":
        model = XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
    elif model_type == "extratrees":
        model = ExtraTreesRegressor(n_estimators=100, max_depth=10, random_state=42)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

    model.fit(X_train_scaled, y_train)

    y_pred = model.predict(X_test_scaled)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)

    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)

    with open("scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)

    return model, scaler, features, rmse, mae

def log_to_mlflow(model, scaler, features, rmse, mae, model_type):
    with mlflow.start_run():
        mlflow.log_param("model_type", model_type)
        mlflow.log_param("features", features)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.sklearn.log_model(model, "model")

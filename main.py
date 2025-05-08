# main.py

from lorgnon_pipeline import load_data, engineer_features, train_model, log_to_mlflow
import argparse

def main(csv_path, model_type="xgboost"):
    print("\n📥 Loading data...")
    df = load_data(csv_path)

    print("\n⚙️ Engineering features...")
    df = engineer_features(df)

    print(f"\n🧠 Training model ({model_type})...")
    model, scaler, features, rmse, mae = train_model(df, model_type=model_type)

    print("\n📊 Logging to MLflow...")
    log_to_mlflow(model, scaler, features, rmse, mae, model_type)

    print(f"\n✅ Done! RMSE = {rmse:.2f}, MAE = {mae:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run MLOps Pipeline")
    parser.add_argument("--data", required=True, help="Path to CSV dataset")
    parser.add_argument("--model_type", default="xgboost", choices=["xgboost", "extratrees"], help="Model to use")
    args = parser.parse_args()

    main(args.data, args.model_type)

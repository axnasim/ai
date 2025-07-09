# Train model and log to MLflow
import pandas as pd
import joblib
import mlflow
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

df = pd.read_csv("data/processed.csv")

X = df.drop(columns=["trip_duration"])
y = df["trip_duration"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

with mlflow.start_run():
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    
    rmse = mean_squared_error(y_test, preds, squared=False)
    print(f"✅ RMSE: {rmse:.2f}")

    # Log metrics and model
    mlflow.log_metric("rmse", rmse)
    mlflow.sklearn.log_model(model, artifact_path="model")

    joblib.dump(model, "models/taxi_duration_model.pkl")

from fastapi import FastAPI
import joblib
import pandas as pd

model = joblib.load("models/taxi_duration_model.pkl")
app = FastAPI()

@app.post("/predict")
def predict(data: dict):
    df = pd.DataFrame([data])
    prediction = model.predict(df)[0]
    return {"trip_duration_minutes": prediction}

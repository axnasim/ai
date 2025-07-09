# Preprocess raw data
import pandas as pd

df = pd.read_parquet("data/yellow_tripdata_2023-01.parquet")

# Filter relevant columns
df = df[[
    "tpep_pickup_datetime", 
    "tpep_dropoff_datetime", 
    "passenger_count", 
    "trip_distance", 
    "PULocationID", 
    "DOLocationID", 
    "fare_amount"
]]

# Drop missing or invalid data
df.dropna(inplace=True)
df = df[df["fare_amount"] > 0]

# Feature engineering
df["trip_duration"] = (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60
df = df[df["trip_duration"] <= 180]  # remove outliers

df["hour"] = df["tpep_pickup_datetime"].dt.hour
df["day_of_week"] = df["tpep_pickup_datetime"].dt.dayofweek

# Define features and target
features = ["passenger_count", "trip_distance", "PULocationID", "DOLocationID", "hour", "day_of_week"]
target = "trip_duration"

df[features + [target]].to_csv("data/processed.csv", index=False)
print("✅ Data processed and saved.")

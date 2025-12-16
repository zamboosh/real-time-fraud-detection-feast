# feature_repo/feature_store.py
from datetime import timedelta
from feast import Entity, FeatureService, FeatureView, Field, FileSource
from feast.types import Float32, Int64

# --- 1. Define the Entity ---
# The primary key for retrieving features (what we are predicting on)
user = Entity(name="user_id", description="ID of the user making a transaction")

# --- 2. Define the Data Source (Mock Offline Data) ---
# In a real system, this would point to a data warehouse (Snowflake, BigQuery, etc.)
# For the POC, we'll use a local parquet file.
user_transactions_source = FileSource(
    path="data/user_transactions.parquet",  # Must be a parquet file
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
)

# --- 3. Define the Feature View (The Feature Logic) ---
# A collection of features related to the user entity
user_transaction_fv = FeatureView(
    name="user_transaction_features",
    entities=[user],
    ttl=timedelta(weeks=52),  # Time-to-live for data freshness
    schema=[
        Field(name="transaction_count_7d", dtype=Int64),
        Field(name="avg_transaction_amount_7d", dtype=Float32),
    ],
    online=True,  # Critical: Makes features available for real-time serving
    source=user_transactions_source,
    tags={},
)

# --- 4. Define a Feature Service ---
# Groups the features needed for a specific model (our fraud model)
fraud_feature_service = FeatureService(
    name="fraud_prediction_service",
    features=[user_transaction_fv],
)

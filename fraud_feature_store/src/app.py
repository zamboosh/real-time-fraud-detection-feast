# src/app.py
from fastapi import FastAPI
from pydantic import BaseModel
from feast import FeatureStore
import os


# --- 1. Define Schemas ---
class UserIn(BaseModel):
    user_id: int
    transaction_amount: float  # Mock field for immediate checks if needed


class PredictionOut(BaseModel):
    is_fraud: bool
    confidence: float
    features_fetched: dict


# --- 2. Initialize FastAPI and Feature Store ---
# MLOps Best Practice: Load the Feature Store object globally on startup
# The repo_path points to where feast init was run (the project root)
# Ensure the application is run from the project root directory
FEAST_REPO_PATH = "feature_repo"
if not os.path.isdir(FEAST_REPO_PATH):
    raise FileNotFoundError(
        f"Feast repo not found at: {FEAST_REPO_PATH}. Run from project root."
    )

try:
    fs = FeatureStore(repo_path=FEAST_REPO_PATH)
    print("Feast Feature Store initialized successfully!")
except Exception as e:
    print(f"FATAL ERROR: Could not initialize Feast: {e}")
    fs = None

app = FastAPI(title="Real-Time Fraud Prediction")


# --- 3. Prediction Endpoint ---
@app.post("/predict", response_model=PredictionOut)
async def predict(user_data: UserIn):
    if not fs:
        raise HTTPException(status_code=503, detail="Feature Store is unavailable.")

    # 1. Define the entity key for the current request
    entity_rows = [
        {"user_id": user_data.user_id}
        # Note: You don't need the timestamp here, Feast assumes "now" for online retrieval
    ]

    # 2. Retrieve the latest online features
    try:
        online_features = fs.get_online_features(
            features=[
                "user_transaction_features:transaction_count_7d",
                "user_transaction_features:avg_transaction_amount_7d",
            ],
            entity_rows=entity_rows,
        ).to_dict()
    except Exception as e:
        # Crucial Error Handling: If Redis (online store) is down, you must handle it!
        raise HTTPException(
            status_code=500, detail=f"Online Feature Store retrieval failed: {e}"
        )

    # 3. MOCK MODEL SCORING
    # In a real project, you would load your trained model here and score it.
    # For now, we'll just check if the average transaction amount is high.
    avg_amount = online_features["avg_transaction_amount_7d"][0]

    is_fraud = avg_amount > 1000  # Simple mock fraud logic

    # 4. Return results
    return PredictionOut(
        is_fraud=is_fraud,
        confidence=0.9 if is_fraud else 0.5,
        features_fetched=online_features,
    )


@app.get("/health")
def health_check():
    """Liveness probe. Checks if the Feature Store connection is active."""
    return {"status": "ok", "feast_ready": fs is not None}

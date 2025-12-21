# scripts/generate_data.py
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

NUM_USERS = 5000
NUM_TRANSACTIONS = 250000
OUTPUT_FILE = "fraud_feature_store/feature_repo/data/user_transactions.parquet"


def generate_transaction_data():
    """Generates mock time-series data for the Feast Feature View."""

    # 1. Generate core columns
    df = pd.DataFrame()
    df["user_id"] = np.random.randint(1001, 1001 + NUM_USERS, NUM_TRANSACTIONS)

    # Generate timestamps over the last 30 days
    now = datetime.now()
    df["event_timestamp"] = [
        now - timedelta(days=np.random.rand() * 30) for _ in range(NUM_TRANSACTIONS)
    ]

    # 2. Generate required features (simulating 7-day aggregation)
    # The MLOps complexity here is that we are writing the result of an aggregation
    # to the offline store, but Feast treats this as the source data.

    # transaction_count_7d: higher counts for lower IDs (mock bias)
    df["transaction_count_7d"] = (
        np.random.randint(5, 50, NUM_TRANSACTIONS) - (df["user_id"] - 1001) // 10
    )

    # avg_transaction_amount_7d: high amounts for low IDs (mock fraud)
    df["avg_transaction_amount_7d"] = np.random.uniform(
        50.0, 500.0, NUM_TRANSACTIONS
    ) * (1 + (df["user_id"] - 1001) / 50)

    # 3. Add a placeholder 'created' column (Feast requires it in some configurations)
    df["created_timestamp"] = now

    # 4. Save to Parquet
    # Ensure the feature_repo/data directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df.to_parquet(OUTPUT_FILE, index=False)

    print(
        f"Successfully generated {NUM_TRANSACTIONS} rows of mock data to {OUTPUT_FILE}"
    )
    print("\nSample Data Head:")
    print(df.head())


if __name__ == "__main__":
    # Ensure all required libraries are installed before running (pandas, numpy, pyarrow)
    generate_transaction_data()

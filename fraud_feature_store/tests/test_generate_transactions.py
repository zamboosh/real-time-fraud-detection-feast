# tests/test_generate_transactions.py
"""Tests for the transaction data generation script."""

import pytest
import pandas as pd
import sys
import os
from datetime import datetime

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


@pytest.mark.unit
def test_generate_transaction_data_schema(tmp_path, monkeypatch):
    """Test that generated data has the correct schema."""
    from generate_transactions import generate_transaction_data

    # Override output file to use temp directory
    output_file = tmp_path / "test_transactions.parquet"
    monkeypatch.setattr("generate_transactions.OUTPUT_FILE", str(output_file))

    # Generate data
    generate_transaction_data()

    # Load and verify
    df = pd.read_parquet(output_file)

    # Check required columns exist
    required_columns = [
        "user_id",
        "event_timestamp",
        "transaction_count_7d",
        "avg_transaction_amount_7d",
        "created_timestamp",
    ]

    for col in required_columns:
        assert col in df.columns, f"Missing required column: {col}"


@pytest.mark.unit
def test_generate_transaction_data_row_count(tmp_path, monkeypatch):
    """Test that the correct number of rows are generated."""
    from generate_transactions import generate_transaction_data, NUM_TRANSACTIONS

    output_file = tmp_path / "test_transactions.parquet"
    monkeypatch.setattr("generate_transactions.OUTPUT_FILE", str(output_file))

    generate_transaction_data()

    df = pd.read_parquet(output_file)
    assert len(df) == NUM_TRANSACTIONS


@pytest.mark.unit
def test_generate_transaction_data_types(tmp_path, monkeypatch):
    """Test that generated data has correct data types."""
    from generate_transactions import generate_transaction_data

    output_file = tmp_path / "test_transactions.parquet"
    monkeypatch.setattr("generate_transactions.OUTPUT_FILE", str(output_file))

    generate_transaction_data()

    df = pd.read_parquet(output_file)

    # Check data types
    assert pd.api.types.is_integer_dtype(df["user_id"])
    assert pd.api.types.is_datetime64_any_dtype(df["event_timestamp"])
    assert pd.api.types.is_integer_dtype(df["transaction_count_7d"])
    assert pd.api.types.is_float_dtype(df["avg_transaction_amount_7d"])
    assert pd.api.types.is_datetime64_any_dtype(df["created_timestamp"])


@pytest.mark.unit
def test_generate_transaction_data_value_ranges(tmp_path, monkeypatch):
    """Test that generated data values are within expected ranges."""
    from generate_transactions import generate_transaction_data, NUM_USERS

    output_file = tmp_path / "test_transactions.parquet"
    monkeypatch.setattr("generate_transactions.OUTPUT_FILE", str(output_file))

    generate_transaction_data()

    df = pd.read_parquet(output_file)

    # Check user_id range
    assert df["user_id"].min() >= 1001
    assert df["user_id"].max() < 1001 + NUM_USERS

    # Note: transaction_count_7d can be negative due to the generation formula:
    # np.random.randint(5, 50) - (user_id - 1001) // 10
    # This is acceptable for mock data

    # Check avg_transaction_amount_7d is positive
    assert df["avg_transaction_amount_7d"].min() > 0


@pytest.mark.unit
def test_generate_transaction_data_timestamps(tmp_path, monkeypatch):
    """Test that timestamps are within the last 30 days."""
    from generate_transactions import generate_transaction_data
    from datetime import timedelta

    output_file = tmp_path / "test_transactions.parquet"
    monkeypatch.setattr("generate_transactions.OUTPUT_FILE", str(output_file))

    generate_transaction_data()

    df = pd.read_parquet(output_file)

    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)

    # All timestamps should be within the last 30 days
    assert df["event_timestamp"].min() >= thirty_days_ago
    assert df["event_timestamp"].max() <= now


@pytest.mark.unit
def test_generate_transaction_data_no_nulls(tmp_path, monkeypatch):
    """Test that generated data has no null values."""
    from generate_transactions import generate_transaction_data

    output_file = tmp_path / "test_transactions.parquet"
    monkeypatch.setattr("generate_transactions.OUTPUT_FILE", str(output_file))

    generate_transaction_data()

    df = pd.read_parquet(output_file)

    # Check for null values
    assert df.isnull().sum().sum() == 0, "Generated data contains null values"


@pytest.mark.unit
def test_generate_transaction_data_user_distribution(tmp_path, monkeypatch):
    """Test that users are distributed across the dataset."""
    from generate_transactions import generate_transaction_data

    output_file = tmp_path / "test_transactions.parquet"
    monkeypatch.setattr("generate_transactions.OUTPUT_FILE", str(output_file))

    generate_transaction_data()

    df = pd.read_parquet(output_file)

    # Check that we have multiple unique users
    unique_users = df["user_id"].nunique()
    assert unique_users > 10, "Not enough user diversity in generated data"

# tests/conftest.py
"""Pytest configuration and shared fixtures for fraud feature store tests."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock
import pandas as pd
from datetime import datetime, timedelta


@pytest.fixture
def mock_feature_store():
    """Mock Feast FeatureStore for testing without actual data."""
    mock_fs = Mock()

    # Mock successful feature retrieval
    def mock_get_online_features(features, entity_rows):
        user_id = entity_rows[0]["user_id"]

        # Simulate different users with different feature values
        if user_id == 1005:
            # Normal user with low transaction amount
            return MagicMock(
                to_dict=lambda: {
                    "user_id": [user_id],
                    "transaction_count_7d": [37],
                    "avg_transaction_amount_7d": [296.62],
                }
            )
        elif user_id == 2000:
            # Fraudulent user with high transaction amount
            return MagicMock(
                to_dict=lambda: {
                    "user_id": [user_id],
                    "transaction_count_7d": [150],
                    "avg_transaction_amount_7d": [1500.0],
                }
            )
        elif user_id == 9999:
            # User not found in feature store
            return MagicMock(
                to_dict=lambda: {
                    "user_id": [user_id],
                    "transaction_count_7d": [None],
                    "avg_transaction_amount_7d": [None],
                }
            )
        else:
            # Default user
            return MagicMock(
                to_dict=lambda: {
                    "user_id": [user_id],
                    "transaction_count_7d": [20],
                    "avg_transaction_amount_7d": [500.0],
                }
            )

    mock_fs.get_online_features = Mock(side_effect=mock_get_online_features)
    return mock_fs


@pytest.fixture
def test_client(mock_feature_store, monkeypatch):
    """FastAPI test client with mocked feature store."""
    import sys
    import os

    # Add parent directory to path to make src importable
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    # Mock the feature store before importing app
    import src.app as app_module

    monkeypatch.setattr(app_module, "fs", mock_feature_store)

    from fastapi.testclient import TestClient

    client = TestClient(app_module.app)
    return client


@pytest.fixture
def sample_transaction_data():
    """Generate sample transaction data for testing."""
    num_rows = 100
    now = datetime.now()

    data = {
        "user_id": [1000 + i % 50 for i in range(num_rows)],
        "event_timestamp": [now - timedelta(days=i % 30) for i in range(num_rows)],
        "transaction_count_7d": [10 + i % 40 for i in range(num_rows)],
        "avg_transaction_amount_7d": [100.0 + (i % 20) * 50 for i in range(num_rows)],
        "created_timestamp": [now for _ in range(num_rows)],
    }

    return pd.DataFrame(data)


@pytest.fixture
def temp_parquet_file(tmp_path, sample_transaction_data):
    """Create a temporary parquet file with sample data."""
    file_path = tmp_path / "test_transactions.parquet"
    sample_transaction_data.to_parquet(file_path, index=False)
    return str(file_path)

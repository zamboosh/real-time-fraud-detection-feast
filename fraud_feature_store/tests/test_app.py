# tests/test_app.py
"""Unit tests for the FastAPI application."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch


@pytest.mark.unit
def test_health_endpoint(test_client):
    """Test the health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "feast_ready" in data


@pytest.mark.unit
def test_predict_normal_user(test_client):
    """Test prediction for a normal user with low transaction amount."""
    response = test_client.post(
        "/predict", json={"user_id": 1005, "transaction_amount": 500.0}
    )

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "is_fraud" in data
    assert "confidence" in data
    assert "features_fetched" in data

    # Normal user should not be flagged as fraud (avg < 1000)
    assert data["is_fraud"] is False
    assert data["confidence"] == 0.5

    # Check features were fetched
    features = data["features_fetched"]
    assert features["user_id"] == [1005]
    assert features["transaction_count_7d"] == [37]
    assert features["avg_transaction_amount_7d"] == [296.62]


@pytest.mark.unit
def test_predict_fraudulent_user(test_client):
    """Test prediction for a user with high average transaction amount."""
    response = test_client.post(
        "/predict", json={"user_id": 2000, "transaction_amount": 2000.0}
    )

    assert response.status_code == 200
    data = response.json()

    # High average amount user should be flagged as fraud (avg > 1000)
    assert data["is_fraud"] is True
    assert data["confidence"] == 0.9

    # Check features
    features = data["features_fetched"]
    assert features["avg_transaction_amount_7d"] == [1500.0]


@pytest.mark.unit
def test_predict_user_not_found(test_client):
    """Test prediction for a user not in the feature store."""
    response = test_client.post(
        "/predict", json={"user_id": 9999, "transaction_amount": 100.0}
    )

    # Should return 404 when user not found
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found in feature store" in data["detail"].lower()


@pytest.mark.unit
def test_predict_invalid_input(test_client):
    """Test prediction with invalid input data."""
    # Missing required field
    response = test_client.post("/predict", json={"user_id": 1005})
    assert response.status_code == 422  # Validation error

    # Invalid data type
    response = test_client.post(
        "/predict", json={"user_id": "invalid", "transaction_amount": 500.0}
    )
    assert response.status_code == 422


@pytest.mark.unit
def test_predict_feature_store_error(test_client, mock_feature_store):
    """Test prediction when feature store retrieval fails."""
    # Make the mock raise an exception
    mock_feature_store.get_online_features.side_effect = Exception(
        "Redis connection failed"
    )

    response = test_client.post(
        "/predict", json={"user_id": 1005, "transaction_amount": 500.0}
    )

    # Should return 500 when feature store fails
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "retrieval failed" in data["detail"].lower()


@pytest.mark.unit
def test_predict_feature_store_unavailable():
    """Test prediction when feature store is not initialized."""
    import sys
    import os

    # Add parent directory to path
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    with patch("src.app.fs", None):
        import src.app as app_module
        from fastapi.testclient import TestClient

        client = TestClient(app_module.app)

        response = client.post(
            "/predict", json={"user_id": 1005, "transaction_amount": 500.0}
        )

        # Should return 503 when feature store is unavailable
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert "unavailable" in data["detail"].lower()


@pytest.mark.unit
def test_fraud_detection_logic(test_client):
    """Test the fraud detection threshold logic."""
    # Test boundary cases around the 1000 threshold

    # Just below threshold - should not be fraud
    response = test_client.post(
        "/predict", json={"user_id": 1005, "transaction_amount": 500.0}
    )
    assert response.status_code == 200
    assert response.json()["is_fraud"] is False

    # Above threshold - should be fraud
    response = test_client.post(
        "/predict", json={"user_id": 2000, "transaction_amount": 2000.0}
    )
    assert response.status_code == 200
    assert response.json()["is_fraud"] is True

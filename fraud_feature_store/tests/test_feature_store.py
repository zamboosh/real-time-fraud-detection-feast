# tests/test_feature_store.py
"""Integration tests for Feast feature store definitions."""

import pytest
import sys
import os

# Add feature_repo to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "feature_repo"))


@pytest.mark.integration
def test_entity_definition():
    """Test that the user entity is properly defined."""
    from feature_store import user

    assert user.name == "user_id"
    assert user.description == "ID of the user making a transaction"


@pytest.mark.integration
def test_data_source_definition():
    """Test that the data source is properly configured."""
    from feature_store import user_transactions_source

    assert user_transactions_source.path == "data/user_transactions.parquet"
    assert user_transactions_source.timestamp_field == "event_timestamp"
    assert user_transactions_source.created_timestamp_column == "created_timestamp"


@pytest.mark.integration
def test_feature_view_definition():
    """Test that the feature view is properly configured."""
    from feature_store import user_transaction_fv
    from datetime import timedelta

    assert user_transaction_fv.name == "user_transaction_features"
    assert user_transaction_fv.ttl == timedelta(weeks=52)
    assert user_transaction_fv.online is True

    # Check schema fields
    field_names = [field.name for field in user_transaction_fv.schema]
    assert "transaction_count_7d" in field_names
    assert "avg_transaction_amount_7d" in field_names


@pytest.mark.integration
def test_feature_view_schema_types():
    """Test that feature view schema has correct data types."""
    from feature_store import user_transaction_fv
    from feast.types import Float32, Int64

    schema_dict = {field.name: field.dtype for field in user_transaction_fv.schema}

    assert schema_dict["transaction_count_7d"] == Int64
    assert schema_dict["avg_transaction_amount_7d"] == Float32


@pytest.mark.integration
def test_feature_view_entities():
    """Test that feature view is associated with correct entity."""
    from feature_store import user_transaction_fv, user

    assert len(user_transaction_fv.entities) == 1
    # In newer Feast versions, entities is a list of strings (entity names)
    assert user_transaction_fv.entities[0] == user.name


@pytest.mark.integration
def test_feature_service_definition():
    """Test that the feature service is properly configured."""
    from feature_store import fraud_feature_service, user_transaction_fv

    assert fraud_feature_service.name == "fraud_prediction_service"
    # Use _features attribute (internal API) or check via feature_view_projections
    assert len(fraud_feature_service._features) == 1


@pytest.mark.integration
def test_feature_view_source():
    """Test that feature view is connected to the correct data source."""
    from feature_store import user_transaction_fv, user_transactions_source

    assert user_transaction_fv.source == user_transactions_source


@pytest.mark.integration
def test_all_required_features_defined():
    """Test that all features required by the app are defined."""
    from feature_store import user_transaction_fv

    required_features = ["transaction_count_7d", "avg_transaction_amount_7d"]

    field_names = [field.name for field in user_transaction_fv.schema]

    for feature in required_features:
        assert feature in field_names, f"Required feature {feature} not found in schema"

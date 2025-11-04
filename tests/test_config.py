"""Tests for configuration module."""

import os
import pytest
from pathlib import Path

from time_to_shop.core.config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_config_from_env_with_defaults(self, monkeypatch):
        """Test config creation with default values."""
        monkeypatch.delenv("GCP_CREDENTIALS_PATH", raising=False)
        monkeypatch.delenv("GCP_PROJECT_ID", raising=False)

        config = Config.from_env()

        assert config.bq_dataset == "SANDBOX_ANALYTICS"
        assert config.bq_input_table == "TTS_Production"
        assert config.bq_output_table == "time_to_shop"
        assert config.model_path == "finalized_model.sav"
        assert config.log_level == "INFO"

    def test_config_from_env_with_custom_values(self, monkeypatch):
        """Test config creation with custom environment variables."""
        monkeypatch.setenv("GCP_PROJECT_ID", "test-project")
        monkeypatch.setenv("BQ_DATASET", "custom_dataset")
        monkeypatch.setenv("BQ_INPUT_TABLE", "custom_input")
        monkeypatch.setenv("BQ_OUTPUT_TABLE", "custom_output")
        monkeypatch.setenv("MODEL_PATH", "custom_model.pkl")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")

        config = Config.from_env()

        assert config.gcp_project_id == "test-project"
        assert config.bq_dataset == "custom_dataset"
        assert config.bq_input_table == "custom_input"
        assert config.bq_output_table == "custom_output"
        assert config.model_path == "custom_model.pkl"
        assert config.log_level == "DEBUG"

    def test_bq_table_properties(self):
        """Test BigQuery table name properties."""
        config = Config(
            gcp_project_id="test-project",
            bq_dataset="test_dataset",
            bq_input_table="test_input",
            bq_output_table="test_output",
        )

        assert config.bq_input_table_full == "`test-project.test_dataset.test_input`"
        assert config.bq_output_table_full == "test_dataset.test_output"

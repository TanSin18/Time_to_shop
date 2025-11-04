"""Configuration management for Time to Shop application."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Application configuration."""

    # Google Cloud settings
    gcp_project_id: Optional[str] = None
    gcp_credentials_path: Optional[str] = None

    # BigQuery settings
    bq_dataset: str = "SANDBOX_ANALYTICS"
    bq_input_table: str = "TTS_Production"
    bq_output_table: str = "time_to_shop"

    # Model settings
    model_path: str = "finalized_model.sav"

    # Logging settings
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables.

        Returns:
            Config: Configuration instance populated from environment.

        Raises:
            ValueError: If required environment variables are missing.
        """
        gcp_credentials_path = os.getenv("GCP_CREDENTIALS_PATH")
        gcp_project_id = os.getenv("GCP_PROJECT_ID")

        if not gcp_credentials_path:
            logger.warning(
                "GCP_CREDENTIALS_PATH not set. Using default or application "
                "default credentials."
            )

        if gcp_credentials_path and not Path(gcp_credentials_path).exists():
            raise ValueError(
                f"GCP credentials file not found: {gcp_credentials_path}"
            )

        return cls(
            gcp_project_id=gcp_project_id,
            gcp_credentials_path=gcp_credentials_path,
            bq_dataset=os.getenv("BQ_DATASET", cls.bq_dataset),
            bq_input_table=os.getenv("BQ_INPUT_TABLE", cls.bq_input_table),
            bq_output_table=os.getenv("BQ_OUTPUT_TABLE", cls.bq_output_table),
            model_path=os.getenv("MODEL_PATH", cls.model_path),
            log_level=os.getenv("LOG_LEVEL", cls.log_level),
        )

    @property
    def bq_input_table_full(self) -> str:
        """Get fully qualified BigQuery input table name."""
        if self.gcp_project_id:
            return f"`{self.gcp_project_id}.{self.bq_dataset}.{self.bq_input_table}`"
        return f"`{self.bq_dataset}.{self.bq_input_table}`"

    @property
    def bq_output_table_full(self) -> str:
        """Get fully qualified BigQuery output table name."""
        return f"{self.bq_dataset}.{self.bq_output_table}"

    def validate(self) -> None:
        """Validate configuration.

        Raises:
            ValueError: If configuration is invalid.
        """
        if self.gcp_credentials_path:
            if not Path(self.gcp_credentials_path).exists():
                raise ValueError(
                    f"GCP credentials file not found: {self.gcp_credentials_path}"
                )

        if self.model_path and not Path(self.model_path).exists():
            raise ValueError(f"Model file not found: {self.model_path}")

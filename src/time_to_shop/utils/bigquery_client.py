"""BigQuery client utilities."""

import logging
from typing import Optional, Tuple

import pandas as pd
from google.cloud import bigquery
from google.cloud import bigquery_storage
from google.oauth2 import service_account

from ..core.config import Config
from ..core.constants import GCP_SCOPES, OUTPUT_TABLE_SCHEMA

logger = logging.getLogger(__name__)


class BigQueryClient:
    """Wrapper for BigQuery operations."""

    def __init__(self, config: Config):
        """Initialize BigQuery client.

        Args:
            config: Application configuration.

        Raises:
            ValueError: If credentials cannot be loaded.
        """
        self.config = config
        self._credentials = self._load_credentials()
        self._bq_client: Optional[bigquery.Client] = None
        self._bq_storage_client: Optional[bigquery_storage.BigQueryReadClient] = None

    def _load_credentials(self) -> Optional[service_account.Credentials]:
        """Load GCP credentials from file or use default credentials.

        Returns:
            Service account credentials or None for default credentials.
        """
        if self.config.gcp_credentials_path:
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    self.config.gcp_credentials_path,
                    scopes=GCP_SCOPES,
                )
                logger.info(
                    f"Loaded credentials from {self.config.gcp_credentials_path}"
                )
                return credentials
            except Exception as e:
                logger.error(f"Failed to load credentials: {e}")
                raise ValueError(f"Failed to load GCP credentials: {e}") from e
        else:
            logger.info("Using application default credentials")
            return None

    @property
    def bq_client(self) -> bigquery.Client:
        """Get or create BigQuery client.

        Returns:
            BigQuery client instance.
        """
        if self._bq_client is None:
            if self._credentials:
                self._bq_client = bigquery.Client(
                    credentials=self._credentials,
                    project=self._credentials.project_id or self.config.gcp_project_id,
                )
            else:
                self._bq_client = bigquery.Client(project=self.config.gcp_project_id)
            logger.info("BigQuery client initialized")
        return self._bq_client

    @property
    def bq_storage_client(self) -> bigquery_storage.BigQueryReadClient:
        """Get or create BigQuery Storage client.

        Returns:
            BigQuery Storage client instance.
        """
        if self._bq_storage_client is None:
            if self._credentials:
                self._bq_storage_client = bigquery_storage.BigQueryReadClient(
                    credentials=self._credentials
                )
            else:
                self._bq_storage_client = bigquery_storage.BigQueryReadClient()
            logger.info("BigQuery Storage client initialized")
        return self._bq_storage_client

    def query_to_dataframe(self, query: str) -> pd.DataFrame:
        """Execute a BigQuery query and return results as DataFrame.

        Args:
            query: SQL query to execute.

        Returns:
            DataFrame containing query results.

        Raises:
            Exception: If query execution fails.
        """
        try:
            logger.info("Executing BigQuery query...")
            logger.debug(f"Query: {query}")

            result = self.bq_client.query(query).result()
            df = result.to_dataframe(bqstorage_client=self.bq_storage_client)

            logger.info(f"Query completed. Retrieved {len(df)} rows.")
            return df

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def upload_to_bigquery(
        self,
        df: pd.DataFrame,
        table_name: str,
        if_exists: str = "append",
    ) -> None:
        """Upload DataFrame to BigQuery table.

        Args:
            df: DataFrame to upload.
            table_name: Destination table name (format: dataset.table).
            if_exists: What to do if table exists ('append', 'replace', 'fail').

        Raises:
            Exception: If upload fails.
        """
        try:
            logger.info(f"Uploading {len(df)} rows to BigQuery table {table_name}...")

            project_id = (
                self._credentials.project_id
                if self._credentials
                else self.config.gcp_project_id
            )

            df.to_gbq(
                destination_table=table_name,
                project_id=project_id,
                if_exists=if_exists,
                table_schema=OUTPUT_TABLE_SCHEMA,
                credentials=self._credentials,
            )

            logger.info(f"Successfully uploaded data to {table_name}")

        except Exception as e:
            logger.error(f"Failed to upload to BigQuery: {e}")
            raise

    def close(self) -> None:
        """Close client connections."""
        if self._bq_client:
            self._bq_client.close()
            logger.info("BigQuery client closed")
        # BigQuery Storage client doesn't have a close method

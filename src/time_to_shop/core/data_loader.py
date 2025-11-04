"""Data loading and preprocessing functions."""

import logging
from typing import Optional

import pandas as pd
import numpy as np

from .config import Config
from .constants import (
    FILL_VALUE_DECILE,
    FILL_VALUE_RECENCY,
    FILL_VALUE_DEFAULT,
    KEY_COLUMNS,
    INT_COLUMNS,
)
from ..utils.bigquery_client import BigQueryClient

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles data loading and preprocessing."""

    def __init__(self, config: Config):
        """Initialize DataLoader.

        Args:
            config: Application configuration.
        """
        self.config = config
        self.bq_client = BigQueryClient(config)

    def load_data(self, query: Optional[str] = None) -> pd.DataFrame:
        """Load data from BigQuery.

        Args:
            query: Optional SQL query. If None, uses default production table.

        Returns:
            Preprocessed DataFrame ready for prediction.
        """
        if query is None:
            query = f"SELECT * FROM {self.config.bq_input_table_full}"

        logger.info("Loading data from BigQuery...")
        df = self.bq_client.query_to_dataframe(query)

        logger.info(f"Loaded {len(df)} records. Starting preprocessing...")
        df = self._preprocess_data(df)

        return df

    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess raw data for prediction.

        Args:
            df: Raw DataFrame from BigQuery.

        Returns:
            Preprocessed DataFrame.
        """
        df = df.copy()

        # Handle missing values with specific rules
        df = self._fill_missing_values(df)

        # Fix negative values in specific columns
        df = self._fix_negative_values(df)

        # Convert data types
        df = self._convert_data_types(df)

        logger.info("Data preprocessing completed")
        return df

    def _fill_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill missing values based on column type.

        Args:
            df: DataFrame with missing values.

        Returns:
            DataFrame with filled values.
        """
        for col in df.columns:
            if 'DECILE' in col:
                # Deciles: fill with 11 (represents missing/no activity)
                df[col].fillna(FILL_VALUE_DECILE, inplace=True)
            elif '_R' in col and 'DECILE' not in col:
                # Recency columns: fill with 366 (more than a year)
                df[col].fillna(FILL_VALUE_RECENCY, inplace=True)
            else:
                # All other columns: fill with 0
                df[col].fillna(FILL_VALUE_DEFAULT, inplace=True)

        return df

    def _fix_negative_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fix negative values in monetary columns.

        Args:
            df: DataFrame potentially containing negative values.

        Returns:
            DataFrame with negative values corrected.
        """
        # Sales and coupon expense should not be negative
        if 'SALES_6M' in df.columns:
            negative_sales = (df['SALES_6M'] < 0).sum()
            if negative_sales > 0:
                logger.warning(f"Found {negative_sales} negative SALES_6M values, setting to 0")
                df.loc[df['SALES_6M'] < 0, 'SALES_6M'] = 0

        if 'COUPON_EXPENSE_6M' in df.columns:
            negative_coupons = (df['COUPON_EXPENSE_6M'] < 0).sum()
            if negative_coupons > 0:
                logger.warning(
                    f"Found {negative_coupons} negative COUPON_EXPENSE_6M values, setting to 0"
                )
                df.loc[df['COUPON_EXPENSE_6M'] < 0, 'COUPON_EXPENSE_6M'] = 0

        return df

    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert columns to appropriate data types.

        Args:
            df: DataFrame with mixed types.

        Returns:
            DataFrame with corrected types.
        """
        # Convert key columns to object type (for IDs)
        for col in KEY_COLUMNS:
            if col in df.columns:
                df[col] = df[col].astype("object")

        # Convert numeric columns to int
        for col in INT_COLUMNS:
            if col in df.columns:
                df[col] = df[col].astype('int')

        return df

    def close(self) -> None:
        """Close BigQuery client connections."""
        self.bq_client.close()

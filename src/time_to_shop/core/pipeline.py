"""Main prediction pipeline orchestration."""

import logging
from typing import Optional

import pandas as pd

from .config import Config
from .data_loader import DataLoader
from ..models.predictor import PurchasePredictor
from ..utils.bigquery_client import BigQueryClient

logger = logging.getLogger(__name__)


class PredictionPipeline:
    """Orchestrates the end-to-end prediction workflow."""

    def __init__(self, config: Config):
        """Initialize pipeline.

        Args:
            config: Application configuration.
        """
        self.config = config
        self.data_loader = DataLoader(config)
        self.predictor = PurchasePredictor(config)
        self.bq_client = BigQueryClient(config)

    def run(
        self,
        query: Optional[str] = None,
        upload_to_bq: bool = True,
        save_local: bool = False,
        output_path: Optional[str] = None,
    ) -> pd.DataFrame:
        """Run the complete prediction pipeline.

        Args:
            query: Optional SQL query for data loading.
            upload_to_bq: Whether to upload results to BigQuery.
            save_local: Whether to save results locally.
            output_path: Path for local CSV output (if save_local=True).

        Returns:
            DataFrame containing predictions.

        Raises:
            Exception: If any pipeline step fails.
        """
        try:
            logger.info("=" * 80)
            logger.info("Starting Time to Shop prediction pipeline")
            logger.info("=" * 80)

            # Step 1: Load and preprocess data
            logger.info("\n[Step 1/4] Loading data...")
            data = self.data_loader.load_data(query)
            logger.info(f"✓ Loaded {len(data)} customer records")

            # Step 2: Load model
            logger.info("\n[Step 2/4] Loading prediction model...")
            self.predictor.load_model()
            logger.info("✓ Model loaded")

            # Step 3: Generate predictions
            logger.info("\n[Step 3/4] Generating predictions...")
            predictions = self.predictor.predict(data)
            predictions = self._prepare_output(predictions)
            logger.info(f"✓ Generated predictions for {len(predictions)} customers")

            # Step 4: Save results
            logger.info("\n[Step 4/4] Saving results...")

            if upload_to_bq:
                self._upload_to_bigquery(predictions)
                logger.info(f"✓ Uploaded to BigQuery: {self.config.bq_output_table_full}")

            if save_local:
                path = output_path or "predictions_output.csv"
                predictions.to_csv(path, index=False)
                logger.info(f"✓ Saved locally: {path}")

            logger.info("\n" + "=" * 80)
            logger.info("Pipeline completed successfully!")
            logger.info("=" * 80)

            self._print_summary(predictions)

            return predictions

        except Exception as e:
            logger.error(f"\n❌ Pipeline failed: {e}", exc_info=True)
            raise

        finally:
            # Cleanup
            self.data_loader.close()
            self.bq_client.close()

    def _prepare_output(self, predictions: pd.DataFrame) -> pd.DataFrame:
        """Prepare output data with correct types.

        Args:
            predictions: Raw predictions DataFrame.

        Returns:
            Formatted predictions DataFrame.
        """
        output = predictions.copy()

        # Reset index
        output.reset_index(drop=True, inplace=True)

        # Convert types
        output['CUSTOMER_ID'] = output['CUSTOMER_ID'].astype(int)
        output['PREVIOUS_PURCHASE'] = pd.to_datetime(output['PREVIOUS_PURCHASE'])
        output['DECILE'] = output['DECILE'].astype(int)
        output['P'] = output['P'].astype(float)

        return output

    def _upload_to_bigquery(self, predictions: pd.DataFrame) -> None:
        """Upload predictions to BigQuery.

        Args:
            predictions: Predictions DataFrame to upload.
        """
        self.bq_client.upload_to_bigquery(
            predictions,
            self.config.bq_output_table_full,
            if_exists='append'
        )

    def _print_summary(self, predictions: pd.DataFrame) -> None:
        """Print summary statistics.

        Args:
            predictions: Predictions DataFrame.
        """
        logger.info("\n📊 Prediction Summary:")
        logger.info(f"   Total customers: {len(predictions):,}")
        logger.info(f"   Average probability: {predictions['P'].mean():.4f}")
        logger.info(f"   High-value customers (Decile 10): {(predictions['DECILE'] == 10).sum():,}")
        logger.info(f"   Low-value customers (Decile 1): {(predictions['DECILE'] == 1).sum():,}")

"""Prediction functionality using trained models."""

import logging
import pickle
from pathlib import Path
from typing import Any, Union

import pandas as pd
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier

from ..core.config import Config
from ..core.constants import FEATURE_COLUMNS, DECILE_BINS, DECILE_LABELS

logger = logging.getLogger(__name__)


class PurchasePredictor:
    """Predicts customer purchase likelihood within 90 days."""

    def __init__(self, config: Config):
        """Initialize predictor.

        Args:
            config: Application configuration.
        """
        self.config = config
        self.model: Optional[ExtraTreesClassifier] = None

    def load_model(self, model_path: Optional[str] = None) -> None:
        """Load trained model from disk.

        Args:
            model_path: Path to model file. If None, uses config path.

        Raises:
            FileNotFoundError: If model file doesn't exist.
            Exception: If model loading fails.
        """
        path = model_path or self.config.model_path
        model_file = Path(path)

        if not model_file.exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        try:
            logger.info(f"Loading model from {path}...")
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def predict(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate predictions for customer purchase likelihood.

        Args:
            data: Preprocessed customer data.

        Returns:
            DataFrame with predictions including:
                - CUSTOMER_ID: Customer identifier
                - PREVIOUS_PURCHASE: Date of last purchase
                - P: Probability of purchase (0-1)
                - DECILE: Probability decile (10=highest, 1=lowest)

        Raises:
            ValueError: If model is not loaded or required features missing.
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        # Validate features
        missing_features = set(FEATURE_COLUMNS) - set(data.columns)
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")

        logger.info(f"Generating predictions for {len(data)} customers...")

        # Extract features
        X = data[FEATURE_COLUMNS]

        # Generate predictions
        try:
            # Get probability estimates
            probabilities = self.model.predict_proba(X)
            prob_purchase = probabilities[:, 1]  # Probability of class 1 (purchase)

            # Create output DataFrame
            output = pd.DataFrame({
                'CUSTOMER_ID': data['CUSTOMER_ID'].values,
                'PREVIOUS_PURCHASE': data['PREVIOUS_PURCHASE'].values,
                'P': prob_purchase
            })

            # Assign deciles based on probability bins
            output['DECILE'] = pd.cut(
                output['P'],
                bins=DECILE_BINS,
                labels=DECILE_LABELS
            )

            logger.info("Predictions generated successfully")
            logger.info(f"Probability distribution:\n{output['P'].describe()}")
            logger.info(f"Decile distribution:\n{output['DECILE'].value_counts().sort_index()}")

            return output

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise

    def predict_with_metadata(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate predictions with additional metadata.

        Args:
            data: Preprocessed customer data.

        Returns:
            DataFrame with predictions and class labels.
        """
        output = self.predict(data)

        # Add predicted class (binary: will purchase or not)
        y_pred = self.model.predict(data[FEATURE_COLUMNS])
        output['PREDICTED_CLASS'] = y_pred

        return output

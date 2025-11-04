"""Pytest configuration and fixtures."""

import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_customer_data():
    """Create sample customer data for testing."""
    np.random.seed(42)

    data = {
        'CUSTOMER_ID': [1001, 1002, 1003, 1004, 1005],
        'ADDRESS_ID': [2001, 2002, 2003, 2004, 2005],
        'PREVIOUS_PURCHASE': pd.date_range('2024-01-01', periods=5),
        'SALES_6M': [100, 250, 50, 400, 150],
        'FREQUENCY_6M': [2, 5, 1, 8, 3],
        'BUYS_Q_03': [1, 2, 0, 3, 1],
        'COUPON_Q_03': [0, 1, 0, 2, 1],
        'PH_MREDEEM90D': [0, 1, 0, 2, 0],
        'PH_PFREQ90D': [1, 3, 0, 5, 2],
        'PH_CFREQ90D': [0, 2, 0, 3, 1],
        'BBB_INSTORE_RFM_DECILE': [5, 8, 3, 10, 6],
        'BBB_ECOM_R_DECILE': [4, 7, 2, 9, 5],
        'BBB_OFFCOUPON_RFM_DECILE': [3, 6, 2, 8, 4],
        'NUM_PERIODS': [2, 4, 1, 6, 3],
        'NUM_PRODUCT_GROUPS': [3, 5, 2, 8, 4],
        'PRESENCE_OF_CHILD': [1, 2, 99, 1, 2],
        'MARITAL_STAT': [1, 2, 1, 2, 99],
    }

    return pd.DataFrame(data)


@pytest.fixture
def sample_predictions():
    """Create sample predictions for testing."""
    data = {
        'CUSTOMER_ID': [1001, 1002, 1003, 1004, 1005],
        'PREVIOUS_PURCHASE': pd.date_range('2024-01-01', periods=5),
        'P': [0.25, 0.65, 0.15, 0.85, 0.45],
        'DECILE': [8, 7, 10, 3, 6],
    }
    return pd.DataFrame(data)

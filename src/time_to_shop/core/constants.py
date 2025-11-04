"""Constants used throughout the Time to Shop application."""

from typing import List

# Feature columns used for prediction
FEATURE_COLUMNS: List[str] = [
    'SALES_6M',
    'FREQUENCY_6M',
    'BUYS_Q_03',
    'COUPON_Q_03',
    'PH_MREDEEM90D',
    'PH_PFREQ90D',
    'PH_CFREQ90D',
    'BBB_INSTORE_RFM_DECILE',
    'BBB_ECOM_R_DECILE',
    'BBB_OFFCOUPON_RFM_DECILE',
    'NUM_PERIODS',
    'NUM_PRODUCT_GROUPS',
    'PRESENCE_OF_CHILD',
    'MARITAL_STAT'
]

# Key columns (IDs)
KEY_COLUMNS: List[str] = ['CUSTOMER_ID', 'ADDRESS_ID']

# Integer type columns
INT_COLUMNS: List[str] = [
    'SALES_6M',
    'COUPON_EXPENSE_6M',
    'BUYS_Q_03',
    'COUPON_Q_03',
    'PH_MREDEEM90D',
    'PH_PFREQ90D',
    'PH_CFREQ90D',
    'BBB_INSTORE_RFM_DECILE',
    'BBB_ECOM_R_DECILE',
    'BBB_OFFCOUPON_RFM_DECILE',
    'PCT_TXNS_ON_MKD_DISC'
]

# Default fill values for missing data
FILL_VALUE_DECILE = 11
FILL_VALUE_RECENCY = 366
FILL_VALUE_DEFAULT = 0

# Decile bin edges for probability bucketing
DECILE_BINS: List[float] = [
    0.00, 0.19662877, 0.21054794, 0.25123934, 0.26712146,
    0.42682036, 0.493293, 0.59348687, 0.67486295, 0.77079006, 1.0
]

# Decile labels (10 = highest probability, 1 = lowest)
DECILE_LABELS: List[str] = ['10', '9', '8', '7', '6', '5', '4', '3', '2', '1']

# BigQuery table schema for output
OUTPUT_TABLE_SCHEMA = [
    {'name': 'CUSTOMER_ID', 'type': 'INTEGER'},
    {'name': 'PREVIOUS_PURCHASE', 'type': 'DATETIME'},
    {'name': 'DECILE', 'type': 'INTEGER'},
    {'name': 'P', 'type': 'FLOAT'}
]

# Google Cloud scopes
GCP_SCOPES: List[str] = ["https://www.googleapis.com/auth/cloud-platform"]

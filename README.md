# Time to Shop - Customer Purchase Prediction System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A machine learning system to predict the likelihood of customers making their next purchase within 90 days from their last purchase. This helps identify repeat purchase opportunities and distinguish one-time shoppers from potential returning customers.

## Overview

### Business Problem
Majority of customers are one-time shoppers. The business needs to:
- Identify customers likely to make repeat purchases
- Target marketing efforts effectively
- Reduce customer acquisition costs by focusing on retention

### Solution
This system predicts the probability (0-1) that a customer will make their next purchase within 90 days from their last purchase date. Customers are segmented into deciles based on their purchase likelihood for targeted marketing campaigns.

### Model Details
- **Algorithm**: Extra Trees Classifier (ensemble method)
- **Input**: Customer transaction and demographic data from the past 6-12 months
- **Output**: Purchase probability and decile score (10 = highest likelihood, 1 = lowest)

## Features

- **Modular Architecture**: Clean separation of concerns (data loading, prediction, output)
- **Configuration Management**: Environment variables and YAML-based configuration
- **Robust Error Handling**: Comprehensive logging and error management
- **Type Safety**: Type hints throughout the codebase
- **Modern Python**: Uses pyproject.toml, follows best practices
- **BigQuery Integration**: Seamless data loading and result storage
- **CLI Interface**: Easy-to-use command-line interface

## Installation

### Prerequisites
- Python 3.8 or higher
- Google Cloud Platform account with BigQuery access
- GCP service account credentials (JSON file)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/TanSin18/Time_to_shop.git
   cd Time_to_shop
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the package**
   ```bash
   pip install -e .
   ```

   Or for development:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Configure your credentials**
   ```bash
   export GCP_CREDENTIALS_PATH=/path/to/your/service-account.json
   export GCP_PROJECT_ID=your-project-id
   ```

## Usage

### Command Line Interface

**Basic usage:**
```bash
time-to-shop
```

**With custom query:**
```bash
time-to-shop --query "SELECT * FROM my_dataset.my_table LIMIT 1000"
```

**Save results locally:**
```bash
time-to-shop --save-local --output predictions.csv
```

**Skip BigQuery upload:**
```bash
time-to-shop --no-upload --save-local
```

**Custom logging:**
```bash
time-to-shop --log-level DEBUG --log-file app.log
```

### Python API

```python
from time_to_shop.core.config import Config
from time_to_shop.core.pipeline import PredictionPipeline
from time_to_shop.utils.logger import setup_logging

# Setup
setup_logging("INFO")
config = Config.from_env()

# Run pipeline
pipeline = PredictionPipeline(config)
predictions = pipeline.run(
    upload_to_bq=True,
    save_local=True,
    output_path="predictions.csv"
)

# Access results
print(predictions.head())
print(f"High-value customers: {(predictions['DECILE'] == 10).sum()}")
```

### Using Individual Components

```python
from time_to_shop.core.config import Config
from time_to_shop.core.data_loader import DataLoader
from time_to_shop.models.predictor import PurchasePredictor

# Load data
config = Config.from_env()
loader = DataLoader(config)
data = loader.load_data()

# Make predictions
predictor = PurchasePredictor(config)
predictor.load_model()
predictions = predictor.predict(data)
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GCP_CREDENTIALS_PATH` | Path to GCP service account JSON | Required |
| `GCP_PROJECT_ID` | GCP project ID | From credentials |
| `BQ_DATASET` | BigQuery dataset name | `SANDBOX_ANALYTICS` |
| `BQ_INPUT_TABLE` | Input table name | `TTS_Production` |
| `BQ_OUTPUT_TABLE` | Output table name | `time_to_shop` |
| `MODEL_PATH` | Path to model file | `finalized_model.sav` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Configuration File

Edit `config/config.yaml` to customize default settings:

```yaml
bigquery:
  dataset: SANDBOX_ANALYTICS
  input_table: TTS_Production
  output_table: time_to_shop

model:
  path: finalized_model.sav

logging:
  level: INFO
```

## Project Structure

```
Time_to_shop/
├── src/
│   └── time_to_shop/
│       ├── core/
│       │   ├── config.py          # Configuration management
│       │   ├── constants.py       # Application constants
│       │   ├── data_loader.py     # Data loading & preprocessing
│       │   └── pipeline.py        # Main orchestration
│       ├── models/
│       │   └── predictor.py       # ML prediction logic
│       ├── utils/
│       │   ├── bigquery_client.py # BigQuery operations
│       │   └── logger.py          # Logging setup
│       ├── cli.py                 # Command-line interface
│       └── __main__.py            # Package entry point
├── tests/                         # Unit tests
├── notebooks/                     # Jupyter notebooks
├── config/                        # Configuration files
├── docs/                          # Documentation
├── pyproject.toml                 # Project metadata & dependencies
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies
└── README.md                      # This file
```

## Development

### Setup Development Environment

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run tests with coverage
pytest --cov=src/time_to_shop --cov-report=html

# Format code
black src/ tests/
isort src/ tests/

# Lint code
flake8 src/ tests/
pylint src/time_to_shop

# Type checking
mypy src/time_to_shop
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_predictor.py

# Run with verbose output
pytest -v
```

### Code Quality

This project uses:
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pylint**: Code analysis
- **pre-commit**: Git hooks for code quality

## Data Schema

### Input Features

| Feature | Type | Description |
|---------|------|-------------|
| `SALES_6M` | int | Total sales in last 6 months |
| `FREQUENCY_6M` | int | Purchase frequency in last 6 months |
| `BUYS_Q_03` | int | Purchases in Q3 |
| `COUPON_Q_03` | int | Coupons used in Q3 |
| `PH_MREDEEM90D` | int | Mail coupons redeemed in 90 days |
| `PH_PFREQ90D` | int | Purchase frequency in 90 days |
| `PH_CFREQ90D` | int | Coupon frequency in 90 days |
| `BBB_INSTORE_RFM_DECILE` | int | In-store RFM decile |
| `BBB_ECOM_R_DECILE` | int | E-commerce recency decile |
| `BBB_OFFCOUPON_RFM_DECILE` | int | Offline coupon RFM decile |
| `NUM_PERIODS` | int | Number of purchase periods |
| `NUM_PRODUCT_GROUPS` | int | Number of product groups purchased |
| `PRESENCE_OF_CHILD` | int | Child presence indicator |
| `MARITAL_STAT` | int | Marital status indicator |

### Output Schema

| Column | Type | Description |
|--------|------|-------------|
| `CUSTOMER_ID` | INTEGER | Customer identifier |
| `PREVIOUS_PURCHASE` | DATETIME | Last purchase date |
| `P` | FLOAT | Purchase probability (0-1) |
| `DECILE` | INTEGER | Probability decile (10-1) |

## Model Performance

The model segments customers into 10 deciles based on purchase probability:
- **Decile 10**: Highest probability (>77% likelihood)
- **Decile 1**: Lowest probability (<20% likelihood)

Use higher deciles for targeted marketing campaigns to maximize ROI.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`pytest && black . && flake8`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Troubleshooting

### Common Issues

**Issue: `FileNotFoundError: Model file not found`**
- Ensure `finalized_model.sav` is in the project root
- Or specify custom path via `MODEL_PATH` environment variable

**Issue: `ValueError: Failed to load GCP credentials`**
- Check that `GCP_CREDENTIALS_PATH` points to valid JSON file
- Verify the service account has BigQuery permissions

**Issue: `Permission denied on BigQuery table`**
- Ensure service account has `bigquery.tables.get` and `bigquery.tables.getData` permissions
- For uploads, need `bigquery.tables.create` and `bigquery.tables.updateData`

## License

This project is licensed under the terms specified in the LICENSE file.

## Authors

- **Tanmay Sinnarkar** - *Initial work*

## Acknowledgments

- Original research and model development by the Bed Bath & Beyond analytics team
- Built with scikit-learn, pandas, and Google Cloud Platform

## Changelog

### Version 2.0.0 (Current)
- Complete refactoring with modular architecture
- Added configuration management
- Improved error handling and logging
- Added type hints and comprehensive documentation
- Modern Python packaging with pyproject.toml
- CLI interface for easy usage
- Pre-commit hooks and code quality tools

### Version 1.0.0
- Initial implementation with basic functionality

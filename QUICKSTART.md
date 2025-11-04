# Quick Start Guide

Get Time to Shop up and running in 5 minutes.

## Prerequisites

- Python 3.8+
- GCP service account with BigQuery access
- Service account credentials JSON file

## Installation

```bash
# 1. Clone and enter directory
git clone https://github.com/TanSin18/Time_to_shop.git
cd Time_to_shop

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install package
pip install -e .
```

## Configuration

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your settings
nano .env  # or use your preferred editor

# Required settings:
# GCP_CREDENTIALS_PATH=/path/to/your/service-account.json
# GCP_PROJECT_ID=your-project-id
```

## Run Predictions

```bash
# Basic run (uploads to BigQuery)
time-to-shop

# Save results locally
time-to-shop --save-local --output predictions.csv

# Test without uploading
time-to-shop --no-upload --save-local

# Custom query
time-to-shop --query "SELECT * FROM my_table LIMIT 100"
```

## Verify Results

```bash
# Check output file
head predictions.csv

# Check BigQuery table
bq query "SELECT COUNT(*) FROM SANDBOX_ANALYTICS.time_to_shop"
```

## Python Usage

```python
from time_to_shop.core.config import Config
from time_to_shop.core.pipeline import PredictionPipeline

config = Config.from_env()
pipeline = PredictionPipeline(config)
predictions = pipeline.run()

print(predictions.head())
```

## Troubleshooting

**Problem**: `ModuleNotFoundError: No module named 'time_to_shop'`
```bash
pip install -e .
```

**Problem**: `FileNotFoundError: Model file not found`
```bash
# Ensure model is in project root
ls finalized_model.sav

# Or set custom path
export MODEL_PATH=/path/to/model.sav
```

**Problem**: `ValueError: Failed to load GCP credentials`
```bash
# Check file exists
ls -l $GCP_CREDENTIALS_PATH

# Verify path in .env
cat .env | grep GCP_CREDENTIALS_PATH
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Review [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) if migrating from v1.0
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## Getting Help

- GitHub Issues: https://github.com/TanSin18/Time_to_shop/issues
- Documentation: See README.md

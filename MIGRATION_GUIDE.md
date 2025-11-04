# Migration Guide: v1.0 to v2.0

This guide helps you migrate from the old `scorer.py` script to the new modular v2.0 architecture.

## Overview of Changes

### What Changed
- **Modular structure**: Single file split into multiple modules
- **Configuration**: Hardcoded values moved to environment variables and config files
- **Error handling**: Comprehensive error handling and logging
- **Type safety**: Type hints throughout
- **Modern packaging**: Uses pyproject.toml instead of setup.py
- **CLI interface**: New command-line tool with arguments

### What Stayed the Same
- **Model**: Same ExtraTreesClassifier model
- **Features**: Same 14 features used for prediction
- **Output**: Same prediction schema (CUSTOMER_ID, PREVIOUS_PURCHASE, P, DECILE)
- **BigQuery integration**: Same data source and destination

## Migration Steps

### 1. Update Project Structure

**Old structure:**
```
Time_to_shop/
├── scorer.py
├── finalized_model.sav
└── requirements.txt
```

**New structure:**
```
Time_to_shop/
├── src/
│   └── time_to_shop/
│       ├── core/
│       ├── models/
│       └── utils/
├── config/
├── tests/
└── finalized_model.sav
```

### 2. Update Dependencies

**Old way:**
```bash
pip install -r requirements.txt
```

**New way:**
```bash
# For production
pip install -e .

# For development
pip install -e ".[dev]"
```

### 3. Configuration Changes

**Old way (hardcoded in scorer.py):**
```python
key_path = '/home/jupyter/d00_key.json'
QUERY = """SELECT * FROM `dw-bq-data-d00.SANDBOX_ANALYTICS.TTS_Production`"""
output_name = 'time_to_shop'
```

**New way (environment variables):**
```bash
# Create .env file
cp .env.example .env

# Edit .env with your values
export GCP_CREDENTIALS_PATH=/path/to/your/credentials.json
export GCP_PROJECT_ID=dw-bq-data-d00
export BQ_DATASET=SANDBOX_ANALYTICS
export BQ_INPUT_TABLE=TTS_Production
export BQ_OUTPUT_TABLE=time_to_shop
export MODEL_PATH=finalized_model.sav
```

### 4. Code Migration

#### Old Code (scorer.py)
```python
from google.oauth2 import service_account
from google.cloud import bigquery
import pandas as pd
import pickle

key_path = '/home/jupyter/d00_key.json'
credentials = service_account.Credentials.from_service_account_file(
    key_path,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

def main():
    QUERY = """SELECT * FROM `dw-bq-data-d00.SANDBOX_ANALYTICS.TTS_Production`"""
    model = pickle.load(open('finalized_model.sav', 'rb'))
    data = data_upload(QUERY)
    output = extratrees_predict(data, model)
    copy_results_to_bq(output, 'time_to_shop', credentials)

if __name__ == "__main__":
    main()
```

#### New Code (CLI)
```bash
# Simple usage with environment variables
time-to-shop

# Or with custom parameters
time-to-shop --query "SELECT * FROM my_table" --save-local
```

#### New Code (Python API)
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
    save_local=False
)
```

### 5. Function Mapping

| Old Function | New Location | Notes |
|--------------|--------------|-------|
| `get_client()` | `utils.bigquery_client.BigQueryClient` | Now a class with better error handling |
| `data_upload()` | `core.data_loader.DataLoader.load_data()` | Separated loading and preprocessing |
| `extratrees_predict()` | `models.predictor.PurchasePredictor.predict()` | Cleaner interface |
| `copy_results_to_bq()` | `utils.bigquery_client.BigQueryClient.upload_to_bigquery()` | More generic |
| `main()` | `cli.main()` or `core.pipeline.PredictionPipeline.run()` | Orchestration layer |

### 6. Running in Production

#### Old Way
```python
python scorer.py
```

#### New Way

**Option 1: CLI**
```bash
time-to-shop
```

**Option 2: Python Module**
```bash
python -m time_to_shop
```

**Option 3: Programmatically**
```python
from time_to_shop.cli import main
main()
```

### 7. Scheduled Jobs / Cron

**Old crontab:**
```
0 2 * * * cd /path/to/project && python scorer.py
```

**New crontab:**
```
0 2 * * * cd /path/to/project && /path/to/venv/bin/time-to-shop --log-file /var/log/tts.log
```

Or use the Python module:
```
0 2 * * * cd /path/to/project && /path/to/venv/bin/python -m time_to_shop
```

### 8. Custom Queries

**Old way:**
```python
# Edit scorer.py
QUERY = """SELECT * FROM custom_table WHERE condition = true"""
```

**New way:**
```bash
time-to-shop --query "SELECT * FROM custom_table WHERE condition = true"
```

Or in Python:
```python
pipeline = PredictionPipeline(config)
predictions = pipeline.run(
    query="SELECT * FROM custom_table WHERE condition = true"
)
```

### 9. Logging

**Old way:**
```python
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.info("Message")
```

**New way:**
```bash
# Set log level via environment
export LOG_LEVEL=DEBUG
time-to-shop --log-file app.log
```

Or in Python:
```python
from time_to_shop.utils.logger import setup_logging
setup_logging("DEBUG", log_file="app.log")
```

### 10. Error Handling

The new version has comprehensive error handling:

```python
try:
    pipeline = PredictionPipeline(config)
    predictions = pipeline.run()
except FileNotFoundError as e:
    print(f"Model or credentials file not found: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Testing Your Migration

### 1. Verify Configuration
```bash
# Check environment variables are set
env | grep GCP
env | grep BQ
env | grep MODEL
```

### 2. Test with Dry Run
```bash
# Run without uploading to BigQuery
time-to-shop --no-upload --save-local --output test_predictions.csv
```

### 3. Verify Output
```python
import pandas as pd

# Load predictions
df = pd.read_csv("test_predictions.csv")

# Check schema
assert set(df.columns) == {'CUSTOMER_ID', 'PREVIOUS_PURCHASE', 'P', 'DECILE'}

# Check data types
assert df['CUSTOMER_ID'].dtype == 'int64'
assert df['DECILE'].dtype == 'int64'
assert df['P'].dtype == 'float64'

print("✓ Output schema matches expected format")
```

### 4. Compare Results
```python
# Compare old vs new predictions
old_predictions = pd.read_csv("old_output.csv")
new_predictions = pd.read_csv("new_output.csv")

# Should match exactly
pd.testing.assert_frame_equal(
    old_predictions.sort_values('CUSTOMER_ID').reset_index(drop=True),
    new_predictions.sort_values('CUSTOMER_ID').reset_index(drop=True)
)
print("✓ Predictions match!")
```

## Troubleshooting

### Issue: Import Errors
```
ModuleNotFoundError: No module named 'time_to_shop'
```

**Solution:**
```bash
# Install package in editable mode
pip install -e .
```

### Issue: Credentials Not Found
```
ValueError: GCP credentials file not found
```

**Solution:**
```bash
# Set correct path
export GCP_CREDENTIALS_PATH=/absolute/path/to/credentials.json

# Verify file exists
ls -l $GCP_CREDENTIALS_PATH
```

### Issue: Model Not Found
```
FileNotFoundError: Model file not found: finalized_model.sav
```

**Solution:**
```bash
# Model should be in project root or specify custom path
export MODEL_PATH=/absolute/path/to/finalized_model.sav
```

## Rollback Plan

If you need to rollback to v1.0:

```bash
# Restore old scorer.py
git checkout v1.0 -- scorer.py

# Use old requirements
git checkout v1.0 -- requirements.txt

# Install old dependencies
pip install -r requirements.txt

# Run old script
python scorer.py
```

## Getting Help

- Check the [README.md](README.md) for detailed documentation
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- Open a GitHub issue for bugs or questions
- Check existing issues for similar problems

## Benefits of Migration

1. **Better maintainability**: Modular code is easier to update
2. **Easier testing**: Each component can be tested independently
3. **Flexible configuration**: No code changes needed for different environments
4. **Better error handling**: Clear error messages and logging
5. **Type safety**: Catch errors before runtime with type hints
6. **Modern tooling**: Pre-commit hooks, automatic formatting, etc.
7. **Better documentation**: Comprehensive docstrings and guides

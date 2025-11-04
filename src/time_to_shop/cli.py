"""Command-line interface for Time to Shop."""

import argparse
import sys
from pathlib import Path

from .core.config import Config
from .core.pipeline import PredictionPipeline
from .utils.logger import setup_logging


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Time to Shop - Customer Purchase Prediction System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with environment variables
  python -m time_to_shop.cli

  # Run with custom query
  python -m time_to_shop.cli --query "SELECT * FROM my_table LIMIT 1000"

  # Save results locally
  python -m time_to_shop.cli --save-local --output predictions.csv

  # Run without uploading to BigQuery
  python -m time_to_shop.cli --no-upload

Environment Variables:
  GCP_CREDENTIALS_PATH    Path to GCP service account JSON file
  GCP_PROJECT_ID          GCP project ID
  BQ_DATASET              BigQuery dataset name (default: SANDBOX_ANALYTICS)
  BQ_INPUT_TABLE          Input table name (default: TTS_Production)
  BQ_OUTPUT_TABLE         Output table name (default: time_to_shop)
  MODEL_PATH              Path to model file (default: finalized_model.sav)
  LOG_LEVEL               Logging level (default: INFO)
        """
    )

    parser.add_argument(
        "--query",
        type=str,
        help="Custom SQL query for data loading",
    )

    parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Skip uploading results to BigQuery",
    )

    parser.add_argument(
        "--save-local",
        action="store_true",
        help="Save predictions to local CSV file",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="predictions_output.csv",
        help="Output CSV filename (when --save-local is used)",
    )

    parser.add_argument(
        "--model-path",
        type=str,
        help="Path to trained model file (overrides env/config)",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (overrides env/config)",
    )

    parser.add_argument(
        "--log-file",
        type=str,
        help="Path to log file (default: console only)",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    args = parse_args()

    try:
        # Load configuration
        config = Config.from_env()

        # Override config with CLI arguments
        if args.model_path:
            config.model_path = args.model_path
        if args.log_level:
            config.log_level = args.log_level

        # Setup logging
        setup_logging(config.log_level, args.log_file)

        # Validate configuration
        config.validate()

        # Run pipeline
        pipeline = PredictionPipeline(config)
        pipeline.run(
            query=args.query,
            upload_to_bq=not args.no_upload,
            save_local=args.save_local,
            output_path=args.output,
        )

        return 0

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 130

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

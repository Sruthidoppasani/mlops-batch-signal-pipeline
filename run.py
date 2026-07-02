import os
import sys
import json
import time
import argparse
import logging
import yaml
import numpy as np
import pandas as pd

from io import StringIO


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="MLOps Technical Assessment"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to input CSV file"
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML config file"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output metrics JSON file"
    )

    parser.add_argument(
        "--log-file",
        required=True,
        help="Log file path"
    )

    return parser.parse_args()


def setup_logging(log_file):
    logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filemode="w"

    )


def load_config(config_path):

    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"Config file '{config_path}' not found."
        )

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    return config


def validate_config(config):

    if config is None:
        raise ValueError("Config file is empty.")

    required_keys = ["seed", "window", "version"]

    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config field: {key}")

    if not isinstance(config["window"], int):
        raise ValueError("Window must be an integer.")

    if config["window"] <= 0:
        raise ValueError("Window must be greater than 0.")
    
def load_dataset(input_path):

   
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file '{input_path}' not found.")

    with open(input_path, "r", encoding="utf-8") as f:
        raw_text = f.read().strip()

    if not raw_text:
        raise ValueError("Input CSV is empty.")

    if raw_text.startswith('"') and raw_text.endswith('"'):
        lines = raw_text.splitlines()
        cleaned_lines = [line.strip('"') for line in lines]
        raw_text = "\n".join(cleaned_lines)

    try:
        df = pd.read_csv(StringIO(raw_text))
    except Exception:
        raise ValueError("Invalid CSV format.")

    if df.empty:
        raise ValueError("CSV contains no rows.")

    df.columns = df.columns.str.lower()

    if "close" not in df.columns:
        raise ValueError("Required column 'close' not found.")

    logging.info(f"Rows Loaded : {len(df)}")
    logging.info(f"Columns : {list(df.columns)}")

    return df

def process_data(df, window):

    logging.info("Starting rolling mean calculation...")

    df["rolling_mean"] = df["close"].rolling(window=window).mean()

    logging.info("Rolling mean completed.")

    logging.info("Generating trading signals...")

    df["signal"] = (df["close"] > df["rolling_mean"]).astype(int)

    logging.info("Signal generation completed.")

    return df

def calculate_metrics(df, version, seed, latency_ms):

    metrics = {
        "version": version,
        "rows_processed": int(len(df)),
        "metric": "signal_rate",
        "value": round(float(df["signal"].mean()), 4),
        "latency_ms": int(latency_ms),
        "seed": seed,
        "status": "success"
    }

    logging.info(f"Metrics: {metrics}")

    return metrics

def save_metrics(metrics, output_file):

    with open(output_file, "w") as file:
        json.dump(metrics, file, indent=4)

    logging.info(f"Metrics saved to {output_file}")


def main():

    start_time = time.perf_counter()
    args = parse_arguments()

    setup_logging(args.log_file)

    logging.info("=" * 60)
    logging.info("Job Started")

    try:
        
        config = load_config(args.config)
        validate_config(config)

        np.random.seed(config["seed"])

        logging.info("Configuration Loaded Successfully")
        logging.info(f"Seed    : {config['seed']}")
        logging.info(f"Window  : {config['window']}")
        logging.info(f"Version : {config['version']}")

        print("\nConfiguration Loaded Successfully")
        print(config)

        
        df = load_dataset(args.input)

        print("\nDataset Loaded Successfully")
        print(df.head())
        
        df = process_data(df, config["window"])

       
        latency_ms = (time.perf_counter() - start_time) * 1000

       
        metrics = calculate_metrics(
            df=df,
            version=config["version"],
            seed=config["seed"],
            latency_ms=latency_ms
        )

        
        save_metrics(metrics, args.output)

        logging.info("Job Finished Successfully")

        print("\nMetrics:")
        print(json.dumps(metrics, indent=4))

        sys.exit(0)

    except Exception as e:

        logging.exception("Job Failed")

        version = "unknown"

        try:
            if "config" in locals():
                version = config.get("version", "unknown")
        except pd.errors.ParserError:
            pass

        error_metrics = {
            "version": version,
            "status": "error",
            "error_message": str(e)
        }

        save_metrics(error_metrics, args.output)

        print("\nError:")
        print(json.dumps(error_metrics, indent=4))

        sys.exit(1)


if __name__ == "__main__":
    main()
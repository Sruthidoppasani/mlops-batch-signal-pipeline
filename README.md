# MLOps Technical Assessment - Batch Signal Pipeline

## Overview

This project implements a minimal **MLOps-style batch processing pipeline** in Python. The application reads market data from a CSV file, loads configuration from a YAML file, computes a rolling mean on the `close` price, generates binary trading signals, logs execution details, and writes structured metrics in JSON format.

The project is fully Dockerized and can be executed locally or inside a Docker container using a single command.

---

## Features

- Configuration management using YAML
- Deterministic execution using NumPy random seed
- Input dataset validation
- Rolling mean calculation on `close` prices
- Binary signal generation
- Structured metrics generation (`metrics.json`)
- Detailed execution logging (`run.log`)
- Graceful error handling
- Docker support for reproducible execution

---

## Project Structure

```text
mlops-task/
│
├── run.py              # Main application
├── config.yaml         # Configuration file
├── data.csv            # Input dataset
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration
├── README.md           # Project documentation
├── metrics.json        # Generated metrics
└── run.log             # Execution logs
```

---

## Configuration

The application uses a YAML configuration file.

Example:

```yaml
seed: 42
window: 5
version: "v1"
```

| Parameter | Description |
|-----------|-------------|
| seed | Random seed for deterministic execution |
| window | Rolling window size |
| version | Pipeline version |

---

## Input Dataset

The input CSV should contain market data with at least the following column:

- `close`

Other OHLCV columns may also be present.

Example columns:

- timestamp
- open
- high
- low
- close
- volume_btc
- volume_usd

---

## Processing Pipeline

The application performs the following steps:

1. Parse command-line arguments
2. Load and validate configuration
3. Set NumPy random seed
4. Load and validate input dataset
5. Compute rolling mean using the configured window size
6. Generate binary trading signals

```text
Signal = 1  if close > rolling_mean
Signal = 0  otherwise
```

7. Calculate execution metrics
8. Write metrics to `metrics.json`
9. Record execution details in `run.log`

---

## Metrics Output

Example `metrics.json`

```json
{
    "version": "v1",
    "rows_processed": 10000,
    "metric": "signal_rate",
    "value": 0.4989,
    "latency_ms": 5,
    "seed": 42,
    "status": "success"
}
```

---

## Error Handling

The application handles the following scenarios gracefully:

- Missing configuration file
- Invalid configuration
- Missing input file
- Empty CSV
- Invalid CSV format
- Missing `close` column

In case of failure:

- Error is logged
- `metrics.json` is still generated
- Appropriate exit code is returned

Example:

```json
{
    "version": "v1",
    "status": "error",
    "error_message": "Required column 'close' not found."
}
```

---

## Installation

Clone the repository

```bash
git clone <repository-url>
cd mlops-task
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Local Execution

Run the application using:

```bash
python run.py --input data.csv --config config.yaml --output metrics.json --log-file run.log
```

---

## Docker

### Build Docker Image

```bash
docker build -t mlops-task .
```

### Run Docker Container

```bash
docker run --rm mlops-task
```

The container prints the generated metrics JSON to stdout.

---

## Dependencies

- Python 3.9+
- NumPy
- Pandas
- PyYAML

Install using:

```bash
pip install -r requirements.txt
```

---

## Logging

Execution logs are written to:

```
run.log
```

The log includes:

- Job start
- Configuration details
- Dataset validation
- Processing steps
- Metrics summary
- Job completion
- Exceptions and validation errors

---

## Technologies Used

- Python
- Pandas
- NumPy
- PyYAML
- Docker
- Logging
- JSON




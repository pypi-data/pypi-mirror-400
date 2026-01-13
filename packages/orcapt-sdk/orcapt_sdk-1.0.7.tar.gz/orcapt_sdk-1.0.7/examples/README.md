# Orca SDK Examples

Comprehensive examples demonstrating all Orca SDK features.

## Quick Start Examples

### 1. `basic_usage.py` - Start Here! 🚀

Basic streaming and button usage. Perfect for beginners.

```bash
python examples/basic_usage.py
```

### 2. `advanced_usage.py` - Advanced Features

Decorators, logging, usage tracking, and more.

```bash
python examples/advanced_usage.py
```

### 3. `error_handling.py` - Error Handling

Comprehensive error handling patterns and best practices.

```bash
python examples/error_handling.py
```

## Deployment Examples

### 4. `lambda_factory_usage.py` - Modern Lambda Factory ⭐

**The recommended way to build Lambda Agents.** Uses `create_hybrid_handler` for zero-config routing.

Features:
- ✅ **One-line setup** for HTTP, SQS, and Cron.
- ✅ **Automatic SQS Offloading** (just set `SQS_QUEUE_URL`).
- ✅ **Built-in FastAPI** for health checks and API access.

### 5. `simulate_factory.py` - One-Click Testing 🧪

Demonstrates how to test your hybrid handler locally using `simulate_lambda_handler`.

```bash
python examples/simulate_factory.py
```

### 6. `lambda_deployment_simple.py` - Manual Lambda Handler

Classic adapter-based approach for more granular control.

## Feature Examples

### 7. `patterns_example.py` - Design Patterns 🏗️

Builder, Context Managers, and Middleware patterns.

```bash
python examples/patterns_example.py
```

### 8. `storage_example.py` - Storage SDK 📦

Orca Storage SDK for file management.

```bash
python examples/storage_example.py
```

## Template Files

### `Dockerfile.lambda` - Lambda Dockerfile Template

Sample Dockerfile for AWS Lambda deployment. Copy to your project root.

### `requirements-lambda.txt` - Lambda Requirements Template

Sample requirements file for Lambda. Keep dependencies minimal!

## Key Concepts

### Streaming

```python
session = handler.begin(data)
session.stream("Hello, world!")
```

### Loading Indicators

```python
from orca.config import LoadingKind
session.loading.start(LoadingKind.THINKING.value)
session.stream("Processing...")
session.loading.end(LoadingKind.THINKING.value)
```

### Buttons

```python
from orca.config import ButtonColor
session.button.link("Click", "https://example.com", color=ButtonColor.PRIMARY.value)
```

### Error Handling

```python
from orca.exceptions import OrcaException
try:
    # operations
except OrcaException as e:
    logger.error(f"Error: {e.to_dict()}")
```

### Decorators

```python
from orca.decorators import retry, log_execution

@retry(max_attempts=3)
@log_execution
def process_data():
    pass
```

### Logging

```python
from orca.logging_config import setup_logging
setup_logging(level=logging.DEBUG, log_file="app.log")
```

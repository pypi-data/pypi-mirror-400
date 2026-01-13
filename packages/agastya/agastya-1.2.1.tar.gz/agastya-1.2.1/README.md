# Agastya

High-performance web scraping and MongoDB utilities for Python.

## Features

- **CustomLogger**: Fast, color-coded logging with minimal overhead
- **Record**: Lightweight MongoDB document wrapper with state management
- **fetch()**: Smart HTTP client with caching, retries, and validation
- **clean_dict()**: Comprehensive text/HTML cleaning utilities
- **run_engine()**: Adaptive concurrent task executor with auto-scaling threads

## Installation

```bash
pip install agastya
```

## Quick Start

### Basic Usage

```python
from agastya import fetch, CustomLogger, Record

# Initialize logger
logger = CustomLogger(name=__file__)

# Fetch with caching
response = fetch(
    url="https://example.com",
    save_dir="cache",
    filename="page.html",
    max_retries=3
)

# Work with MongoDB records
from pymongo import MongoClient
db = MongoClient()['mydb']
collection = db['items']

doc = collection.find_one({"_id": "123"})
record = Record(doc, collection, logger)

# Mark states
record.mark_done("scraped", meta={"items": 42})
record.mark_fail("parsed", meta={"error": "timeout"})
```

### Configuration

Create a `config.py` in your project root:

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client['your_database']
```

### Advanced Features

**Smart caching with validation:**
```python
response = fetch(
    url="https://example.com/data",
    save_dir="cache",
    filename="data.html",
    valid_rules={
        "required": ["expected text"],
        "forbidden": ["error", "404"],
        "remove": True  # delete invalid cache
    }
)
```

**Concurrent processing:**
```python
from agastya import run_engine
from pymongo import MongoClient

db = MongoClient()['mydb']
collection = db['tasks']

def worker(doc):
    # Process document
    print(f"Processing {doc['_id']}")

query = {"status": "pending"}
run_engine(collection, query, worker, THREADS_START=50)
```

## Requirements

- Python 3.8+
- requests
- lxml
- pymongo
- urllib3

## Development

```bash
# Clone repository
git clone https://github.com/yourusername/agastya.git
cd agastya

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT License - see LICENSE file for details
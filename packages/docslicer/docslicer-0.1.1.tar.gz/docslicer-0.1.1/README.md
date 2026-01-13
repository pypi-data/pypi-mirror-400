# DocSlicer SDK

Python SDK for the DocSlicer document processing API.

## Installation

```bash
pip install docslicer
```

## Quick Start

```python
from docslicer import run

# Process a URL
chunks = run("https://sec.gov/filing.html", api_key="sk_live_...")

# Process a local file
chunks = run("./document.html", api_key="sk_live_...")

# Process all HTML files in a directory
chunks = run("./docs/", api_key="sk_live_...")

# Process multiple files
chunks = run(["file1.html", "file2.html"], api_key="sk_live_...")

# Process URLs from a CSV
chunks = run("./urls.csv", api_key="sk_live_...")
```

## Options

```python
chunks = run(
    "./docs/",
    api_url="https://www.docslicer.ai/api/v1/run",  # Custom API URL
    api_key="sk_live_...",                           # API key for auth
    format="json",                                   # Output format: json, csv, jsonl, parquet
    timeout=300,                                     # Request timeout
)
```

## Output Formats

```python
# JSON (default) - list of dictionaries
chunks = run("./doc.html", api_key="sk_live_...", format="json")

# CSV - string with header row  
csv_data = run("./doc.html", api_key="sk_live_...", format="csv")

# JSON Lines - one JSON object per line
jsonl_data = run("./doc.html", api_key="sk_live_...", format="jsonl")

# Parquet - binary bytes
parquet_bytes = run("./doc.html", api_key="sk_live_...", format="parquet")
```

## Async Support

```python
from docslicer import run_async

chunks = await run_async("./docs/", api_key="sk_live_...")
```

## Client Class

For multiple calls, use the client class to reuse configuration:

```python
from docslicer import DocSlicerClient

client = DocSlicerClient(
    api_url="https://www.docslicer.ai/api/v1/run",
    api_key="sk_live_...",
)

chunks1 = client.run("./doc1.html")
chunks2 = client.run("./doc2.html")
```

## Environment Variables

You can set the API URL via environment variable:

```bash
export DOCSLICER_API_URL="https://www.docslicer.ai/api/v1/run"
```

## Get an API Key

Sign up at [docslicer.ai](https://www.docslicer.ai) to get your API key.

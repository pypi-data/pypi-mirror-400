# DocSlicer SDK
"""
Python SDK for the DocSlicer document processing service.

DocSlicer transforms HTML documents into structured chunks optimized for 
RAG (Retrieval Augmented Generation) applications.

Basic Usage:
    >>> from docslicer import run
    >>> 
    >>> # Process a URL
    >>> chunks = run("https://sec.gov/cgi-bin/browse-edgar?...")
    >>> 
    >>> # Process a local file
    >>> chunks = run("./10k.html")
    >>> 
    >>> # Process all HTML files in a directory
    >>> chunks = run("./docs/")
    >>> 
    >>> # Process multiple specific files
    >>> chunks = run(["a.html", "b.html"])
    >>> 
    >>> # Process URLs from a CSV file
    >>> chunks = run("./urls.csv", url_column="url")

Output Formats:
    >>> # JSON (default) - list of dictionaries
    >>> chunks = run("./doc.html", format="json")
    >>> 
    >>> # CSV - string with header row
    >>> csv_data = run("./doc.html", format="csv")
    >>> 
    >>> # JSON Lines - one JSON object per line
    >>> jsonl_data = run("./doc.html", format="jsonl")
    >>> 
    >>> # Parquet - binary bytes
    >>> parquet_bytes = run("./doc.html", format="parquet")

Async Usage:
    >>> import asyncio
    >>> from docslicer import run_async
    >>> 
    >>> async def main():
    ...     chunks = await run_async("./doc.html")
    ...     print(f"Got {len(chunks)} chunks")
    >>> 
    >>> asyncio.run(main())

Configuration:
    >>> from docslicer import DocSlicerClient
    >>> 
    >>> client = DocSlicerClient(
    ...     api_url="https://www.docslicer.ai/api/v1/run",
    ...     api_key="your-api-key",
    ...     timeout=600,
    ... )
    >>> chunks = client.run("./doc.html")
"""
from .client import run, run_async, DocSlicerClient, OutputFormat

__version__ = "0.1.0"
__all__ = ["run", "run_async", "DocSlicerClient", "OutputFormat"]

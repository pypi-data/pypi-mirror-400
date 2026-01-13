# docslicer/client.py - SDK client for the DocSlicer API
"""
Python SDK for the DocSlicer document processing service.

The SDK provides a simple interface to process documents (URLs, HTML files, 
directories) and get back structured chunks ready for RAG applications.

Example:
    >>> from docslicer import run
    >>> chunks = run("https://sec.gov/doc.html", api_key="sk_live_...")
    >>> chunks = run("./10k.html", api_key="sk_live_...")
    >>> chunks = run("./docs/", api_key="sk_live_...")  # Process all HTML files
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Union, Optional, Literal
import httpx

# Live API URL - can be overridden via DOCSLICER_API_URL env var
LIVE_API_URL = "https://www.docslicer.ai/api/v1/run"
DEFAULT_API_URL = os.environ.get("DOCSLICER_API_URL", LIVE_API_URL)

# Supported output formats
OutputFormat = Literal["json", "csv", "jsonl", "parquet"]


class DocSlicerClient:
    """
    Client for the DocSlicer API.
    
    Args:
        api_url: API endpoint URL (default: https://www.docslicer.ai/api/v1/run)
        api_key: Optional API key for authentication
        timeout: Request timeout in seconds (default: 300)
    
    Example:
        >>> client = DocSlicerClient(api_key="your-key")
        >>> chunks = client.run("./document.html")
    """
    
    def __init__(
        self,
        api_url: str = DEFAULT_API_URL,
        api_key: Optional[str] = None,
        timeout: int = 300,
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout
    
    def run(
        self,
        input: Union[str, List[str], Path],
        format: OutputFormat = "json",
        url_column: str = "url",
    ) -> Union[List[Dict[str, Any]], bytes, str]:
        """
        Process documents and return chunks.
        
        Args:
            input: URL, file path, directory path, or list of paths
            format: Output format - "json" (default), "csv", "jsonl", or "parquet"
            url_column: Column name for URLs when processing CSV files
        
        Returns:
            - format="json": List of chunk dictionaries
            - format="csv": CSV string
            - format="jsonl": JSON Lines string
            - format="parquet": Parquet bytes
        """
        input_type, payload = _detect_and_prepare(input)
        # API key format: sk_live_... (sent directly, not as Bearer token)
        headers = {"Authorization": self.api_key} if self.api_key else {}
        
        with httpx.Client(timeout=self.timeout) as client:
            response = _make_request(client, self.api_url, input_type, payload, format, url_column, headers)
            response.raise_for_status()
            return _parse_response(response, format)


def run(
    input: Union[str, List[str], Path],
    *,
    api_url: str = DEFAULT_API_URL,
    api_key: Optional[str] = None,
    format: OutputFormat = "json",
    url_column: str = "url",
    timeout: int = 300,
) -> Union[List[Dict[str, Any]], bytes, str]:
    """
    Process documents and return chunks.
    
    This is the main entry point for the DocSlicer SDK. It automatically detects
    the input type (URL, file, directory, or list of files) and processes accordingly.
    
    Args:
        input: What to process:
            - URL string (https://...)
            - File path ("./doc.html")
            - Directory path ("./docs/") - processes all .html/.htm files
            - List of file paths (["a.html", "b.html"])
            - CSV file path ("./urls.csv") - processes URLs from specified column
        api_url: API endpoint URL (default: https://www.docslicer.ai/api/v1/run)
        api_key: Optional API key for authentication
        format: Output format:
            - "json" (default): List of chunk dictionaries
            - "csv": CSV string
            - "jsonl": JSON Lines string  
            - "parquet": Parquet bytes
        url_column: Column name for URLs when processing CSV files
        timeout: Request timeout in seconds (default: 300)
    
    Returns:
        Chunks in the requested format:
        - format="json": List[Dict] - List of chunk objects
        - format="csv": str - CSV with header row
        - format="jsonl": str - One JSON object per line
        - format="parquet": bytes - Apache Parquet binary
    
    Examples:
        >>> # Process a URL
        >>> chunks = run("https://sec.gov/Archives/edgar/.../10k.htm")
        >>> len(chunks)
        150
        
        >>> # Process a local file
        >>> chunks = run("./document.html")
        
        >>> # Process all HTML files in a directory
        >>> chunks = run("./docs/")
        
        >>> # Process multiple specific files
        >>> chunks = run(["10k.html", "10q.html"])
        
        >>> # Get CSV output
        >>> csv_data = run("./doc.html", format="csv")
        >>> with open("chunks.csv", "w") as f:
        ...     f.write(csv_data)
        
        >>> # Get Parquet output (for data processing)
        >>> parquet_bytes = run("./doc.html", format="parquet")
        >>> with open("chunks.parquet", "wb") as f:
        ...     f.write(parquet_bytes)
    """
    client = DocSlicerClient(api_url=api_url, api_key=api_key, timeout=timeout)
    return client.run(input, format=format, url_column=url_column)


async def run_async(
    input: Union[str, List[str], Path],
    *,
    api_url: str = DEFAULT_API_URL,
    api_key: Optional[str] = None,
    format: OutputFormat = "json",
    url_column: str = "url",
    timeout: int = 300,
) -> Union[List[Dict[str, Any]], bytes, str]:
    """
    Async version of run().
    
    Same arguments and return values as run(), but can be awaited
    in async code.
    
    Example:
        >>> async def process():
        ...     chunks = await run_async("./doc.html")
        ...     return chunks
    """
    input_type, payload = _detect_and_prepare(input)
    # API key format: sk_live_... (sent directly, not as Bearer token)
    headers = {"Authorization": api_key} if api_key else {}
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await _make_request_async(client, api_url, input_type, payload, format, url_column, headers)
        response.raise_for_status()
        return _parse_response(response, format)


# =============================================================================
# Internal helpers
# =============================================================================

def _detect_and_prepare(input: Union[str, List[str], Path]) -> tuple:
    """Detect input type and prepare payload."""
    
    # List of paths → multiple files
    if isinstance(input, list):
        files = [_read_file(p) for p in input]
        return ("files", files)
    
    input_str = str(input)
    
    # URL
    if input_str.startswith(("http://", "https://")):
        return ("url", input_str)
    
    # Path
    path = Path(input_str)
    
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {input_str}")
    
    # Directory → multiple files
    if path.is_dir():
        html_files = list(path.glob("*.html")) + list(path.glob("*.htm"))
        if not html_files:
            raise ValueError(f"No HTML files found in: {input_str}")
        files = [_read_file(f) for f in sorted(html_files)]
        return ("files", files)
    
    # CSV file
    if path.suffix.lower() == ".csv":
        return ("csv", _read_file(path))
    
    # Single file
    return ("file", _read_file(path))


def _read_file(path: Union[str, Path]) -> tuple:
    """Read file and return (filename, content, content_type) tuple."""
    path = Path(path)
    content = path.read_bytes()
    content_type = {
        ".html": "text/html",
        ".htm": "text/html",
        ".csv": "text/csv",
    }.get(path.suffix.lower(), "application/octet-stream")
    return (path.name, content, content_type)


def _make_request(client, api_url, input_type, payload, format, url_column, headers):
    """Make sync HTTP request."""
    params = {"format": format}
    
    if input_type == "url":
        return client.post(api_url, params=params, json={"url": payload}, headers=headers)
    elif input_type == "file":
        return client.post(api_url, params=params, files={"file": payload}, headers=headers)
    elif input_type == "files":
        return client.post(api_url, params=params, files=[("files", f) for f in payload], headers=headers)
    elif input_type == "csv":
        params["url_column"] = url_column
        return client.post(api_url, params=params, files={"csv": payload}, headers=headers)
    else:
        raise ValueError(f"Unknown input type: {input_type}")


async def _make_request_async(client, api_url, input_type, payload, format, url_column, headers):
    """Make async HTTP request."""
    params = {"format": format}
    
    if input_type == "url":
        return await client.post(api_url, params=params, json={"url": payload}, headers=headers)
    elif input_type == "file":
        return await client.post(api_url, params=params, files={"file": payload}, headers=headers)
    elif input_type == "files":
        return await client.post(api_url, params=params, files=[("files", f) for f in payload], headers=headers)
    elif input_type == "csv":
        params["url_column"] = url_column
        return await client.post(api_url, params=params, files={"csv": payload}, headers=headers)
    else:
        raise ValueError(f"Unknown input type: {input_type}")


def _parse_response(response: httpx.Response, format: OutputFormat):
    """Parse response based on format."""
    if format == "json":
        return response.json()
    elif format == "parquet":
        return response.content  # Binary bytes
    else:  # csv, jsonl
        return response.text  # String content

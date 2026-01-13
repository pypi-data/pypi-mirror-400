# lei-google-scholar

A Python package for searching Google Scholar with MCP server support.

## Installation

```bash
pip install lei-google-scholar
```

## Usage

### As a Python library

```python
from lei_google_scholar import google_scholar_search, advanced_google_scholar_search

# Simple keyword search
results = google_scholar_search("machine learning", num_results=5)
for r in results:
    print(r['Title'], r.get('Citations', 0))

# Advanced search with filters
results = advanced_google_scholar_search(
    "deep learning",
    author="Yann LeCun",
    year_range=(2010, 2024),
    num_results=10
)
```

### As an MCP server

```bash
# Run the MCP server
lei-google-scholar-server
```

## Features

- Search Google Scholar by keywords
- Advanced search with author and year range filters
- Get author information
- MCP server integration for AI assistants

## Requirements

- Python 3.10+
- scholarly library
- MCP library

## License

MIT

from typing import Any, List, Dict, Optional
import asyncio
import logging
from mcp.server.fastmcp import FastMCP
from lei_google_scholar.core import google_scholar_search, advanced_google_scholar_search
from scholarly import scholarly

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

mcp = FastMCP("lei_google_scholar")


@mcp.tool()
async def search_google_scholar_key_words(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search for articles on Google Scholar using keywords.

    Args:
        query: Search query string
        num_results: Number of results to return (default: 5)

    Returns:
        List of dictionaries containing article information
    """
    logging.info(f"Searching Google Scholar for: {query}, num_results: {num_results}")
    try:
        results = await asyncio.to_thread(google_scholar_search, query, num_results)
        return results
    except Exception as e:
        return [{"error": f"An error occurred: {str(e)}"}]


@mcp.tool()
async def search_google_scholar_advanced(
    query: str,
    author: Optional[str] = None,
    year_range: Optional[list] = None,
    num_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for articles on Google Scholar using advanced filters.

    Args:
        query: General search query
        author: Author name filter
        year_range: List containing [start_year, end_year]
        num_results: Number of results to return (default: 5)

    Returns:
        List of dictionaries containing article information
    """
    logging.info(f"Advanced search with: {locals()}")
    try:
        results = await asyncio.to_thread(
            advanced_google_scholar_search,
            query, author, tuple(year_range) if year_range else None, num_results
        )
        return results
    except Exception as e:
        return [{"error": f"An error occurred: {str(e)}"}]


@mcp.tool()
async def get_author_info(author_name: str) -> Dict[str, Any]:
    """
    Get detailed information about an author from Google Scholar.

    Args:
        author_name: Name of the author to search for

    Returns:
        Dictionary containing author information
    """
    logging.info(f"Retrieving author info for: {author_name}")
    try:
        def _search():
            search_query = scholarly.search_author(author_name)
            try:
                author = next(search_query)
            except StopIteration:
                return None
            return scholarly.fill(author)

        filled_author = await asyncio.to_thread(_search)

        if filled_author is None:
            return {"error": f"Author '{author_name}' not found"}

        return {
            "name": filled_author.get("name", "N/A"),
            "affiliation": filled_author.get("affiliation", "N/A"),
            "interests": filled_author.get("interests", []),
            "citedby": filled_author.get("citedby", 0),
            "publications": [
                {
                    "title": pub.get("bib", {}).get("title", "N/A"),
                    "year": pub.get("bib", {}).get("pub_year", "N/A"),
                    "citations": pub.get("num_citations", 0)
                }
                for pub in filled_author.get("publications", [])[:5]
            ]
        }
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}


if __name__ == "__main__":
    mcp.run(transport="stdio")

from scholarly import scholarly
import time


def google_scholar_search(query, num_results=5):
    """
    Search Google Scholar using a simple keyword query.

    Parameters:
    query (str): The search query (e.g., paper title or author).
    num_results (int): The number of results to retrieve.

    Returns:
    list: A list of dictionaries containing search results.
    """
    try:
        search_results = scholarly.search_pubs(query)

        results = []
        count = 0

        for pub in search_results:
            if count >= num_results:
                break

            bib = pub.get('bib', {})
            result_data = {
                'Title': bib.get('title', 'No title available'),
                'Authors': bib.get('author', 'No authors available'),
                'Abstract': bib.get('abstract', 'No abstract available'),
                'URL': pub.get('url', 'No link available'),
                'Year': bib.get('pub_year', 'N/A'),
                'Citations': pub.get('num_citations', 0)
            }
            results.append(result_data)
            count += 1
            time.sleep(0.5)

        return results

    except Exception as e:
        print(f"Error during search: {e}")
        return []


def advanced_google_scholar_search(query, author=None, year_range=None, num_results=5):
    """
    Search Google Scholar using advanced search filters.

    Parameters:
    query (str): The search query.
    author (str): Author name filter.
    year_range (tuple): (start_year, end_year) filter.
    num_results (int): Number of results to retrieve.

    Returns:
    list: A list of dictionaries containing search results.
    """
    try:
        search_query = query
        if author:
            search_query += f" author:{author}"

        search_results = scholarly.search_pubs(search_query)

        results = []
        count = 0

        for pub in search_results:
            if count >= num_results:
                break

            bib = pub.get('bib', {})
            pub_year = bib.get('pub_year')

            if year_range and pub_year:
                start_year, end_year = year_range
                try:
                    year = int(pub_year)
                    if not (start_year <= year <= end_year):
                        continue
                except (ValueError, TypeError):
                    pass

            result_data = {
                'Title': bib.get('title', 'No title available'),
                'Authors': bib.get('author', 'No authors available'),
                'Abstract': bib.get('abstract', 'No abstract available'),
                'URL': pub.get('url', 'No link available'),
                'Year': pub_year or 'N/A',
                'Citations': pub.get('num_citations', 0)
            }
            results.append(result_data)
            count += 1
            time.sleep(0.5)

        return results

    except Exception as e:
        print(f"Error during advanced search: {e}")
        return []


def get_author_info(author_name):
    """
    Get detailed information about an author from Google Scholar.

    Parameters:
    author_name (str): Name of the author to search for.

    Returns:
    dict: Dictionary containing author information.
    """
    try:
        search_query = scholarly.search_author(author_name)
        try:
            author = next(search_query)
        except StopIteration:
            return None
        filled_author = scholarly.fill(author)
        return filled_author
    except Exception as e:
        print(f"Error getting author info: {e}")
        return None

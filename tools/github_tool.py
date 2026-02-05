import requests
from typing import List, Dict, Any
import time


def search_repos(query: str, limit: int = 3, retries: int = 3) -> List[Dict[str, Any]]:
    """Search GitHub repositories by query. Uses exponential backoff on failure."""
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&per_page={limit}"
    
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            res = response.json()

            repos = []
            for repo in res.get("items", [])[:limit]:
                repos.append({
                    "name": repo.get("name", "Unknown"),
                    "stars": repo.get("stargazers_count", 0),
                    "url": repo.get("html_url", ""),
                    "description": repo.get("description") or "No description"
                })

            return repos
            
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            return [{"error": f"Failed to fetch GitHub repositories: {str(e)}"}]
        except Exception as e:
            return [{"error": f"Unexpected error: {str(e)}"}]
    
    return [{"error": "Failed to fetch GitHub repositories after retries"}]

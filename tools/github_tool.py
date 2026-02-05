import requests


def search_repos(query, limit=3):

    url = f"https://api.github.com/search/repositories?q={query}&sort=stars"
    res = requests.get(url).json()

    repos = []

    for repo in res.get("items", [])[:limit]:
        repos.append({
            "name": repo["name"],
            "stars": repo["stargazers_count"],
            "url": repo["html_url"],
            "description": repo["description"]
        })

    return repos

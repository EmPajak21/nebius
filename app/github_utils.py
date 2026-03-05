import os
import requests

GITHUB_API = "https://api.github.com/repos"


def _github_headers():
    token = os.getenv("GITHUB_TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def parse_repo_url(url: str):
    if "github.com" not in url:
        raise ValueError("URL must point to a GitHub repository (github.com)")

    parts = url.rstrip("/").split("/")

    if len(parts) < 5:
        raise ValueError("Invalid GitHub repository URL — expected https://github.com/owner/repo")

    # Use fixed indices so URLs with extra path segments (e.g. /tree/main) still parse correctly
    owner = parts[3]
    repo = parts[4]

    return owner, repo


def fetch_repo_tree(url: str):

    owner, repo = parse_repo_url(url)

    api_url = f"{GITHUB_API}/{owner}/{repo}/git/trees/HEAD?recursive=1"

    response = requests.get(api_url, headers=_github_headers())

    if response.status_code == 404:
        raise FileNotFoundError(
            f"Repository '{owner}/{repo}' not found — check the URL or ensure the repo is public"
        )

    if response.status_code == 403:
        raise PermissionError(f"Access denied for '{owner}/{repo}' — the repository may be private")

    if response.status_code != 200:
        raise Exception(f"GitHub API error {response.status_code} fetching repository tree")

    data = response.json()

    return data["tree"], owner, repo


def fetch_file_content(owner, repo, path):

    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/{path}"

    response = requests.get(raw_url, headers=_github_headers())

    if response.status_code != 200:
        return None

    return response.text

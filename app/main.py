from fastapi import FastAPI, HTTPException

from app.models import RepoRequest, RepoResponse
from app.github_utils import fetch_repo_tree, fetch_file_content
from app.repo_processor import select_files, truncate_content, build_repo_tree, MAX_CHARS_PER_FILE, MAX_TOTAL_CHARS
from app.summarizer import summarize_repo


app = FastAPI(title="GitHub Repository Summarizer")


@app.post("/summarize", response_model=RepoResponse)
async def summarize_repo_endpoint(request: RepoRequest):

    try:
        tree, owner, repo = fetch_repo_tree(request.github_url)

    except ValueError as e:
        raise HTTPException(status_code=422, detail={"status": "error", "message": str(e)})
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail={"status": "error", "message": str(e)})
    except PermissionError as e:
        raise HTTPException(status_code=403, detail={"status": "error", "message": str(e)})

    try:
        selected_files = select_files(tree)

        if not selected_files:
            raise HTTPException(status_code=422, detail={"status": "error", "message": "Repository appears to be empty or contains no readable files"})

        repo_tree = build_repo_tree(tree)

        file_contents = {}
        total_chars = 0

        for path in selected_files:
            if total_chars >= MAX_TOTAL_CHARS:
                break

            content = fetch_file_content(owner, repo, path)

            if content:
                remaining = MAX_TOTAL_CHARS - total_chars
                truncated = truncate_content(content, min(MAX_CHARS_PER_FILE, remaining))
                file_contents[path] = truncated
                total_chars += len(truncated)

        result = summarize_repo(repo_tree, file_contents)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"status": "error", "message": str(e)})

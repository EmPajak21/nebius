import json

from app.llm_client import call_llm


def build_prompt(repo_tree: str, files: dict) -> str:
    file_context = ""
    for path, content in files.items():
        file_context += f"\n--- FILE: {path} ---\n{content}\n"

    return f"""Analyse the GitHub repository below and return a JSON summary.

=== REPOSITORY FILE TREE ===
{repo_tree}

=== KEY FILE CONTENTS (some files may be truncated) ===
{file_context}

Return a JSON object with exactly these fields:
- "summary": a clear paragraph describing what the project does and its purpose
- "technologies": a list of the main languages, frameworks, libraries, and tools used
- "structure": a brief description of how the project is organised (key directories and their roles)

Return only the JSON object."""


def summarize_repo(repo_tree: str, files: dict) -> dict:
    prompt = build_prompt(repo_tree, files)
    response = call_llm(prompt)

    # Strip markdown fences in case response_format is not honoured
    text = response.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # drop opening fence line (e.g. ```json) and closing fence
        text = "\n".join(line for line in lines if not line.strip().startswith("```"))

    return json.loads(text)

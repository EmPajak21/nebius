# GitHub Repository Summarizer

A FastAPI service that takes a GitHub repository URL and returns a structured summary — including a description, technology stack, and project structure — powered by an LLM.

## Setup

**1. Clone the repository**

```bash
git clone <repo-url>
cd nebius
```

**2. Install dependencies**

```bash
pip install .
```

**3. Set your API key**

```bash
export NEBIUS_API_KEY=your_key
```

Optionally, set a GitHub token to avoid rate limits (60 unauthenticated requests/hour):

```bash
export GITHUB_TOKEN=your_github_token
```

**4. Start the server**

```bash
uvicorn app.main:app --reload
```

The server will run at `http://localhost:8000`.

## Example Usage

```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"github_url":"https://github.com/EmPajak21/CarAT"}'
```

**Response:**

```json
{
  "summary": "CarAT (Carbon Atom Tracker) is a Python tool designed to automate the tracking of biogenic carbon content (BCC) across complex industrial chemical value chains. It addresses the Together for Sustainability (TfS) consortium's mandate for BCC reporting by 2026, serving as both a compliance tool and a decision support system for decarbonisation strategies. The methodology involves three stages: processing ERP-derived value chain data, utilizing RXNMapper for atom-level tracking through chemical reactions, and applying linear programming optimization to calculate carbon distribution throughout the entire value chain network.",
  "technologies": [
    "Python 3.10+",
    "RDKit",
    "RXNMapper",
    "Python-MIP",
    "CBC solver",
    "Pandas",
    "NumPy",
    "NetworkX",
    "Plotly",
    "Matplotlib",
    "pytest",
    "Ruff",
    "uv",
    "Hatchling",
    "GitHub Actions"
  ],
  "structure": "The project follows a src-layout Python package structure. The `src/carat/` directory contains the main package with three key subpackages: `core/` (linear programming optimization and bill-of-atoms calculation), `processing/` (data preprocessing and configuration datatypes), and `vis/` (Sankey diagrams and Mermaid graph visualization). Additional modules include `chem_utils.py` for chemical structure handling and `utils.py` for data serialization. Tests are located in `tests/`, CI/CD workflows in `.github/workflows/`, and configuration is managed via `pyproject.toml`."
}
```

## Error Responses

All errors return JSON in the form `{"status": "error", "message": "..."}` with an appropriate HTTP status code:

| Status | Cause |
|--------|-------|
| 422 | Invalid or non-GitHub URL, or repository contains no readable files |
| 404 | Repository not found or does not exist |
| 403 | Repository is private or access is denied |
| 500 | LLM API failure or unexpected server error |

## Model

`moonshotai/Kimi-K2.5` via [Nebius Token Factory](https://tokenfactory.nebius.com) — a strong model for code understanding tasks.

## Repository Processing Strategy

Repositories can be very large, so the service performs lightweight signal extraction before sending anything to the LLM:

- **Binary and noise filtering** — binary files (images, fonts, archives, compiled objects), lock files, and dependency directories (`node_modules/`, `vendor/`, `.venv/`, etc.) are excluded entirely
- **File scoring** — remaining files are ranked by informational value: `README` (+100), dependency manifests (`pyproject.toml`, `requirements.txt`, `package.json`, `Cargo.toml`, etc., +80), `Dockerfile` (+60), entrypoints (`main`, `app`, `index`, `server`, +50), CI/config YAML (+35), source files (+30)
- **Selection** — the top 20 scoring files are chosen
- **Per-file truncation** — each file is capped at 3 000 characters
- **Total context budget** — all file contents combined are capped at 40 000 characters to stay well within the LLM's context window
- **Full directory tree** — the complete repo file tree (up to 200 paths) is included separately so the model understands the overall project layout even for files not included in full

This lets the model understand a repository without ingesting the full codebase.

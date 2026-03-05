MAX_FILES = 20
MAX_CHARS_PER_FILE = 3000
MAX_TOTAL_CHARS = 40000

BINARY_EXTENSIONS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".ico",
    ".svg",
    ".webp",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".xz",
    ".7z",
    ".rar",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".whl",
    ".pyc",
    ".pyo",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".otf",
    ".mp3",
    ".mp4",
    ".wav",
    ".ogg",
    ".avi",
    ".mov",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".bin",
    ".dat",
    ".pkl",
    ".npy",
    ".npz",
)

SKIP_DIRS = (
    "node_modules/",
    "vendor/",
    ".venv/",
    "venv/",
    "__pycache__/",
    "dist/",
    "build/",
    ".git/",
)

LOCK_FILES = (".lock", "-lock.json", ".sum")

DEP_FILES = (
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "package.json",
    "cargo.toml",
    "go.mod",
    "gemfile",
    "pom.xml",
    "build.gradle",
    "composer.json",
)


def score_file(path: str) -> int:
    p = path.lower()
    score = 0

    if "readme" in p:
        score += 100

    if any(p.endswith(dep) or p == dep for dep in DEP_FILES):
        score += 80

    if "dockerfile" in p:
        score += 60

    if "main" in p or "app" in p or "index" in p or "server" in p:
        score += 50

    if p.endswith((".yml", ".yaml")):
        score += 35

    if p.endswith((".py", ".js", ".ts", ".go", ".rs", ".java", ".rb", ".cpp", ".c", ".cs")):
        score += 30

    if p.endswith((".toml", ".cfg", ".ini", ".env.example")):
        score += 15

    if p.endswith(".json") and "package.json" not in p:
        score += 10

    if "test" in p or "spec" in p:
        score -= 20

    return score


def is_skipped(path: str) -> bool:
    p = path.lower()
    if p.endswith(BINARY_EXTENSIONS):
        return True
    if any(skip in p for skip in SKIP_DIRS):
        return True
    if any(p.endswith(lock) for lock in LOCK_FILES):
        return True
    return False


def select_files(tree) -> list[str]:
    candidates = []

    for item in tree:
        path = item["path"]

        if item["type"] != "blob":
            continue

        if is_skipped(path):
            continue

        score = score_file(path)

        if score > 0:
            candidates.append((score, path))

    candidates.sort(reverse=True)

    return [path for _, path in candidates[:MAX_FILES]]


def truncate_content(content: str, limit: int = MAX_CHARS_PER_FILE) -> str:
    if len(content) <= limit:
        return content
    return content[:limit] + f"\n... [truncated at {limit} chars]"


def build_repo_tree(tree_items, max_paths: int = 200) -> str:
    """Build a full directory listing from the repo tree for structural context."""
    paths = sorted(
        item["path"]
        for item in tree_items
        if item["type"] == "blob" and not is_skipped(item["path"])
    )
    if len(paths) > max_paths:
        paths = paths[:max_paths] + [f"... ({len(paths) - max_paths} more files)"]
    return "\n".join(paths)

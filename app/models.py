from pydantic import BaseModel
from typing import List


class RepoRequest(BaseModel):
    github_url: str


class RepoResponse(BaseModel):
    summary: str
    technologies: List[str]
    structure: str

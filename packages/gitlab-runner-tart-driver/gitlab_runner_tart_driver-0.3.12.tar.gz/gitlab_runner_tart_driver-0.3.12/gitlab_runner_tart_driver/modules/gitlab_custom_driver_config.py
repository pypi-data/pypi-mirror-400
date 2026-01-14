import pathlib
from typing import Optional

from pydantic import BaseModel


class GitLabCustomDriver(BaseModel):
    name: str
    version: str


class GitLabCustomDriverConfig(BaseModel):
    builds_dir: Optional[pathlib.Path] = None
    cache_dir: Optional[pathlib.Path] = None
    builds_dir_is_shared: Optional[bool] = None
    hostname: Optional[str] = None
    driver: Optional[GitLabCustomDriver] = None
    job_env: Optional[dict] = None

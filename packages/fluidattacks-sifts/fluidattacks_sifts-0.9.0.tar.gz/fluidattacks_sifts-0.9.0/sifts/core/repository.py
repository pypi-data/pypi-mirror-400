import asyncio
import logging
import os
import tempfile
from functools import lru_cache
from pathlib import Path

from git import GitError, Repo
from platformdirs import user_data_dir

LOGGER = logging.getLogger(__name__)

DEFAULT_REPOSITORY_URI = "https://unknown.invalid/repository"


def get_base_dir() -> Path:
    """
    Get the base directory for sifts data.

    In AWS Batch, use a temporary directory to avoid issues with user_data_dir.
    Otherwise, use the standard user data directory.
    """
    if os.getenv("AWS_BATCH_JOB_ID"):
        # Running in AWS Batch, use a temporary directory
        temp_dir = tempfile.mkdtemp(prefix="sifts_")
        return Path(temp_dir)

    # Running locally, use user data directory
    return Path(user_data_dir(appname="sifts", appauthor="fluidattacks", ensure_exists=True))


async def pull_repositories(group_name: str, nickname: str) -> Path:
    """Pull repositories using melts command."""
    base_dir = get_base_dir()
    Path(base_dir, "groups").mkdir(parents=True, exist_ok=True)
    process = await asyncio.create_subprocess_exec(
        "melts",
        "pull-repos",
        "--group",
        group_name,
        "--root",
        nickname,
        cwd=base_dir,
    )
    await process.wait()
    if process.returncode != 0:
        msg = f"Failed to pull repositories for group {group_name} and nickname {nickname}"
        LOGGER.error(msg)
        raise RuntimeError(msg)

    working_dir = Path(base_dir, "groups", group_name, nickname)

    if not working_dir.exists() or not any(working_dir.iterdir()):
        msg = f"Working directory not found for group {group_name} and nickname {nickname}"
        raise RuntimeError(msg)

    return working_dir


def get_repo_remote(path: str | Path) -> str:
    try:
        repo: Repo = Repo(search_parent_directories=True, path=path)
        remotes = repo.remotes
        if remotes:
            url = remotes[0].url
            if url and not url.startswith("http"):
                url = f"ssh://{url}"
            if url:
                return url

    except GitError:
        LOGGER.exception("Computing active branch")
        return DEFAULT_REPOSITORY_URI

    return DEFAULT_REPOSITORY_URI


@lru_cache(maxsize=128)
def _get_repo_head_hash_cached(path_str: str) -> str | None:
    try:
        repo: Repo = Repo(search_parent_directories=True, path=path_str)
        head_hash: str = repo.head.commit.hexsha
    except (GitError, ValueError, BrokenPipeError):
        LOGGER.exception("Unable to find commit HEAD on analyzed directory")
        return None
    return head_hash


def get_repo_head_hash(path: str | Path) -> str | None:
    """
    Return the HEAD commit hash for the repo containing *path*.

    Results are cached in-memory to avoid hitting Git repeatedly for the same
    repository during the lifetime of the process.
    """
    path_str: str = str(Path(path).resolve())
    return _get_repo_head_hash_cached(path_str)


def get_repo_branch(path: str | Path) -> str | None:
    try:
        repo: Repo = Repo(search_parent_directories=True, path=path)
    except GitError:
        LOGGER.exception("Computing active branch")
    except IndexError:
        return None
    else:
        return repo.active_branch.name

    return None

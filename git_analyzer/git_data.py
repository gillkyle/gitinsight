"""Git data management for GitInsight."""

import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import git


@dataclass
class CommitInfo:
    """Information about a single commit."""

    hash: str
    author: str
    date: datetime
    message: str


class GitDataManager:
    """Manages git repository data and caching."""

    def __init__(self, repo_path: str):
        self.repo_path = os.path.abspath(repo_path)
        self.repo: Optional[git.Repo] = None
        self._commit_time_cache: Dict[int, int] = {}
        self._author_commits_cache: Dict[str, int] = {}
        self._recent_commits_cache: List[CommitInfo] = []

    def connect(self) -> None:
        """Connect to the git repository."""
        print(f"Connecting to repository at: {self.repo_path}")

        if not os.path.exists(self.repo_path):
            raise ValueError(f"Repository path does not exist: {self.repo_path}")

        git_dir = os.path.join(self.repo_path, ".git")
        if not os.path.exists(git_dir):
            raise ValueError(
                f"Not a git repository (no .git directory found): {self.repo_path}"
            )

        try:
            self.repo = git.Repo(self.repo_path, search_parent_directories=True)
            # Test the connection by trying to access basic repo info
            branch = self.repo.active_branch
            print(f"Connected successfully. Active branch: {branch.name}")
        except git.InvalidGitRepositoryError as e:
            raise ValueError(f"Invalid git repository: {self.repo_path}") from e
        except git.NoSuchPathError as e:
            raise ValueError(f"Repository path not found: {self.repo_path}") from e
        except Exception as e:
            raise ValueError(f"Error connecting to repository: {str(e)}") from e

    def _ensure_connected(self) -> None:
        """Ensure we're connected to a repository."""
        if self.repo is None:
            print("No repository connection, connecting now...")
            self.connect()
        # Verify the connection is still valid
        try:
            _ = self.repo.active_branch  # type: ignore
        except (git.InvalidGitRepositoryError, AttributeError):
            print("Repository connection lost, reconnecting...")
            self.repo = None
            self.connect()

    def get_commits_by_hour(self) -> Dict[int, int]:
        """Get commit counts by hour of day."""
        print("Getting commits by hour...")
        self._ensure_connected()
        if not self._commit_time_cache:
            commit_times = defaultdict(int)
            try:
                commit_count = 0
                for commit in self.repo.iter_commits():  # type: ignore
                    hour = commit.authored_datetime.hour
                    commit_times[hour] += 1
                    commit_count += 1
                print(f"Processed {commit_count} commits")
                self._commit_time_cache = dict(commit_times)
            except Exception as e:
                print(f"Error while getting commits by hour: {e}")
                raise ValueError(f"Error fetching commit times: {str(e)}") from e
        return self._commit_time_cache

    def get_commits_by_author(self) -> Dict[str, int]:
        """Get commit counts by author."""
        print("Getting commits by author...")
        self._ensure_connected()
        if not self._author_commits_cache:
            author_commits = defaultdict(int)
            try:
                commit_count = 0
                for commit in self.repo.iter_commits():  # type: ignore
                    author_name = commit.author.name
                    if author_name:
                        author_commits[author_name] += 1
                        commit_count += 1
                print(f"Processed {commit_count} commits")
                self._author_commits_cache = dict(author_commits)
            except Exception as e:
                print(f"Error while getting commits by author: {e}")
                raise ValueError(f"Error fetching commit authors: {str(e)}") from e
        return self._author_commits_cache

    def get_recent_commits(self, limit: int = 20) -> List[CommitInfo]:
        """Get recent commits."""
        print(f"Getting {limit} recent commits...")
        self._ensure_connected()
        if not self._recent_commits_cache:
            commits = []
            try:
                for commit in self.repo.iter_commits(max_count=limit):  # type: ignore
                    commit_hash = str(commit.hexsha[:8])
                    author = (
                        str(commit.author.name) if commit.author.name else "Unknown"
                    )
                    message = str(commit.message).split("\n")[0]

                    commits.append(
                        CommitInfo(
                            hash=commit_hash,
                            author=author,
                            date=commit.authored_datetime,
                            message=message,
                        )
                    )
                print(f"Retrieved {len(commits)} recent commits")
                self._recent_commits_cache = commits
            except Exception as e:
                print(f"Error while getting recent commits: {e}")
                raise ValueError(f"Error fetching recent commits: {str(e)}") from e
        return self._recent_commits_cache

    def clear_cache(self) -> None:
        """Clear all cached data."""
        print("Clearing all caches")
        self._commit_time_cache.clear()
        self._author_commits_cache.clear()
        self._recent_commits_cache.clear()

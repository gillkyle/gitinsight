"""Views package for GitInsight."""

from .author_commits import AuthorCommitsView
from .base import BaseView
from .commit_time import CommitTimeView
from .recent_commits import RecentCommitsView

__all__ = ["BaseView", "CommitTimeView", "AuthorCommitsView", "RecentCommitsView"]

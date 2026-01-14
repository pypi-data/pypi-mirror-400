"""GitHub contribution graph gamification tool."""

from .github_client import (
    ContributionData,
    ContributionDay,
    ContributionWeek,
    GitHubAPIError,
    GitHubClient,
)

__version__ = "0.1.0"

__all__ = [
    "GitHubClient",
    "GitHubAPIError",
    "ContributionData",
    "ContributionDay",
    "ContributionWeek",
]

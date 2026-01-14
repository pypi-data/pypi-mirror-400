"""GraphQL client for GitLab work item operations.

GitLab's work item parent-child relationships are only available via GraphQL API.
"""

from .client import GitLabGraphQLClient

__all__ = ["GitLabGraphQLClient"]

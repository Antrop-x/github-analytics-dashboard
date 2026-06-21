"""
Infrastructure layer - Camada de infraestrutura e abstração técnica

Exports:
- RepositoryApiClient: Interface para acesso a repositórios
- GitHubRepositoryAdapter: Implementação usando GitHub API
- GitHubApiClient: Cliente baixo nível de GitHub (uso interno apenas)
"""

from infrastructure.base_api import RepositoryApiClient
from infrastructure.github_repository_adapter import GitHubRepositoryAdapter

__all__ = [
    "RepositoryApiClient",
    "GitHubRepositoryAdapter",
]

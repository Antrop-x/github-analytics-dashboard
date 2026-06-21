"""
GitHub Repository Adapter - Adaptador que implementa RepositoryApiClient
usando GitHubApiClient como infraestrutura subjacente.

Implementa o padrão Adapter (Adapter Pattern) para abstrair a dependência
direta de GitHubApiClient, permitindo inversão de controle e testabilidade.
"""

import logging
from typing import Dict, List, Optional

from infrastructure.base_api import RepositoryApiClient
from infrastructure.github_api import GitHubApiClient, RateLimitError

logger = logging.getLogger(__name__)


class GitHubRepositoryAdapter(RepositoryApiClient):
    """
    Implementação de RepositoryApiClient usando GitHubApiClient.
    
    Este adaptador encapsula a comunicação com GitHub API e fornece
    uma interface genérica que pode ser substituída por outras implementações.
    
    Exemplos de alternativas futuras:
    - GitLabRepositoryAdapter
    - BitbucketRepositoryAdapter
    - MockRepositoryAdapter (para testes)
    """

    def __init__(self, token: Optional[str] = None, per_page: int = 30, base_url: str = "https://api.github.com"):
        """
        Inicializa o adaptador com um cliente GitHub.
        
        Args:
            token: Token de autenticação do GitHub (opcional)
            per_page: Quantidade padrão de itens por página
            base_url: URL base da API
        """
        self._client = GitHubApiClient(token=token, per_page=per_page, base_url=base_url)
        logger.info(f"GitHubRepositoryAdapter inicializado com base_url={base_url}")

    def fetch_repos(
        self,
        query: str,
        sort: str = "stars",
        per_page: int = 30,
        page: int = 1,
        headers: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Busca repositórios de uma página específica.
        
        Args:
            query: Termo de busca
            sort: Campo para ordenação (stars, forks, updated)
            per_page: Quantidade de itens por página
            page: Número da página (1-indexed)
            headers: Headers customizados (opcional)
            
        Returns:
            Lista de repositórios encontrados
            
        Raises:
            RateLimitError: Se o rate limit foi atingido
        """
        try:
            result = self._client.fetch_repos(
                query=query,
                sort=sort,
                per_page=per_page,
                page=page,
                headers=headers
            )
            return result
        except RateLimitError as e:
            logger.error(f"Rate limit atingido ao buscar repos: {e}")
            raise

    def fetch_multiple_pages(
        self,
        query: str,
        pages: int = 2,
        sort: str = "stars",
        per_page: int = 30
    ) -> List[Dict]:
        """
        Busca múltiplas páginas de repositórios.
        
        Args:
            query: Termo de busca
            pages: Número de páginas a buscar
            sort: Campo para ordenação
            per_page: Quantidade de itens por página
            
        Returns:
            Lista consolidada de repositórios
            
        Raises:
            RateLimitError: Se o rate limit foi atingido
        """
        try:
            result = self._client.fetch_multiple_pages(
                query=query,
                pages=pages,
                sort=sort,
                per_page=per_page
            )
            return result
        except RateLimitError as e:
            logger.error(f"Rate limit atingido ao buscar múltiplas páginas: {e}")
            raise

    def health_check(self) -> bool:
        """
        Verifica saúde da conexão com o repositório.
        
        Returns:
            True se a conexão está funcionando, False caso contrário
        """
        try:
            is_healthy = self._client.health_check()
            logger.debug(f"Health check: {is_healthy}")
            return is_healthy
        except Exception as e:
            logger.error(f"Health check falhou: {e}")
            return False

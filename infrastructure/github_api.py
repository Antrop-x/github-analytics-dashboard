import requests
import time
import logging
from typing import List, Dict, Optional
from .base_api import RepositoryApiClient

logger = logging.getLogger(__name__)
GITHUB_API_URL = "https://api.github.com/search/repositories"
DEFAULT_TIMEOUT = 10


class RateLimitError(RuntimeError):
    def __init__(self, response, partial_results: Optional[List[Dict]] = None):
        super().__init__("RATE_LIMIT")
        self.response = response
        self.partial_results = partial_results or []

# ==============================
# CONFIGURAÇÃO DE REQUISIÇÃO
# ==============================

def _make_request(params: Dict, headers: Optional[Dict] = None) -> Dict:
    """
    Executa requisição HTTP com tratamento básico de erro.
    """
    try:
        response = requests.get(
            GITHUB_API_URL,
            params=params,
            headers=headers or {},
            timeout=DEFAULT_TIMEOUT
        )
        if response.status_code == 403:
            logger.warning("Rate limit atingido")
            raise RateLimitError(response)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição GitHub: {e}")
        raise


# ==============================
# NORMALIZAÇÃO BRUTA
# ==============================

def _normalize_items(items: List[Dict]) -> List[Dict]:
    """
    Converte resposta bruta do GitHub em estrutura padronizada.
    """
    normalized = []
    for item in items:
        normalized.append({
            "name": item.get("full_name"),
            "stars": item.get("stargazers_count", 0),
            "forks": item.get("forks_count", 0),
            "description": item.get("description", ""),
            "url": item.get("html_url", ""),
            "updated_at": item.get("updated_at", "")
        })
    return normalized


class GitHubApiClient(RepositoryApiClient):
    """
    Cliente para a API de busca de repositórios do GitHub.
    """

    def __init__(self, token: Optional[str] = None, per_page: int = 30):
        self.token = token
        self.per_page = per_page

    def _build_headers(self) -> Dict[str, str]:
        headers = {}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    def fetch_repos(
        self,
        query: str = "language:python",
        sort: str = "stars",
        per_page: int = 30,
        page: int = 1,
        headers: Optional[Dict] = None
    ) -> List[Dict]:
        params = {
            "q": query,
            "sort": sort,
            "order": "desc",
            "per_page": per_page,
            "page": page
        }
        payload = _make_request(params, headers=headers or self._build_headers())
        return _normalize_items(payload.get("items", []))

    def fetch_multiple_pages(
        self,
        query: str,
        pages: int = 2,
        sort: str = "stars",
        per_page: int = 30
    ) -> List[Dict]:
        results: List[Dict] = []
        for page in range(1, pages + 1):
            try:
                batch = self.fetch_repos(query, sort, per_page, page)
                results.extend(batch)
                time.sleep(1)
            except RateLimitError as e:
                e.partial_results = results
                raise e
        return results

    def health_check(self) -> bool:
        try:
            _make_request({"q": "language:python", "per_page": 1}, headers=self._build_headers())
            return True
        except Exception:
            return False

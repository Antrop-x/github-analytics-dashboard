"""
GitHub API Client - Infraestrutura de coleta de dados

Responsabilidades:
- Comunicação com GitHub API v3
- Retry automático com backoff exponencial
- Detecção robusto de rate limiting
- Cache com TTL para dados estáveis
- Tratamento específico de erros de rede
"""

import logging
import time
from functools import wraps
from typing import Dict, Optional, Any, List
from urllib.parse import urlencode
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry as Urllib3Retry

from config.settings import Settings

logger = logging.getLogger(__name__)


def _normalize_repository_fields(raw_item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mapeia campos da API do GitHub para o esquema esperado pelo sistema.
    
    GitHub API → Sistema
    - stargazers_count → stars
    - forks_count → forks
    - html_url → url
    - full_name → name
    
    Args:
        raw_item: Item bruto da API do GitHub
    
    Returns:
        Item normalizado com campos renomeados
    """
    normalized = {
        "name": raw_item.get("full_name"),
        "stars": raw_item.get("stargazers_count", 0),
        "forks": raw_item.get("forks_count", 0),
        "url": raw_item.get("html_url"),
        "description": raw_item.get("description", ""),
        "updated_at": raw_item.get("updated_at"),
    }
    return normalized


def _normalize_repositories_batch(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normaliza um lote de repositórios da API.
    
    Args:
        items: Lista de itens brutos
    
    Returns:
        Lista de itens normalizados
    """
    return [_normalize_repository_fields(item) for item in items]


class RateLimitError(Exception):
    """Exceção para rate limit do GitHub"""
    pass


class GitHubApiClient:
    """
    Cliente robusto para GitHub API v3 com retry automático.
    
    Melhorias implementadas:
    ✅ Timeout como tuple (connect, read) - evita ConnectTimeout indefinido
    ✅ Retry automático na infraestrutura (Session + HTTPAdapter)
    ✅ Detecção robusto de rate limit via X-RateLimit-Remaining
    ✅ Tratamento específico de erros (ConnectTimeout, ReadTimeout, ConnectionError)
    ✅ Logs detalhados (tempo de resposta, tentativas, origem do erro)
    """
    
    # Timeout: (connect_timeout, read_timeout) em segundos
    REQUEST_TIMEOUT = (10, 30)
    
    # Configuração de retry do urllib3
    RETRY_STRATEGY = Urllib3Retry(
        total=3,  # 3 tentativas totais
        backoff_factor=0.5,  # 0.5s, 1s, 2s entre tentativas
        status_forcelist=[429, 500, 502, 503, 504],  # Retry em rate limit e server errors
        allowed_methods=["GET"]  # Apenas GET é seguro para retry
    )
    
    def __init__(self, token: Optional[str] = None, per_page: int = 30, base_url: str = "https://api.github.com"):
        """
        Inicializa cliente com sessão preparada para retry automático.
        
        Args:
            token: GitHub API token (ghp_*) ou None para buscar de Settings
            per_page: Quantidade padrão de itens por página
            base_url: URL base da API
        """
        self.base_url = base_url
        self.token = token or Settings.get_github_token()
        self.per_page = per_page
        
        # Criar sessão com retry automático
        self.session = self._create_session()
        self.last_rate_limit_remaining = None
        self.last_response_time_ms = None
        
        logger.info(f"GitHubApiClient inicializado: {base_url}")
    
    def _create_session(self) -> requests.Session:
        """Cria sessão com HTTPAdapter para retry automático."""
        session = requests.Session()
        adapter = HTTPAdapter(max_retries=self.RETRY_STRATEGY)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session
    
    def _build_headers(self) -> Dict[str, str]:
        """Headers com autenticação."""
        if not self.token:
            raise RuntimeError("GitHub API token is required")

        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "github-analytics-dashboard",
        }

    def _get_headers(self) -> Dict[str, str]:
        """Alias para compatibilidade interna."""
        return self._build_headers()
    
    def _track_rate_limit(self, response_headers: Dict[str, str]):
        """Registra estado atual de rate limit."""
        remaining = response_headers.get("X-RateLimit-Remaining", "?")
        limit = response_headers.get("X-RateLimit-Limit", "?")
        reset = response_headers.get("X-RateLimit-Reset", "?")
        
        try:
            self.last_rate_limit_remaining = int(remaining)
        except ValueError:
            pass
        
        logger.debug(f"Rate limit: {remaining}/{limit} (reset em {reset})")
    
    def _is_rate_limited(self, response_headers: Dict[str, str]) -> bool:
        """
        Detecta rate limit através de múltiplos indicadores.
        
        Melhoria: Não usar só status_code == 403
        Verificar X-RateLimit-Remaining == 0
        """
        # Indicador 1: Status 403 (legado)
        if response_headers.get("Status") == "403 Forbidden":
            return True
        
        # Indicador 2: X-RateLimit-Remaining = 0 (mais confiável)
        try:
            remaining = int(response_headers.get("X-RateLimit-Remaining", -1))
            if remaining == 0:
                return True
        except ValueError:
            pass
        
        # Indicador 3: Retry-After header (indicador oficial)
        if "Retry-After" in response_headers:
            return True
        
        return False
    
    def _make_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Faz requisição com tratamento específico de erros.
        
        Melhoria: Separar ConnectTimeout, ReadTimeout, ConnectionError
        Evitar except genérico
        """
        start_time = time.time()
        attempt = 0
        max_attempts = 3
        
        while attempt < max_attempts:
            attempt += 1
            
            try:
                logger.debug(
                    f"Tentativa {attempt}/{max_attempts}: {method} {url} "
                    f"(params: {params})"
                )
                
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=self._build_headers(),
                    params=params,
                    timeout=self.REQUEST_TIMEOUT,  # Tuple (connect, read)
                    **kwargs
                )
                
                elapsed_ms = (time.time() - start_time) * 1000
                self.last_response_time_ms = elapsed_ms
                
                # Rastrear rate limit
                self._track_rate_limit(response.headers)
                
                # Detectar rate limit ANTES de lançar exceção
                if self._is_rate_limited(response.headers):
                    retry_after = response.headers.get("Retry-After", "60")
                    msg = f"Rate limited (retry-after: {retry_after}s)"
                    logger.warning(msg)
                    raise RateLimitError(msg)
                
                # Outros erros HTTP
                if response.status_code >= 400:
                    logger.error(
                        f"HTTP {response.status_code} em {url} "
                        f"(tentativa {attempt}, {elapsed_ms:.1f}ms)"
                    )
                    response.raise_for_status()
                
                logger.debug(
                    f"✓ Sucesso em {elapsed_ms:.1f}ms "
                    f"(tentativa {attempt})"
                )
                
                return {
                    "status": "success",
                    "data": response.json() if response.text else {},
                    "headers": dict(response.headers),
                    "response_time_ms": elapsed_ms,
                    "attempts": attempt,
                }
            
            except requests.exceptions.ConnectTimeout as e:
                # Timeout de conexão (TCP handshake)
                logger.warning(
                    f"ConnectTimeout em {url} "
                    f"(tentativa {attempt}/{max_attempts}): {e}"
                )
                if attempt >= max_attempts:
                    raise
                time.sleep(0.5 * attempt)  # Backoff: 0.5s, 1s, 1.5s
            
            except requests.exceptions.ReadTimeout as e:
                # Timeout de leitura (resposta lenta)
                logger.warning(
                    f"ReadTimeout em {url} "
                    f"(tentativa {attempt}/{max_attempts}): {e}"
                )
                if attempt >= max_attempts:
                    raise
                time.sleep(0.5 * attempt)
            
            except requests.exceptions.ConnectionError as e:
                # Erro de conexão (DNS, reset, etc)
                logger.warning(
                    f"ConnectionError em {url} "
                    f"(tentativa {attempt}/{max_attempts}): {e}"
                )
                if attempt >= max_attempts:
                    raise
                time.sleep(0.5 * attempt)
            
            except requests.exceptions.HTTPError as e:
                # Erro HTTP não-rate-limit
                logger.error(f"HTTP error em {url}: {e}")
                raise
            
            except RateLimitError:
                # Rate limit é fatal, não retry
                raise
            
            except Exception as e:
                # Erro inesperado
                logger.error(f"Erro inesperado em {url}: {type(e).__name__}: {e}")
                raise
        
        # Nunca deve chegar aqui (exceções são levantadas dentro do loop)
        raise RuntimeError(f"Falha após {max_attempts} tentativas em {url}")
    
    def health_check(self) -> bool:
        """Verifica se API está acessível."""
        try:
            result = self._make_request("GET", f"{self.base_url}/rate_limit")
            logger.info("✓ API health check passed")
            return result["status"] == "success"
        except Exception as e:
            logger.error(f"✗ API health check failed: {e}")
            return False
    
    def fetch_repos(
        self,
        query: str,
        sort: str = "stars",
        page: int = 1,
        per_page: int = 100
    ) -> Dict[str, Any]:
        """
        Busca repositórios com uma query específica (1 página).
        
        Args:
            query: Query de busca (ex: "language:python stars:>1000")
            sort: Campo para ordenação (stars, forks, updated)
            page: Número da página (1-indexed)
            per_page: Itens por página (1-100)
        
        Returns:
            {
                "status": "success" | "rate_limited" | "error",
                "data": {
                    "total_count": int,
                    "items": [...],
                    "incomplete_results": bool
                },
                "headers": {...},
                "response_time_ms": float,
                "attempts": int
            }
        """
        params = {
            "q": query,
            "sort": sort,
            "order": "desc",
            "page": page,
            "per_page": min(per_page, 100),
        }
        
        try:
            result = self._make_request(
                "GET",
                f"{self.base_url}/search/repositories",
                params=params
            )
            return {**result, "status": "success"}
        
        except RateLimitError as e:
            logger.error(f"Rate limited: {e}")
            return {
                "status": "rate_limited",
                "data": None,
                "error": str(e),
                "response_time_ms": self.last_response_time_ms or 0,
                "attempts": 0,
            }
        
        except Exception as e:
            logger.error(f"Erro fetching repos: {e}")
            return {
                "status": "error",
                "data": None,
                "error": str(e),
                "response_time_ms": self.last_response_time_ms or 0,
                "attempts": 0,
            }

    def fetch_multiple_pages(
        self,
        query: str,
        pages: int = 10,
        max_pages: Optional[int] = None,
        sort: str = "stars",
        per_page: int = 100
    ) -> Dict[str, Any]:
        """
        Busca múltiplas páginas de repositórios.

        Melhoria: Tolerante a falhas - retorna dados parciais
        Se página 1-3 funcionam e 4 falha, retorna resultado de 1-3

        Args:
            query: Query de busca
            pages: Número de páginas a buscar
            max_pages: Alias compatível para páginas
            sort: Campo para ordenação (stars, forks, updated)
            per_page: Itens por página

        Returns:
            {
                "status": "success" | "partial" | "rate_limited" | "error",
                "total_pages_fetched": int,
                "items": [all items from all pages],
                "total_count": int,
                "incomplete_results": bool,
                "response_time_ms": float
            }
        """
        start_time = time.time()
        all_items = []
        total_count = 0
        incomplete_results = False
        pages_fetched = 0
        last_status = None
        target_pages = max_pages if max_pages is not None else pages

        for page in range(1, target_pages + 1):
            logger.info(f"Buscando página {page}/{target_pages}...")

            result = self.fetch_repos(
                query=query,
                sort=sort,
                page=page,
                per_page=per_page
            )

            last_status = result["status"]

            if result["status"] == "success":
                data = result.get("data", {})
                items = data.get("items", [])

                # NORMALIZAR CAMPOS DA API
                normalized_items = _normalize_repositories_batch(items)
                
                all_items.extend(normalized_items)
                total_count = data.get("total_count", 0)
                incomplete_results = data.get("incomplete_results", False)
                pages_fetched = page
                
                logger.info(
                    f"✓ Página {page}: {len(normalized_items)} items normalizados "
                    f"({result['response_time_ms']:.1f}ms, "
                    f"tentativa {result.get('attempts', 1)})"
                )

                # Se temos menos items que esperado, provavelmente chegou no final
                if len(normalized_items) < per_page:
                    logger.info(f"Última página alcançada ({len(normalized_items)} < {per_page})")
                    break

            elif result["status"] == "rate_limited":
                logger.warning(f"Rate limited na página {page}")
                # Retornar dados parciais coletados até agora
                break

            elif result["status"] == "error":
                logger.error(f"Erro na página {page}: {result.get('error')}")
                # Retornar dados parciais coletados até agora
                break

        elapsed_ms = (time.time() - start_time) * 1000

        target_pages = max_pages if max_pages is not None else pages

        # Determinar status final
        if pages_fetched == 0:
            final_status = last_status or "error"
        elif pages_fetched < target_pages and last_status in ["rate_limited", "error"]:
            final_status = "partial"
        else:
            final_status = "success"

        return {
            "status": final_status,
            "total_pages_fetched": pages_fetched,
            "items": all_items,
            "total_count": total_count,
            "incomplete_results": incomplete_results,
            "response_time_ms": elapsed_ms,
        }


def cache_with_ttl(ttl_seconds: int = 3600):
    """
    Decorator para cache com TTL (time-to-live).
    
    Melhoria: Cache com TTL evita dados stale
    Nunca mascare estado da API (rate_limited flag)
    
    Args:
        ttl_seconds: Tempo de vida do cache em segundos
    """
    def decorator(func):
        cache = {}
        cache_times = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave de cache
            key = (args, tuple(sorted(kwargs.items())))
            
            try:
                key_hashable = hash(key)
            except TypeError:
                # Se não é hashable, não cachear
                return func(*args, **kwargs)
            
            now = time.time()
            
            # Verificar se cache é válido
            if key_hashable in cache:
                cached_time = cache_times[key_hashable]
                if now - cached_time < ttl_seconds:
                    logger.debug(f"Cache hit para {func.__name__}")
                    return cache[key_hashable]
                else:
                    logger.debug(f"Cache expirado para {func.__name__}")
                    del cache[key_hashable]
                    del cache_times[key_hashable]
            
            # Calcular e cachear resultado
            result = func(*args, **kwargs)
            cache[key_hashable] = result
            cache_times[key_hashable] = now
            
            return result
        
        return wrapper
    
    return decorator


def ensure_pipeline_safety(df_or_error) -> Dict[str, Any]:
    """
    Valida resultado do pipeline sem lançar erro.
    
    Melhoria: Não lançar erro para DataFrame vazio
    Deixar pipeline degradar graciosamente
    
    Args:
        df_or_error: DataFrame ou dict de erro
    
    Returns:
        {"status": "ok" | "empty" | "error", "data": df_or_error}
    """
    import pandas as pd
    
    if isinstance(df_or_error, dict):
        if "error" in df_or_error:
            logger.warning(f"Pipeline error: {df_or_error['error']}")
            return {"status": "error", "data": None}
    
    if isinstance(df_or_error, pd.DataFrame):
        if df_or_error.empty:
            logger.info("Pipeline retornou DataFrame vazio (degradação graciosa)")
            return {"status": "empty", "data": df_or_error}
        return {"status": "ok", "data": df_or_error}
    
    logger.error(f"Tipo inesperado no pipeline: {type(df_or_error)}")
    return {"status": "error", "data": None}

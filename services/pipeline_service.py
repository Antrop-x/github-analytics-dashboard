import time
import logging
from typing import List, Dict, Optional, Callable
from functools import lru_cache
import pandas as pd
from infrastructure.github_api import GitHubApiClient, RateLimitError
from infrastructure.base_api import RepositoryApiClient
from core.metrics import build_metrics, compute_hegemony_index, segment_repositories
from models.domain import validate_repository_df, to_repository_objects

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ==============================
# CACHE LAYER (IN-MEMORY)
# ==============================
@lru_cache(maxsize=64)
def _cached_fetch(query: str, pages: int, sort: str, client_name: str) -> List[Dict]:
    logger.debug(f"Cache hit para query: {query}, pages: {pages}, sort: {sort}")
    client = GitHubApiClient() if client_name == "GitHubApiClient" else GitHubApiClient()
    return client.fetch_multiple_pages(query=query, pages=pages, sort=sort)

# ==============================
# RATE LIMIT HANDLING
# ==============================
class RateLimitHandler:
    """
    Gerencia controle de rate limit com intervalo mínimo entre chamadas.
    """

    def __init__(self, min_interval: float = 1.2):
        self.last_call_time = 0.0
        self.min_interval = min_interval

    def wait_if_needed(self) -> None:
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            logger.debug(f"Aguardando {self.min_interval - elapsed:.2f}s por rate limit")
            time.sleep(self.min_interval - elapsed)
        self.last_call_time = time.time()


rate_limiter = RateLimitHandler()

# ==============================
# RATE LIMIT RESPONSE HANDLER
# ==============================
def handle_rate_limit(response) -> bool:
    """
    Detecta e aguarda rate limit da API GitHub.
    Retorna True se rate limit foi detectado e tratado.
    """
    if hasattr(response, 'status_code') and response.status_code == 403:
        reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
        sleep_time = max(reset_time - time.time(), 0)
        logger.warning(f"Rate limit detectado. Aguardando {sleep_time:.0f}s para reset")
        if sleep_time > 0:
            time.sleep(sleep_time)
        return True
    return False

# ==============================
# RETRY POLICY
# ==============================
def retry_with_backoff(func: Callable[[], List[Dict]], retries: int = 3, base_delay: float = 2.0) -> tuple[List[Dict], bool]:
    """
    Executa função com retry exponencial e retorna se houve rate limit.
    """
    rate_limited = False
    for attempt in range(retries):
        try:
            logger.debug(f"Tentativa {attempt + 1} de {retries}")
            return func(), rate_limited
        except RateLimitError as e:
            rate_limited = True
            logger.warning(f"Tentativa {attempt + 1} interrompida por rate limit")
            if handle_rate_limit(e.response):
                if attempt < retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.info(f"Retrying em {delay:.2f}s após rate limit")
                    time.sleep(delay)
                    continue
            logger.error("Rate limit persistente após tratamento")
            return e.partial_results, rate_limited
        except Exception as e:
            logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
            if attempt < retries - 1:
                delay = base_delay * (2 ** attempt)
                logger.info(f"Retrying em {delay:.2f}s")
                time.sleep(delay)
            else:
                logger.error(f"Falha após {retries} tentativas: {e}")
                raise
    return [], rate_limited


# ==============================
# FETCH RAW DATA
# ==============================
def fetch_raw_data(
    query: str = "language:python",
    pages: int = 2,
    sort: str = "stars",
    api_client: Optional[RepositoryApiClient] = None,
    use_cache: bool = True
) -> tuple[List[Dict], bool]:
    client = api_client or GitHubApiClient()
    if use_cache:
        return _cached_fetch(query, pages, sort, client.__class__.__name__), False
    return retry_with_backoff(lambda: client.fetch_multiple_pages(query=query, pages=pages, sort=sort))


# ==============================
# NORMALIZAÇÃO E VALIDAÇÃO DE DADOS
# ==============================
def validate_repository_data(df: pd.DataFrame) -> bool:
    if not validate_repository_df(df):
        logger.warning("Dados inválidos recebidos da API.")
        return False
    return True


def ensure_pipeline_safety(df: pd.DataFrame) -> pd.DataFrame:
    """
    Verifica se o DataFrame não é None e não está vazio, lançando exceções claras.
    """
    if df is None:
        raise ValueError("DataFrame não pode ser None. Verifique a entrada de dados.")
    if df.empty:
        raise ValueError("DataFrame não pode estar vazio. Nenhum dado foi processado.")
    return df


def normalize_repository_data(df: pd.DataFrame) -> pd.DataFrame:
    return ensure_pipeline_safety(df)


def enrich_repository_data(df: pd.DataFrame) -> pd.DataFrame:
    df = build_metrics(df)
    return ensure_pipeline_safety(df)

# ==============================
# INGESTÃO PRINCIPAL
# ==============================
def ingest_repositories(
    query: str = "language:python",
    pages: int = 2,
    sort: str = "stars",
    use_cache: bool = True,
    api_client: Optional[RepositoryApiClient] = None
) -> Dict:
    logger.info(f"Iniciando ingestão: query='{query}', pages={pages}, sort='{sort}', cache={use_cache}")
    rate_limiter.wait_if_needed()
    
    raw_data, rate_limited = fetch_raw_data(query, pages, sort, api_client=api_client, use_cache=use_cache)

    status = "partial" if rate_limited else "success"

    if not raw_data:
        logger.info("Nenhum dado retornado da API.")
        empty_df = pd.DataFrame()
        empty_heg = pd.DataFrame()
        return {
            "data": empty_df,
            "hegemony": empty_heg,
            "rate_limited": rate_limited,
            "records": 0
        }

    df = pd.DataFrame(raw_data)
    logger.debug(f"Dados brutos recebidos: {len(df)} registros")

    if not validate_repository_data(df):
        empty_df = pd.DataFrame()
        empty_heg = pd.DataFrame()
        return {
            "data": empty_df,
            "hegemony": empty_heg,
            "rate_limited": rate_limited,
            "status": status,
            "records": 0,
            "requested_pages": pages
        }

    df = normalize_repository_data(df)
    if df.empty:
        logger.warning("DataFrame vazio após normalização")
        empty_heg = pd.DataFrame()
        return {
            "data": df,
            "hegemony": empty_heg,
            "rate_limited": rate_limited,
            "status": status,
            "records": 0,
            "requested_pages": pages
        }

    repository_objects = to_repository_objects(df)
    logger.debug(f"Convertidos {len(repository_objects)} repositórios usando contrato de dados")

    df = enrich_repository_data(df)
    heg = compute_hegemony_index(df)
    
    if rate_limited:
        logger.warning(
            f"Ingestão parcial devido a rate limit: pages={pages}, records coletados={len(df)}"
        )
    else:
        logger.info(
            f"Ingestão concluída com sucesso: pages={pages}, records processados={len(df)}"
        )
    
    import datetime
    log_info = {
        "timestamp": datetime.datetime.now().isoformat(),
        "query": query,
        "pages_collected": pages if not rate_limited else len(df) // 30,  # approx
        "total_records": len(df),
        "sort_by": sort
    }
    
    return {
        "data": df,
        "hegemony": heg,
        "rate_limited": rate_limited,
        "status": status,
        "records": len(df),
        "requested_pages": pages,
        "log": log_info
    }

# ==============================
# INGESTÃO OTIMIZADA (FAST PATH)
# ==============================
def ingest_fast(
    query: str = "language:python",
    sort: str = "stars",
    use_cache: bool = True,
    api_client: Optional[RepositoryApiClient] = None
) -> Dict:
    logger.debug(f"Ingestão rápida para query: {query}")
    return ingest_repositories(query=query, pages=1, sort=sort, use_cache=use_cache, api_client=api_client)

# ==============================
# HEALTH CHECK DO SERVIÇO
# ==============================
def check_service_health(api_client: Optional[RepositoryApiClient] = None) -> Dict[str, bool]:
    client = api_client or GitHubApiClient()
    return {
        "service_available": client.health_check()
    }

# ==============================
# METADATA DO SERVIÇO
# ==============================
SERVICE_VERSION = "1.0.2"  # Atualizado para refletir melhorias
SERVICE_DESCRIPTION = (
    "Camada de orquestração entre API GitHub e modelos de dados. "
    "Responsável por confiabilidade, cache e controle de fluxo."
)
import time
import logging
from typing import List, Dict, Optional, Callable, Tuple
from functools import wraps
import pandas as pd
from infrastructure.base_api import RepositoryApiClient
from infrastructure.github_repository_adapter import GitHubRepositoryAdapter
from infrastructure.github_api import RateLimitError
from core.metrics import build_metrics, compute_hegemony_index, segment_repositories
from models.domain import validate_repository_df, enforce_schema, to_repository_objects

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ==============================
# CACHE COM TTL (TIME-TO-LIVE)
# ==============================

class CacheEntry:
    """Entry de cache com TTL para evitar dados stale."""
    def __init__(self, value: Tuple[List[Dict], bool], ttl_seconds: int = 300):
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds
    
    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl_seconds
    
    def get(self) -> Optional[Tuple[List[Dict], bool]]:
        if self.is_expired():
            logger.debug("Cache expirado (TTL).")
            return None
        return self.value


def _make_cache_key(query: str, pages: int, sort: str) -> str:
    """Gera chave de cache a partir dos parâmetros."""
    return f"{query}:{pages}:{sort}"


def _cached_fetch(cache: Dict[str, CacheEntry], client: RepositoryApiClient, query: str, pages: int, sort: str, use_cache: bool = True) -> Tuple[List[Dict], bool]:
    """
    Busca com cache com TTL. Retorna (dados, rate_limited).
    Cache expira em 5 minutos ou se houver rate limit.
    
    Args:
        cache: Dicionário de cache com TTL
        client: Cliente de repositório (implementa RepositoryApiClient)
        query: Query de busca
        pages: Número de páginas
        sort: Campo para ordenação
        use_cache: Se deve usar cache
        
    Returns:
        Tuple (dados, rate_limited)
    """
    cache_key = _make_cache_key(query, pages, sort)
    
    if use_cache:
        # Verificar cache válido
        if cache_key in cache:
            cached = cache[cache_key].get()
            if cached is not None:
                logger.debug(f"Cache HIT para query={query}, pages={pages}")
                return cached
    
    logger.debug(f"Cache MISS para query={query}, pages={pages}. Buscando da API...")
    
    logger.debug(f"Iniciando fetch_multiple_pages: query={query}, pages={pages}, sort={sort}")
    result = client.fetch_multiple_pages(query=query, pages=pages, sort=sort)
    items = result.get("items", [])
    logger.debug(f"Resultado da API: status={result.get('status')}, items={len(items)}, rate_limited={result.get('status') == 'rate_limited'}")
    
    rate_limited = result.get("status") == "rate_limited"
    normalized_items = items
    if items:
        df = pd.DataFrame(items)
        df = enforce_schema(df)
        df["stars"] = pd.to_numeric(df["stars"], errors="coerce").fillna(0).astype(int)
        df["forks"] = pd.to_numeric(df["forks"], errors="coerce").fillna(0).astype(int)
        if validate_repository_data(df):
            normalized_items = df.to_dict("records")
            cache_entry = CacheEntry((normalized_items, rate_limited), ttl_seconds=300)
            cache[cache_key] = cache_entry
            logger.debug(f"Dados válidos cacheados: {len(normalized_items)} itens")
        else:
            logger.warning("Dados não validados, não armazenando cache.")
    else:
        logger.warning("Nenhum item retornado para cachear.")
    
    return normalized_items, rate_limited


# ==============================
# VALIDAÇÃO E NORMALIZAÇÃO
# ==============================



# ==============================
# NORMALIZAÇÃO E VALIDAÇÃO DE DADOS
# ==============================
def validate_repository_data(df: pd.DataFrame) -> bool:
    logger.debug(f"validate_repository_data: df.shape={df.shape}, columns={list(df.columns)}")
    
    if df is None or df.empty:
        logger.warning("validate_repository_data: DataFrame é None ou vazio")
        return False
    
    # Log de inspeção
    logger.debug(f"validate_repository_data: primeiras 3 linhas: {df.head(3).to_dict()}")
    logger.debug(f"validate_repository_data: tipos: {df.dtypes.to_dict()}")
    
    valid = validate_repository_df(df)
    if not valid:
        logger.warning("Dados inválidos recebidos da API.")
    return valid


def clean_repository_data(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(f"Total bruto recebido: {len(df)}")
    logger.info(f"DataFrame inicial: {df.shape}")
    logger.info(f"Colunas: {df.columns.tolist()}")

    df = enforce_schema(df)
    df["stars"] = pd.to_numeric(df["stars"], errors="coerce").fillna(0).astype(int)
    df["forks"] = pd.to_numeric(df["forks"], errors="coerce").fillna(0).astype(int)

    invalid = df[df["name"].isna() | df["url"].isna()]
    if not invalid.empty:
        logger.warning(f"Exemplo inválido:\n{invalid.head()}")

    before = len(df)
    df = df.dropna(subset=["name", "url"])
    after = len(df)
    logger.warning(f"Linhas antes: {before}")
    logger.warning(f"Linhas depois: {after}")

    return df


def ensure_pipeline_safety(df: pd.DataFrame, allow_empty: bool = False) -> pd.DataFrame:
    """
    Valida DataFrame degradando graciosamente.
    
    Args:
        df: DataFrame para validar
        allow_empty: Se True, permite DataFrame vazio (degrada graciosamente)
                    Se False, lança erro (comportamento original)
    
    Returns:
        DataFrame validado
        
    Raises:
        ValueError: Se None ou (vazio e allow_empty=False)
    """
    if df is None:
        logger.error("DataFrame é None. Verifique a entrada de dados.")
        raise ValueError("DataFrame não pode ser None.")
    
    if df.empty:
        if allow_empty:
            logger.warning("DataFrame vazio. Pipeline degradando graciosamente.")
            return df
        else:
            logger.error("DataFrame vazio. Nenhum dado foi processado.")
            raise ValueError("DataFrame vazio.")
    
    return df


def normalize_repository_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza dados de repositório. Permite vazio para degradação graciosa."""
    return ensure_pipeline_safety(df, allow_empty=True)


def enrich_repository_data(df: pd.DataFrame) -> pd.DataFrame:
    """Enriquece dados com métricas. Permite vazio para degradação graciosa."""
    if df.empty:
        logger.warning("DataFrame vazio. Pulando enriquecimento.")
        return df
    df = build_metrics(df)
    return ensure_pipeline_safety(df, allow_empty=True)

# ==============================
# INGESTÃO PRINCIPAL
# ==============================
def ingest_repositories(
    query: str = "language:python",
    pages: int = 2,
    sort: str = "stars",
    use_cache: bool = True,
    api_client: Optional[RepositoryApiClient] = None,
    cache: Optional[Dict[str, CacheEntry]] = None,
    client: Optional[RepositoryApiClient] = None
) -> Dict:
    """
    Orquestra coleta e processamento de repositórios.
    
    Fluxo:
    1. Busca da API (com retry automático na infraestrutura)
    2. Validação básica
    3. Normalização
    4. Enriquecimento (métricas)
    5. Retorna dados ou degrada graciosamente
    
    Args:
        query: Query de busca
        pages: Número de páginas
        sort: Campo de ordenação
        use_cache: Se deve usar cache
        api_client: Cliente injetado (opcional, alternativa a client)
        cache: Cache customizado (opcional)
        client: Cliente alternativo (opcional)
    
    Returns:
        Dict com chaves:
        - data: DataFrame com repositórios
        - hegemony: DataFrame com índice de hegemonia
        - rate_limited: bool indicando rate limit
        - status: "success" ou "partial"
        - records: número de registros processados
        - requested_pages: páginas solicitadas
        - log: dict com metadados
    """
    import datetime
    
    cache = cache if cache is not None else {}
    client = client if client is not None else (api_client or GitHubRepositoryAdapter())

    start_time = time.time()
    logger.info(f"Iniciando ingestão: query='{query}', pages={pages}, sort='{sort}', cache={use_cache}")
    
    try:
        # Buscar dados (retry está na infraestrutura agora)
        raw_data, rate_limited = _cached_fetch(cache, client, query, pages, sort, use_cache)
        fetch_time = time.time() - start_time
        logger.info(f"Busca completada em {fetch_time:.2f}s. Coletados {len(raw_data)} registros.")
        
        if not raw_data:
            logger.warning("Nenhum dado retornado da API.")
            return {
                "data": pd.DataFrame(),
                "hegemony": pd.DataFrame(),
                "rate_limited": rate_limited,
                "status": "no_data",
                "records": 0,
                "requested_pages": pages,
                "log": {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "query": query,
                    "total_time": fetch_time,
                    "total_records": 0,
                    "sort_by": sort
                }
            }
        
        # Criar DataFrame
        df = pd.DataFrame(raw_data)
        logger.info(f"Total bruto recebido: {len(raw_data)}")
        logger.info(f"DataFrame inicial: {df.shape}")
        logger.info(f"Colunas: {df.columns.tolist()}")
        logger.debug(f"DataFrame criado com {len(df)} linhas e {len(df.columns)} colunas")
        
        # Limpeza relaxada de dados sujos
        if not validate_repository_data(df):
            logger.warning("Dados brutos contém problemas; aplicando limpeza relaxada.")
        df = clean_repository_data(df)
        if df.empty:
            logger.warning("DataFrame vazio após limpeza. Retornando vazio.")
            return {
                "data": df,
                "hegemony": pd.DataFrame(),
                "rate_limited": rate_limited,
                "status": "empty_after_clean",
                "records": 0,
                "requested_pages": pages,
                "log": {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "query": query,
                    "total_time": time.time() - start_time,
                    "total_records": 0,
                    "sort_by": sort
                }
            }
        
        # Normalizar (permitindo vazio para degradação graciosa)
        df = normalize_repository_data(df)
        
        if df.empty:
            logger.warning("DataFrame vazio após normalização. Retornando vazio.")
            return {
                "data": df,
                "hegemony": pd.DataFrame(),
                "rate_limited": rate_limited,
                "status": "empty_after_norm",
                "records": 0,
                "requested_pages": pages,
                "log": {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "query": query,
                    "total_time": time.time() - start_time,
                    "total_records": 0,
                    "sort_by": sort
                }
            }
        
        # Converter para objetos do domínio
        repository_objects = to_repository_objects(df)
        logger.debug(f"Convertidos {len(repository_objects)} repositórios usando contrato de dados")
        
        # Enriquecer com métricas
        enrich_start = time.time()
        df = enrich_repository_data(df)
        heg = compute_hegemony_index(df)
        enrich_time = time.time() - enrich_start
        logger.debug(f"Enriquecimento concluído em {enrich_time:.2f}s")
        
        status = "partial" if rate_limited else "success"
        total_time = time.time() - start_time
        
        if rate_limited:
            logger.warning(
                f"Ingestão parcial: rate_limited=True, pages={pages}, "
                f"registros_coletados={len(df)}, tempo_total={total_time:.2f}s"
            )
        else:
            logger.info(
                f"Ingestão bem-sucedida: pages={pages}, registros={len(df)}, "
                f"tempo_total={total_time:.2f}s"
            )
        
        return {
            "data": df,
            "hegemony": heg,
            "rate_limited": rate_limited,
            "status": status,
            "records": len(df),
            "requested_pages": pages,
            "log": {
                "timestamp": datetime.datetime.now().isoformat(),
                "query": query,
                "pages_collected": pages if not rate_limited else len(df) // 30,  # approx
                "total_records": len(df),
                "sort_by": sort,
                "total_time": total_time,
                "fetch_time": fetch_time,
                "enrich_time": enrich_time
            }
        }
        
    except RateLimitError as e:
        logger.warning(f"Rate limit na busca. Retornando {len(e.partial_results)} registros parciais.")
        if e.partial_results:
            df = pd.DataFrame(e.partial_results)
            if not df.empty and validate_repository_data(df):
                df = normalize_repository_data(df)
                df = enrich_repository_data(df) if not df.empty else df
                heg = compute_hegemony_index(df) if not df.empty else pd.DataFrame()
                return {
                    "data": df,
                    "hegemony": heg,
                    "rate_limited": True,
                    "status": "partial",
                    "records": len(df),
                    "requested_pages": pages,
                    "log": {
                        "timestamp": datetime.datetime.now().isoformat(),
                        "query": query,
                        "total_time": time.time() - start_time,
                        "total_records": len(df),
                        "sort_by": sort,
                        "error": "rate_limit"
                    }
                }
        
        return {
            "data": pd.DataFrame(),
            "hegemony": pd.DataFrame(),
            "rate_limited": True,
            "status": "rate_limited",
            "records": 0,
            "requested_pages": pages,
            "log": {
                "timestamp": datetime.datetime.now().isoformat(),
                "query": query,
                "total_time": time.time() - start_time,
                "total_records": 0,
                "sort_by": sort,
                "error": "rate_limit"
            }
        }
        
    except Exception as e:
        logger.error(f"Erro fatal na ingestão: {type(e).__name__}: {e}", exc_info=True)
        return {
            "data": pd.DataFrame(),
            "hegemony": pd.DataFrame(),
            "rate_limited": False,
            "status": "error",
            "records": 0,
            "requested_pages": pages,
            "log": {
                "timestamp": datetime.datetime.now().isoformat(),
                "query": query,
                "total_time": time.time() - start_time,
                "total_records": 0,
                "sort_by": sort,
                "error": str(e)
            }
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

def check_service_health(api_client: Optional[RepositoryApiClient] = None) -> Dict[str, bool]:
    """Verifica saúde do serviço de API."""
    client = api_client or GitHubRepositoryAdapter()
    return {
        "service_available": client.health_check()
    }


class PipelineService:
    """
    Serviço de Pipeline - Coordena coleta e processamento de dados.
    Isola lógica de pipeline da UI e interpretação.

    Depende de:
    - RepositoryApiClient: Abstração para acesso a repositórios (inversão de controle)
    """

    def __init__(self, settings):
        """
        Inicializa o serviço de pipeline com configurações.

        Args:
            settings: Configurações da aplicação
        """
        self.settings = settings

    def ingest_repositories(self, query: str = "language:python", pages: int = 2,
                           sort: str = "stars", use_cache: bool = True,
                           api_client: Optional[RepositoryApiClient] = None) -> Dict:
        """
        Método principal de ingestão de repositórios.

        Args:
            query: Query de busca do GitHub
            pages: Número de páginas a coletar
            sort: Ordenação dos resultados
            use_cache: Se deve usar cache
            api_client: Cliente de API injetado (para testes ou alternativas)

        Returns:
            Dicionário com dados coletados e metadados
        """
        return ingest_repositories(
            query=query,
            pages=pages,
            sort=sort,
            use_cache=use_cache,
            api_client=api_client
        )

# ==============================
# METADATA DO SERVIÇO
# ==============================
SERVICE_VERSION = "1.0.2"  # Atualizado para refletir melhorias
SERVICE_DESCRIPTION = (
    "Camada de orquestração entre API GitHub e modelos de dados. "
    "Responsável por confiabilidade, cache e controle de fluxo."
)
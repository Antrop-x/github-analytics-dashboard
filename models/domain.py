from dataclasses import dataclass, asdict
from typing import List
import logging
import pandas as pd

REPOSITORY_SCHEMA_COLUMNS = {
    "name",
    "stars",
    "forks",
    "description",
    "url",
    "updated_at"
}
# ==============================
# SCHEMA BASE DO REPOSITÓRIO
# ==============================
@dataclass
class RepositorySchema:
    """
    Representa a unidade mínima de observação do sistema.
    """
    name: str
    stars: int
    forks: int
    description: str
    url: str
    updated_at: str
# ==============================
# VALIDAÇÃO DE DATAFRAME
# ==============================
def validate_repository_df(df: pd.DataFrame) -> bool:
    """
    Valida e limpa o DataFrame do repositório de forma relaxada.
    """
    logger = logging.getLogger(__name__)

    if df is None or df.empty:
        logger.warning("validate_repository_df: DataFrame é None ou vazio")
        return False

    before = len(df)
    if "name" not in df.columns:
        df["name"] = None
    if "url" not in df.columns:
        df["url"] = None

    df.dropna(subset=["name", "url"], inplace=True)
    after = len(df)
    logger.warning(f"Linhas antes: {before}")
    logger.warning(f"Linhas depois: {after}")

    invalid = df[df["name"].isna() | df["url"].isna()]
    if not invalid.empty:
        logger.warning(f"Exemplo inválido:\n{invalid.head()}")

    if "stars" not in df.columns and "stargazers_count" in df.columns:
        df["stars"] = df["stargazers_count"]
    if "forks" not in df.columns and "forks_count" in df.columns:
        df["forks"] = df["forks_count"]

    df["stars"] = pd.to_numeric(df.get("stars", 0), errors="coerce").fillna(0)
    df["forks"] = pd.to_numeric(df.get("forks", 0), errors="coerce").fillna(0)

    if not pd.api.types.is_numeric_dtype(df["stars"]):
        logger.warning("validate_repository_df: stars não é numérico")
        return False

    if not pd.api.types.is_numeric_dtype(df["forks"]):
        logger.warning("validate_repository_df: forks não é numérico")
        return False

    return True
# ==============================
# NORMALIZAÇÃO DE ESQUEMA
# ==============================
def enforce_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rede de segurança: garante que colunas essenciais existam.
    Mapeia variantes de nomes de campos (ex: stargazers_count -> stars).
    
    Se o mapper da infraestrutura falhar, recria colunas a partir de variantes.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if df is None or df.empty:
        return pd.DataFrame()

    result = df.copy()
    
    # Mapear campos alternativos se coluna padrão não existe
    field_mappings = {
        "name": ["full_name", "name"],
        "stars": ["stargazers_count", "stars"],
        "forks": ["forks_count", "forks"],
        "url": ["html_url", "url"],
    }
    
    for target_col, source_cols in field_mappings.items():
        if target_col not in result.columns:
            # Procurar por coluna alternativa
            found = False
            for source_col in source_cols:
                if source_col in result.columns:
                    result[target_col] = result[source_col]
                    logger.debug(f"enforce_schema: mapeado '{source_col}' -> '{target_col}'")
                    found = True
                    break
            
            if not found:
                # Nenhuma coluna fonte encontrada, usar padrão
                if target_col in ["stars", "forks"]:
                    result[target_col] = 0
                else:
                    result[target_col] = ""
                logger.warning(f"enforce_schema: '{target_col}' criada com valor padrão")
    
    # Garantir tipos corretos
    result["name"] = result.get("name", "").fillna("unknown").astype(str)
    result["stars"] = pd.to_numeric(result.get("stars", 0), errors="coerce").fillna(0).astype(int)
    result["forks"] = pd.to_numeric(result.get("forks", 0), errors="coerce").fillna(0).astype(int)

    if "description" not in result.columns:
        result["description"] = ""
    if "url" not in result.columns:
        result["url"] = ""
    if "updated_at" not in result.columns:
        result["updated_at"] = ""

    return result[list(REPOSITORY_SCHEMA_COLUMNS)]
# ==============================
# CONVERSÃO PARA MODELO TIPADO
# ==============================
def to_repository_objects(df: pd.DataFrame) -> List[RepositorySchema]:
    """
    Converte DataFrame em lista de objetos tipados.
    Útil para validação futura e APIs externas.
    """
    if df is None or df.empty:
        return []

    df = enforce_schema(df)
    repositories: List[RepositorySchema] = []

    for record in df.to_dict(orient="records"):
        repositories.append(
            RepositorySchema(
                name=str(record.get("name", "unknown")),
                stars=int(record.get("stars", 0)),
                forks=int(record.get("forks", 0)),
                description=str(record.get("description", "")),
                url=str(record.get("url", "")),
                updated_at=str(record.get("updated_at", ""))
            )
        )
    return repositories


def repository_objects_to_dataframe(repos: List[RepositorySchema]) -> pd.DataFrame:
    return pd.DataFrame([asdict(repo) for repo in repos])


# ==============================
# SANITY CHECK (PIPELINE SAFETY)
# ==============================
def ensure_pipeline_safety(df: pd.DataFrame) -> pd.DataFrame:
    """
    Função de segurança final antes de qualquer processamento no /core.
    Combina validação + normalização.
    """
    if not validate_repository_df(df):
        return pd.DataFrame()
    return enforce_schema(df)
# ==============================
# METADATA DO SCHEMA
# ==============================
SCHEMA_VERSION = "1.0.0"
SCHEMA_DESCRIPTION = (
    "Contrato estrutural dos dados do Observatório do Trabalho Digital. "
    "Define como dados do GitHub são interpretados antes da camada de métricas."
)
from dataclasses import dataclass, asdict
from typing import List
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
    Valida se o DataFrame respeita o contrato mínimo esperado.
    """
    if df is None or df.empty:
        return False

    required_columns = {"name", "stars", "forks"}
    if not required_columns.issubset(set(df.columns)):
        return False

    if df["name"].isnull().any():
        return False

    if not pd.api.types.is_numeric_dtype(df["stars"]):
        return False

    if not pd.api.types.is_numeric_dtype(df["forks"]):
        return False

    return True
# ==============================
# NORMALIZAÇÃO DE ESQUEMA
# ==============================
def enforce_schema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Garante coerência estrutural dos dados antes de entrar no /core.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    result = df.copy()
    result["name"] = result["name"].fillna("unknown").astype(str)
    result["stars"] = result["stars"].fillna(0).astype(int)
    result["forks"] = result["forks"].fillna(0).astype(int)

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
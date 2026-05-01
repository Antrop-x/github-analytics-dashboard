from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class RepositoryApiClient(ABC):
    @abstractmethod
    def fetch_repos(
        self,
        query: str,
        sort: str = "stars",
        per_page: int = 30,
        page: int = 1,
        headers: Optional[Dict] = None
    ) -> List[Dict]:
        raise NotImplementedError

    @abstractmethod
    def fetch_multiple_pages(
        self,
        query: str,
        pages: int = 2,
        sort: str = "stars",
        per_page: int = 30
    ) -> List[Dict]:
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        raise NotImplementedError

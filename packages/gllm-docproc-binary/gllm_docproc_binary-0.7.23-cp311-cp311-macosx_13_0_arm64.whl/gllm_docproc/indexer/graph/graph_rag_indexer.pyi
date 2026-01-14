from abc import ABC, abstractmethod
from gllm_docproc.indexer import BaseIndexer as BaseIndexer

class BaseGraphRAGIndexer(BaseIndexer, ABC):
    """Abstract base class for Graph RAG Indexer.

    This class defines the interface for a Graph RAG Indexer.
    """
    @abstractmethod
    def resolve_entities(self) -> None:
        """Resolve entities in the graph."""

from gllm_datastore.graph_data_store.light_rag_data_store import BaseLightRAGDataStore
from gllm_docproc.indexer.graph.graph_rag_indexer import BaseGraphRAGIndexer as BaseGraphRAGIndexer
from gllm_docproc.model.element import Element as Element
from typing import Any

class LightRAGGraphRAGIndexer(BaseGraphRAGIndexer):
    '''Indexer abstract base class for LightRAG-based graph RAG.

    How to run LightRAG with PostgreSQL using Docker:
    ```bash
    docker run         -p 5455:5432         -d         --name postgres-LightRag         shangor/postgres-for-rag:v1.0         sh -c "service postgresql start && sleep infinity"
    ```

    Example:
        ```python
        from gllm_inference.em_invoker import OpenAIEMInvoker
        from gllm_inference.lm_invoker import OpenAILMInvoker
        from gllm_docproc.indexer.graph.light_rag_graph_rag_indexer import LightRAGGraphRAGIndexer
        from gllm_datastore.graph_data_store.light_rag_postgres_data_store import LightRAGPostgresDataStore

        # Create the LightRAGPostgresDataStore instance
        graph_store = LightRAGPostgresDataStore(
            lm_invoker=OpenAILMInvoker(model_name="gpt-4o-mini"),
            em_invoker=OpenAIEMInvoker(model_name="text-embedding-3-small"),
            postgres_db_host="localhost",
            postgres_db_port=5455,
            postgres_db_user="rag",
            postgres_db_password="rag",
            postgres_db_name="rag",
            postgres_db_workspace="default",
        )


        # Create the indexer
        indexer = LightRAGGraphRAGIndexer(graph_store=graph_store)

        # Create elements to index
        elements = [
            {
                "text": "This is a sample document about AI.",
                "structure": "uncategorized",
                "metadata": {
                    "source": "sample.txt",
                    "source_type": "TEXT",
                    "loaded_datetime": "2025-07-10T12:00:00",
                    "chunk_id": "chunk_001",
                    "file_id": "file_001"
                }
            }
        ]

        # Index the elements
        indexer.index(elements)
        ```

    Attributes:
        _graph_store (BaseLightRAGDataStore): The LightRAG data store used for indexing and querying.
    '''
    def __init__(self, graph_store: BaseLightRAGDataStore) -> None:
        """Initialize the LightRAGGraphRAGIndexer.

        Args:
            graph_store (BaseLightRAGDataStore): The LightRAG instance to use for indexing.
        """
    def index(self, elements: list[dict[str, Any]], **kwargs: Any) -> None:
        """Index elements into the LightRAG system and create graph relationships.

        This method extracts text and chunk IDs from the provided elements,
        inserts them into the LightRAG system, and creates a graph structure
        connecting files to chunks.

        Args:
            elements (list[dict[str, Any]]): List of Element objects containing text and metadata.
                Each element should have a metadata attribute with a chunk_id and a file_id.
            **kwargs (Any): Additional keyword arguments.
        """
    def delete(self, file_id: str | None = None, chunk_id: str | None = None, entity_id: str | None = None, **kwargs: Any) -> None:
        """Delete entities from the LightRAG system and graph.

        Supports multiple deletion modes based on the provided keyword arguments.
        Exactly one of the supported deletion parameters must be provided.

        Args:
            file_id (str, optional): Delete a file and all its associated chunks. Defaults to None.
            chunk_id (str, optional): Delete a specific chunk entity. Defaults to None.
            entity_id (str, optional): Delete a specific entity or node. Defaults to None.
            **kwargs (Any): Additional keyword arguments.

        Raises:
            ValueError: If no deletion parameter is provided or multiple are provided.
        """
    def resolve_entities(self) -> None:
        """Resolve entities from the graph.

        Currently, this method does nothing. Resolve entities
        has been implicitly implemented in the LightRAG instance.
        """

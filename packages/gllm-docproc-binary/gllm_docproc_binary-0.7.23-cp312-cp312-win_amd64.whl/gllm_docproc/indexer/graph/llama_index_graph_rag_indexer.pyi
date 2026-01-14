from _typeshed import Incomplete
from gllm_datastore.graph_data_store.llama_index_graph_rag_data_store import LlamaIndexGraphRAGDataStore
from gllm_docproc.indexer.graph.graph_rag_indexer import BaseGraphRAGIndexer as BaseGraphRAGIndexer
from gllm_docproc.indexer.graph.utils.schema_validator import validate_kg_schema as validate_kg_schema
from gllm_docproc.model.element import Element as Element
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.base.llms.base import BaseLLM
from llama_index.core.schema import TransformComponent as TransformComponent
from llama_index.core.vector_stores.types import BasePydanticVectorStore
from typing import Any

logger: Incomplete

class LlamaIndexGraphRAGIndexer(BaseGraphRAGIndexer):
    """Indexer for graph RAG using LlamaIndex.

    Attributes:
        _index (PropertyGraphIndex): Property graph index.
        _graph_store (LlamaIndexGraphRAGDataStore): Storage for property graph.
        _strict_mode (bool): Whether strict schema validation is enabled.
    """
    def __init__(self, graph_store: LlamaIndexGraphRAGDataStore, llama_index_llm: BaseLLM | None = None, allowed_entity_types: list[str] | None = None, allowed_relation_types: list[str] | None = None, kg_validation_schema: dict[str, list[str]] | None = None, strict_mode: bool = False, kg_extractors: list[TransformComponent] | None = None, embed_model: BaseEmbedding | None = None, vector_store: BasePydanticVectorStore | None = None, max_triplets_per_chunk: int = 10, num_workers: int = 4, **kwargs: Any) -> None:
        '''Initialize the LlamaIndexGraphRAGIndexer.

        Args:
            graph_store (LlamaIndexGraphRAGDataStore): Storage for property graph.
            llama_index_llm (BaseLLM | None, optional): Language model for LlamaIndex. Defaults to None.
            allowed_entity_types (list[str] | None, optional): List of allowed entity types. When strict_mode=True,
                only these types are extracted. When strict_mode=False, serves as hints. Defaults to None.
            allowed_relation_types (list[str] | None, optional): List of allowed relationship types. Behavior depends
                on strict_mode. Defaults to None.
            kg_validation_schema (dict[str, list[str]] | None, optional): Validation schema for
                strict mode. Maps entity types to their allowed outgoing relationship types.
                Format:
                {"ENTITY_TYPE": ["ALLOWED_REL1", "ALLOWED_REL2"], ...}
                Example: {"PERSON": ["WORKS_AT", "FOUNDED"], "ORGANIZATION": ["LOCATED_IN"]}
                Defaults to None.
            strict_mode (bool, optional): If True, uses SchemaLLMPathExtractor with strict validation.
                If False (default), uses DynamicLLMPathExtractor with optional guidance. Defaults to False.
            kg_extractors (list[TransformComponent] | None, optional): Custom list of extractors.
                If provided, overrides automatic extractor selection based on strict_mode. Defaults to None.
            embed_model (BaseEmbedding | None, optional): Embedding model for vector representations. Defaults to None.
            vector_store (BasePydanticVectorStore | None, optional): Storage for vector data. Defaults to None.
            max_triplets_per_chunk (int, optional): Maximum triplets to extract per chunk. Defaults to 10.
            num_workers (int, optional): Number of parallel workers. Defaults to 4.
            **kwargs (Any): Additional keyword arguments.
        '''
    def index(self, elements: list[Element] | list[dict[str, Any]], **kwargs: Any) -> None:
        """Index elements into the graph.

        This method indexes elements into the graph.

        Notes:
        - Currently only Neo4jPropertyGraphStore that is supported for indexing the metadata from the TextNode.
        - The 'document_id' parameter is used to specify the document ID for the elements.
        - The 'chunk_id' parameter is used to specify the chunk ID for the elements.

        Args:
            elements (list[Element] | list[dict[str, Any]]): List of elements or list of dictionaries representing
                elements to be indexed.
            **kwargs (Any): Additional keyword arguments.
        """
    def resolve_entities(self) -> None:
        """Resolve entities in the graph.

        Currently, this method does nothing.
        """
    def delete(self, **kwargs: Any) -> None:
        """Delete elements from the knowledge graph.

        This method deletes elements from the knowledge graph based on the provided document_id.

        Args:
            **kwargs (Any): Additional keyword arguments.

        Raises:
            ValueError: If document_id is not provided.
            Exception: If an error occurs during deletion.
        """

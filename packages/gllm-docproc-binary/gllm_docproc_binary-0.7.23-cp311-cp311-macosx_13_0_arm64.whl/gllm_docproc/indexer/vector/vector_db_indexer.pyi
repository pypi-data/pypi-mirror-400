from _typeshed import Incomplete
from gllm_datastore.core.capabilities import VectorCapability
from gllm_docproc.indexer import BaseIndexer as BaseIndexer
from gllm_docproc.model.element import Element as Element
from gllm_inference.schema import Vector as Vector
from typing import Any, TypeVar

T = TypeVar('T')

class VectorDBIndexer(BaseIndexer):
    """Index elements into a vector datastore capability."""
    logger: Incomplete
    vector_capability: Incomplete
    def __init__(self, vector_capability: VectorCapability) -> None:
        """Initialize the indexer with an optional vector capability instance.

        Args:
            vector_capability (VectorCapability): The capability implementation
                (for example, `ElasticsearchVectorCapability`) that will receive
                chunks for indexing operations. Must be set before calling
                indexing methods.
        """
    def index(self, elements: list[dict[str, Any]], **kwargs: Any) -> None:
        """Index elements into the configured vector capability.

        Args:
            elements (list[dict[str, Any]]): Parsed elements containing text and metadata.
            **kwargs (Any): Additional keyword arguments for customization.

        Kwargs:
            replace_file_id (str, optional): File identifier to be replaced before indexing.
                Defaults to None. If provided, existing records for this file_id are removed first.
            batch_size (int, optional): The number of chunks to process in each batch.
                Defaults to 100.
            max_retries (int, optional): The maximum number of retry attempts for failed batches.
                Defaults to 3.
            vectors (list[Vector] | None, optional): Pre-computed vectors for the elements.
                If provided, uses create_from_vector instead of create. Must match the length
                of elements. Defaults to None.

        Raises:
            Exception: If an error occurs during indexing.
        """
    def delete(self, **kwargs: Any) -> None:
        """Delete documents from the vector capability based on the file ID.

        Kwargs:
            file_id (str): The ID of the file(s) to be deleted.

        Raises:
            ValueError: If file_id is not provided.
            Exception: If an error occurs during deletion.
        """

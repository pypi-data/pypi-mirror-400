from _typeshed import Incomplete
from gllm_datastore.cache.hybrid_cache.hybrid_cache import BaseHybridCache
from gllm_docproc.loader.base_loader import BaseLoader as BaseLoader
from typing import Any

class PipelineLoader:
    """A pipeline loader for loading documents.

    This class serves as the pipeline loader for loading document. It defines the structure for
    loading document with several loaders using pipeline.

    Methods:
        add_loader(loader): Add loader to the pipeline loader.
        load(source, **kwargs): Load the document from the given source.
    """
    loaders: list[BaseLoader]
    cache_data_store: Incomplete
    logger: Incomplete
    def __init__(self, cache_data_store: BaseHybridCache | None = None) -> None:
        """Initialize the PipelineLoader.

        Args:
            cache_data_store (BaseHybridCache, optional): The cache data store to be used.
                Defaults to None.
        """
    def add_loader(self, loader: BaseLoader):
        """Add loader to the pipeline loader.

        This method defines the process of adding loader to the pipeline loader.

        Args:
            loader (BaseLoader): The loader to be added.
        """
    def load(self, source: str, **kwargs: Any) -> list[dict[str, Any]]:
        """Load the document from the given file path.

        This method defines the process of loading the document using loaders.

        Args:
            source (str): Might be file path, URL, the content itself.
            **kwargs (Any): Additional keyword arguments.

        Kwargs:
            ttl (int, optional): The TTL of the cache. Defaults to None.

        Returns:
            List[dict[str, Any]]: A list of dictionaries containing loaded content and metadata.
        """

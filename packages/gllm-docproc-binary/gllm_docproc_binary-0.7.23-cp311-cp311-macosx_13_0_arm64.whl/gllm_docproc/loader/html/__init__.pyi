from .flat import HTMLFlatLoader as HTMLFlatLoader
from .html_base_loader import HTMLBaseLoader as HTMLBaseLoader
from .nested import HTMLNestedLoader as HTMLNestedLoader

__all__ = ['HTMLBaseLoader', 'HTMLFlatLoader', 'HTMLNestedLoader']

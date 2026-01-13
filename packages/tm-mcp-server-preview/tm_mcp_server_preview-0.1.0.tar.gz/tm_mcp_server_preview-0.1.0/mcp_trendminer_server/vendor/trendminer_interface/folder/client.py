import abc
from .factory import FolderFactory


class FolderClient(abc.ABC):
    """Client for folder factory"""
    @property
    def folder(self):
        """Factory for creating and retrieving folders"""
        return FolderFactory(client=self)

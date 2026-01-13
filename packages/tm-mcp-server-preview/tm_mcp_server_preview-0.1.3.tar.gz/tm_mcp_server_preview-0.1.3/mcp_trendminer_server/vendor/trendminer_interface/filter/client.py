from .filter import FilterFactory


class FilterClient:
    """Filter client"""
    @property
    def filter(self):
        """Factory for filter objects

        Returns
        -------
        FilterFactory
        """
        return FilterFactory(client=self)

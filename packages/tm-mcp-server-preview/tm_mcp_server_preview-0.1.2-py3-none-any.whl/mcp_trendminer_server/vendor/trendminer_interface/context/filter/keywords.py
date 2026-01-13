from trendminer_interface import _input as ip
from trendminer_interface.base import FactoryBase
from trendminer_interface.context.filter.base import ContextFilterWithModeBase


class KeywordFilter(ContextFilterWithModeBase):
    """Filter on context item keywords"""
    filter_type = "KEYWORD_FILTER"

    def __init__(self, client, keywords, mode):
        super().__init__(client=client, mode=mode)
        self.keywords = keywords

    @property
    def keywords(self):
        """Context item keywords

        Returns
        -------
        keywords : list of str
            Keywords which must be present on the context items
        """

        return self._keywords

    @keywords.setter
    def keywords(self, keywords):
        self._keywords = [kw.lower() for kw in ip.any_list(keywords)]

    def _json(self):
        return {
            **super()._json(),
            "keywords": self.keywords,
        }


class KeywordFilterFactory(FactoryBase):
    """Factory for creating context item keyword filter"""
    tm_class = KeywordFilter

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        KeywordFilter
        """
        return self.tm_class(client=self.client, keywords=data.get("keywords"), mode=data.get("mode"))

    def __call__(self, keywords=None, mode=None):
        """Create new context item keywords filter

        Parameters
        ----------
        keywords : list of str, optional
            Keywords which must be present on the context items
        mode : str, optional
            Filter for "EMPTY" or "NON_EMPTY" description. When using mode, any given keywords are ignored.

        Returns
        -------
        KeywordFilter
            Filter on context item keywords
        """
        return self.tm_class(client=self.client, keywords=keywords, mode=mode)

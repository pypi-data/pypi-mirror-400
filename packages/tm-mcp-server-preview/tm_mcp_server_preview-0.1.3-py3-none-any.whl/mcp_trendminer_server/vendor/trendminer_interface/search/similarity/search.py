import pandas as pd
from trendminer_interface.base import ByFactory
from trendminer_interface.search.base import SearchBase, SearchFactoryBase, kwargs_to_class
from trendminer_interface.search.calculation import SearchCalculationFactory

from .query import SimilaritySearchQueryFactory


class SimilaritySearch(SearchBase):
    """Similarity search

    Similarity score of search result intervals are given in the 'score' column.

    Note that unlike the UX, it is possible to give separate weights per tag, though it is not recommended to do so, as
    loading the search in the UX will reset the weight settings to be equal.

    Attributes
    ----------
    queries : list of SimilaritySearchQuery
        Similarity search queries
    interval : pandas.Interval
        Focus chart interval used for the search
    threshold : float
        Similarity cutoff value (0-100)
    """
    content_type = "SIMILARITY_SEARCH"
    search_type = "similarity"
    queries = ByFactory(SimilaritySearchQueryFactory, "_list")

    def __init__(self,
                 client,
                 identifier,
                 identifier_complex,
                 name,
                 description,
                 parent,
                 owner,
                 last_modified,
                 version,
                 interval,
                 threshold,
                 queries,
                 calculations,
                 ):
        super().__init__(
            client=client,
            identifier=identifier,
            name=name,
            description=description,
            parent=parent,
            owner=owner,
            last_modified=last_modified,
            version=version,
            calculations=calculations,
            identifier_complex=identifier_complex,
        )

        self.interval = interval
        self.queries = queries
        self.threshold = threshold

    @property
    def tags(self):
        return [query.source for query in self.queries]

    def _json_definition(self):

        return {
            **super()._json_definition(),
            "queries": [query._json_search(self.interval) for query in self.queries],
            "parameters": {
                "detectionThreshold": self.threshold,
                "focusTimePeriod": {
                    "startDate": self.interval.left.isoformat(timespec="milliseconds"),
                    "endDate": self.interval.right.isoformat(timespec="milliseconds"),
                },
            },
        }

    def _json_data(self):
        return {
            "calculations": [calculation._json() for calculation in self.calculations],
            "cutOffPercentage": self.threshold,
            "originalEndDate": self.interval.right.isoformat(timespec="milliseconds"),
            "originalStartDate": self.interval.left.isoformat(timespec="milliseconds"),
            "tags": [query._json_save(self.interval) for query in self._queries]
        }

    @property
    def _empty_result_df(self):
        return super()._empty_result_df.assign(score=None).astype("float64")


class SimilaritySearchFactory(SearchFactoryBase):
    """Factory for generating and retrieving similarity searches"""
    tm_class = SimilaritySearch

    def __call__(
            self,
            queries,
            interval,
            threshold=70,
            name="New Search",
            description="",
            parent=None,
            calculations=None,
    ):
        """Instantiate a new similarity search

        Parameters
        ----------
        queries : list of SimilaritySearchQuery or list of Any
            Similarity search queries
        interval : pandas.Interval
            Focus chart interval used for the search
        threshold : float
            Similarity cutoff value (0-100)
        name : str
            Name of the search; only relevant when saving
        description : str
            Description of the search; only relevant when saving
        parent : Folder or Any
            Folder to save the search in
        calculations : list of SearchCalculation or Any
            Calculations to perform on the search

        Returns
        -------
        SimilaritySearch
        """
        return self.tm_class(
            client=self.client,
            identifier=None,
            identifier_complex=None,
            name=name,
            description=description,
            parent=parent,
            owner=None,
            last_modified=None,
            version=None,
            interval=interval,
            threshold=threshold,
            queries=queries,
            calculations=calculations,
        )

    @property
    def query(self):
        """Factory for similarity search queries"""
        return SimilaritySearchQueryFactory(client=self.client)

    def _json_data(self, data):
        """From json with full info"""
        return {
            "identifier_complex": data["data"]["id"],
            "calculations": [
                SearchCalculationFactory(client=self.client)._from_json(calc)
                for calc in data["data"]["calculations"]
            ],
            "queries": [
                SimilaritySearchQueryFactory(client=self.client)._from_json(tag)
                for tag in data["data"]["tags"]
            ],
            "threshold": data["data"]["cutOffPercentage"],
            "interval": pd.Interval(
                left=pd.Timestamp(data["data"]["originalStartDate"]).tz_convert(self.client.tz),
                right=pd.Timestamp(data["data"]["originalEndDate"]).tz_convert(self.client.tz),
                closed="both",
            ),
        }

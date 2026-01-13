import pandas as pd

from trendminer_interface.constants import SIMILARITY_SEARCH_TYPES, SIMILARITY_SEARCH_TYPE_MAPPING
from trendminer_interface.base import FactoryBase, ByFactory, HasOptions, AuthenticatableBase
from trendminer_interface.tag import TagFactory
from .weight import SimilaritySearchWeightFactory


class SimilaritySearchQuery(AuthenticatableBase):
    """A similarity search query

    Attributes
    ----------
    source : Tag
        The source tag holding the pattern we are searching
    target : Tag
        The tag that we are searching in for a similar pattern
    search_type : str
        - ABSOLUTE_VALUES: match by the tag values
        - SIGNAL_SHAPE: match by the changes in tag values (e.g. drop from 11 to 4 matches drop from 8 to 1)
    weights : list of SimilaritySearchWeight
        Weighted intervals assigned to the source tag
    """
    source = ByFactory(TagFactory)
    target = ByFactory(TagFactory)
    search_type = HasOptions(SIMILARITY_SEARCH_TYPES)
    weights = ByFactory(SimilaritySearchWeightFactory, method="_list")

    def __init__(self, client, source, target, search_type, weights):
        super().__init__(client=client)
        self.source = source
        self.target = target
        self.search_type = search_type
        self.weights = weights

    def _source_scale(self, interval):
        """Scale of the source tag

        Can be either set on the tag itself, or needs to be calculated from the focus interval of the similarity search

        Parameters
        ----------
        interval : pandas.Interval
            The focus interval of the Similarity search object

        Returns
        -------
        list of float
            [min, max] list giving the scale/range of the source tag
        """

        if self.source.scale is None:
            df = (
                pd.DataFrame(index=[interval])
                .interval.calculate(tag=self.source, operation="min", name="min")
                .interval.calculate(tag=self.source, operation="max", name="max")
            )
            min_val = df["min"][0]
            max_val = df["max"][0]

            # Equal values give errors. Subtracting/adding 1 to the range as the TrendMiner UX does.
            if min_val == max_val:
                min_val -= 1
                max_val += 1

            return [
                min_val,
                max_val,
            ]

        else:
            return self.source.scale

    def _json_search(self, interval):
        """Get json payload for executing a similarity search

        Parameters
        ----------
        interval : pandas.Interval
            The focus interval of the Similarity search object. Required for getting the tag scale.

        Returns
        -------
        dict
            Json payload for executing a similarity search

        """
        scale = self._source_scale(interval)
        return {
            "range": {
                "min": scale[0],
                "max": scale[1],
            },
            "searchType": self.search_type,
            "source": {
                "id": self.source.identifier,
                "shift": self.source.shift.total_seconds(),  # not rounded
                "name": self.source.name,
                "interpolationType": self.source._interpolation_payload_str_lower,
            },
            "target": {
                "id": self.target.identifier,
                "shift": self.target.shift.total_seconds(),  # not rounded
                "name": self.target.name,
                "interpolationType": self.target._interpolation_payload_str_lower,
            },
            "weights": [weight._json_search() for weight in self.weights],
        }

    def _json_save(self, interval):
        """Get json payload for saving a similarity search

        Parameters
        ----------
        interval : pandas.Interval
            The focus interval of the Similarity search object. Required for getting the tag scale.

        Returns
        -------
        dict
            Json payload for saving a similarity search

        """
        scale = self._source_scale(interval)
        return {
            "interpolationType": self.source._interpolation_payload_str_lower,
            "minScale": scale[0],
            "name": self.source.name,
            "range": scale[1]-scale[0],
            "shift": int(self.source.shift.total_seconds()),
            "searchType": SIMILARITY_SEARCH_TYPE_MAPPING[self.search_type],
            "searchIn": {
                "tagName": self.target.name,
                "shift": int(self.target.shift.total_seconds()),
                "interpolationType": self.target._interpolation_payload_str_lower,
            },
            "weights": [weight._json() for weight in self.weights],
        }

    def __repr__(self):
        if self.source.name == self.target.name:
            target_info = ""
        else:
            target_info = f"| {self.target.name} "
        return f'<< {self.__class__.__name__} | {self.source.name} {target_info}>>'


class SimilaritySearchQueryFactory(FactoryBase):
    tm_class = SimilaritySearchQuery

    def __call__(self, source, target=None, search_type="absolute values", weights=None):
        """Create a new similarity search query

        Parameters
        ----------
        source : Tag
            The source tag holding the pattern we are searching
        target : Tag, optional
            The tag that we are searching in for a similar pattern. Defaults to source tag.
        search_type : str
            - absolute values: match by the tag values
            - signal shape: match by the changes in tag values (e.g. drop from 11 to 4 matches drop from 8 to 1)
        weights : list of SimilaritySearchWeight
            Weighted intervals assigned to the source tag
        """
        return self.tm_class(
            client=self.client,
            source=source,
            target=target or source,
            search_type=search_type,
            weights=weights,
        )

    def _from_json(self, data):
        return self.tm_class(
            client=self.client,
            source=TagFactory(client=self.client)._from_json_similarity_search_source(data),
            target=TagFactory(client=self.client)._from_json_similarity_search_target(data["searchIn"]),
            weights=[SimilaritySearchWeightFactory(client=self.client)._from_json(w) for w in data.get("weights", [])],
            search_type={value: key for key, value in SIMILARITY_SEARCH_TYPE_MAPPING.items()}[data["searchType"]]
        )

    def from_tag(self, ref):
        """Generate a search query directly from  a tag

        Defaults to basic settings for all other aspects of the Similarity search query

        Parameters
        ----------
        ref : Tag or Any
            Tag to turn into a query

        Returns
        -------
        SimilaritySearchQuery
        """
        return self.tm_class(
            client=self.client,
            source=ref,
            target=ref,
            weights=None,
            search_type="ABSOLUTE_VALUES",
        )

    @property
    def _get_methods(self):
        return self.from_tag,

import abc
import pandas as pd

from .base import TagBuilderTagBase
from trendminer_interface.base import ByFactory, AsTimedelta, HasOptions, kwargs_to_class
from trendminer_interface.work import WorkOrganizerObjectFactoryBase
from trendminer_interface.tag import TagFactory
from trendminer_interface.constants import AGGREGATION_POSITIONS, AGGREGATION_OPTIONS


class AggregationClient(abc.ABC):
    """Client for aggregation tag factory"""

    @property
    def aggregation(self):
        """Factory for instantiating and retrieving aggregations"""
        return AggregationFactory(client=self)


class Aggregation(TagBuilderTagBase):
    """Tag builder aggregation tag

    Attributes
    ----------
    target : Tag
        The tag that is aggregated
    operator : str
        AVERAGE, MINIMUM, MAXIMUM, RANGE, DELTA, INTEGRAL_PER_DAY, INTEGRAL_PER_HOUR, INTEGRAL_PER_MINUTE, or
        INTEGRAL_PER_SECOND
    position : str
        Aggregation position
            - START: next x time
            - CENTER: last x/2 and next x/2 time
            - END: last x time
    window : pandas.Timedelta
        Aggregation window
    """
    content_type = "AGGREGATION"
    target = ByFactory(TagFactory)
    window = AsTimedelta()
    position = HasOptions(AGGREGATION_POSITIONS)
    operator = HasOptions(AGGREGATION_OPTIONS)

    def __init__(
            self,
            client,
            target,
            operator,
            position,
            window,
            name,
            description,
            identifier,
            parent,
            owner,
            last_modified,
            version,
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
        )

        self.target = target
        self.position = position
        self.window = window
        self.operator = operator

    def _json_data(self):
        return {
            "aggregationPosition": self.position,
            "aggregationWindow": round(self.window.total_seconds()),
            "interpolationType": self.target._interpolation_payload_str,
            "operator": self.operator,
            "timeSeriesDefinitionId": self.target.identifier,
            "timeSeriesName": self.target.name,
        }

    def _full_instance(self):
        return AggregationFactory(client=self.client).from_identifier(self.identifier)


class AggregationFactory(WorkOrganizerObjectFactoryBase):
    """Factory for creating and retrieving formula tags"""
    tm_class = Aggregation

    def __call__(self, target, operator, position, window, name, description="", parent=None):
        """Instantiate aggregation

        Parameters
        ----------
        target : Tag or Any
            The tag that is aggregated
        operator : str
            AVERAGE, MINIMUM, MAXIMUM, RANGE, DELTA, INTEGRAL_PER_DAY, INTEGRAL_PER_HOUR, INTEGRAL_PER_MINUTE, or
            INTEGRAL_PER_SECOND
        position : str
            START (forward), CENTER, or END (backward)
        window : pandas.Timedelta
            Aggregation window
        name : str
            Name of the aggregation and the resulting tag
        description : str
            Description of the aggregation and the resulting tag
        """
        return self.tm_class(
            client=self.client,
            target=target,
            operator=operator,
            position=position,
            window=window,
            name=name,
            description=description,
            identifier=None,
            parent=parent,
            owner=None,
            last_modified=None,
            version=None,
        )

    def _json_data(self, data):
        """Full enriched payload"""
        return {
            "target": TagFactory(client=self.client)._from_json_aggregation(data["data"]),
            "operator": data["data"]["operator"],
            "window": pd.Timedelta(seconds=data["data"]["aggregationWindow"]),
            "position": data["data"]["aggregationPosition"],
        }

import math
import pandas as pd
from trendminer_interface.base import SerializableBase, FactoryBase


# TODO: could weights be a DataFrame?
class SimilaritySearchWeight(SerializableBase):
    """Weighted periods used in similarity searches

    Attributes
    ----------
    interval : pandas.Interval
        The weighted interval
    weight : int
        The weight (1-5) assigned to the interval
    """

    def __init__(self, client, interval, weight):
        """"""
        super().__init__(client=client)
        self.interval = interval
        self.weight = weight

    def _json_search(self):
        return {
            "start": self.interval.left.isoformat(timespec="milliseconds"),
            "end": self.interval.right.isoformat(timespec="milliseconds"),
            "weight": round(3**self.weight), # needs to be multiplied by 3 for some unknown reason
        }

    def _json(self):
        # These timestamps cannot be regular isoformat, since the sql varchar column in which they are stored is limited
        # to 24 characters
        return {
            "startDate": self.interval.left.astimezone("UTC").strftime('%Y-%m-%dT%H:%M:%SZ'),
            "endDate": self.interval.right.astimezone("UTC").strftime('%Y-%m-%dT%H:%M:%SZ'),
            "weight": round(3**self.weight)
        }


class SimilaritySearchWeightFactory(FactoryBase):
    """Factory for creating similarity search weights"""
    tm_class = SimilaritySearchWeight

    def __call__(self, interval, weight):
        """Create a new similarity search weight

        Parameters
        ----------
        interval : pandas.Interval
            Interval for which the weight is assigned
        weight : int
            Value from 1 to 5 giving the additional weight to this interval

        Returns
        -------
        SimilaritySearchWeight
        """
        return self.tm_class(
            client=self.client,
            interval=interval,
            weight=weight,
        )

    def from_tuple(self, ref):
        """Generate list of weights from a list of tuples

        Parameters
        ----------
        ref : tuple
            (Interval, int) input.

        Returns
        -------
        SimilaritySearchWeight
        """
        return self.__call__(interval=ref[0], weight=ref[1])

    def _from_json(self, data):
        """Get weight from json structure

        Parameters
        ----------
        data : dict
            Similarity searh weight in json format

        Returns
        -------
        SimilaritySearchWeight
        """
        return self.tm_class(
            client=self.client,
            interval=pd.Interval(
                left=pd.Timestamp(data["startDate"]).tz_convert(self.client.tz),
                right=pd.Timestamp(data["endDate"]).tz_convert(self.client.tz),
                closed="both",
            ),
            weight=round(math.log(data["weight"], 3))
        )

    @property
    def _get_methods(self):
        return self.from_tuple,

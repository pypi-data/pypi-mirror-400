import pandas as pd

from trendminer_interface.base import FactoryBase

from .base import FilterPropertiesBase


class ManualFilterProperties(FilterPropertiesBase):
    # TODO: allow DataFrame and Series input too
    """Properties of a manual filter created from a list of intervals

    Attributes
    ----------
    intervals : pandas.IntervalIndex
        Filtered-out intervals
    """
    properties_type = "MANUAL"

    def __init__(self, client, intervals):
        super().__init__(client=client)
        self.intervals = intervals

    def _json_properties(self):
        return {
            "periods": [
                {
                    "start": interval.left.isoformat(timespec="milliseconds"),
                    "end": interval.right.isoformat(timespec="milliseconds"),
                } for interval in self.intervals
            ]
        }


class ManualFilterPropertiesFactory(FactoryBase):
    """Factory for retrieving manual filter properties"""
    tm_class = ManualFilterProperties

    def _from_json(self, data):
        df = (
            pd.DataFrame(data["properties"]["periods"])
            .assign(
                start=lambda df: pd.to_datetime(df["start"]).dt.tz_convert(self.client.tz),
                end=lambda df: pd.to_datetime(df["end"]).dt.tz_convert(self.client.tz),
            )
        )

        # TODO: does the name of the IntervalIndex matter?
        intervals = pd.IntervalIndex.from_arrays(
            left=df["start"], right=df["end"], closed="both",
        )

        return self.tm_class(client=self.client, intervals=intervals)

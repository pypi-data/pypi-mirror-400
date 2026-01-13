import pandas as pd
from trendminer_interface.base import FactoryBase, SerializableBase
from trendminer_interface import _input as ip
from trendminer_interface.constants import LINE_STYLES


class FingerprintLayer(SerializableBase):
    # TODO: docstring

    def __init__(
            self,
            client,
            base,
            interval,
            name,
            line_style,
            hidden_references,
    ):
        super().__init__(client=client)
        self.base = base
        self.interval = interval
        self.name = name
        self.line_style = line_style
        self.hidden_references = hidden_references

    @property
    def line_style(self):
        if self.base:
            return "SOLID"
        return self._line_style if self._line_style != "SOLID" else "DASHED"

    @line_style.setter
    @ip.options(LINE_STYLES)
    def line_style(self, line_style):
        self._line_style = line_style

    def _json(self):
        return {
            "base": self.base,
            "name": self.name,
            "properties": {
                "lineStyle": self.line_style,
                "hiddenDataReferences": self.hidden_references,
            },
            "timePeriodStart": self.interval.left.isoformat(timespec="milliseconds"),
            "timePeriodEnd": self.interval.right.isoformat(timespec="milliseconds"),
        }


class FingerprintLayerFactory(FactoryBase):
    tm_class = FingerprintLayer

    @property
    def _get_methods(self):
        return self.from_interval,

    def from_interval(self, interval):
        """Create a FingerprintLayer from a given Interval

        Intended to convert list of intervals into layers when the user creates a view.
        Layer will not be base by default, and have the "DASHED" linestyle.

        Parameters
        ----------
        interval : pandas.Interval
            Interval to be turned into a layer
        """
        return self.tm_class(
            client=self.client,
            base=False,
            interval=interval,
            name="",
            line_style="DASHED",
            hidden_references=[],
        )

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        FingerprintLayer
        """
        return self.tm_class(
            client=self.client,
            base=data["base"],
            interval=pd.Interval(
                left=pd.Timestamp(data["timePeriodStart"]).tz_convert(self.client.tz),
                right=pd.Timestamp(data["timePeriodEnd"]).tz_convert(self.client.tz),
                closed="both",
            ),
            name=data["name"],
            line_style=data["properties"]["lineStyle"],
            hidden_references=data["properties"]["hiddenDataReferences"],
        )

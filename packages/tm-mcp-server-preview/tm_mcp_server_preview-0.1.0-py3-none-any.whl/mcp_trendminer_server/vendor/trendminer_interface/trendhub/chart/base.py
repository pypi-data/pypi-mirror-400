import abc
from trendminer_interface.base import SerializableBase


class ChartingPropertiesBase(SerializableBase, abc.ABC):
    """Charting Properties base class

    Attributes
    ----------
    locked : bool
        Whether the chart timeframe is locked
    y_axis_visibility : bool
        Whether the y-axes of the tags are visualized
    """
    chart_type = abc.abstractmethod(lambda: None)

    def __init__(self, client, locked, y_axis_visibility):
        super().__init__(client=client)
        self.locked = locked
        self.y_axis_visibility = y_axis_visibility

    @abc.abstractmethod
    def _json_settings(self):
        pass

    def _json(self):
        return {
            "chartType": self.chart_type,
            "chartSettings": self._json_settings(),
            "focusTimeSpanLocked": self.locked,
            "yAxisVisibility": self.y_axis_visibility,
        }

    def __repr__(self):
        return f"<< {self.__class__.__name__} >>"

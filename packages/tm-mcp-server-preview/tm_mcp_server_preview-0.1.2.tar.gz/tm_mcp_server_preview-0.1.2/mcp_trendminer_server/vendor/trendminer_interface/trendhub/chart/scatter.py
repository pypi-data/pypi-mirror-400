from .base import ChartingPropertiesBase
from trendminer_interface.base import FactoryBase


class ScatterChartProperties(ChartingPropertiesBase):
    """Scatter chart configuration

    Attributes
    ----------
    grid : bool
        Whether gridlines are shown
    histogram : bool
        Whether a histogram is displayed
    colored : bool
        Whether points are colored according to their timestamps
    correlation: bool
        Whether tag correlations are given
    mode : dict
        Scatter mode configuration as raw json. Not intended to be edited via the sdk at this point.
    """
    chart_type = "SCATTER_CHART"

    def __init__(self, client, locked, y_axis_visibility, grid, histogram, colored, correlation, mode):
        super().__init__(client=client, locked=locked, y_axis_visibility=y_axis_visibility)
        self.grid = grid
        self.histogram = histogram
        self.colored = colored,
        self.correlation = correlation,
        self.mode = mode

    def _json_settings(self):
        return {
            "scatterGridLines": self.grid,
            "scatterHistogram": self.histogram,
            "scatterColoredPoints": self.colored,
            "scatterCorrelation": self.correlation,
            "scatterMode": self.mode
        }


class ScatterChartPropertiesFactory(FactoryBase):
    """Factory for creating scatter chart properties instances"""
    tm_class = ScatterChartProperties

    def __init__(self, client):
        super().__init__(client=client)

    def __call__(self, locked=True, grid=False, histogram=True, colored=True, correlation=False):
        """Create new scatter chart configuration

        Attributes
        ----------
        locked : bool, default True
            Whether the focus chart timespan is locked
        grid : bool, default False
            Whether gridlines are shown
        histogram : bool, default True
            Whether a histogram is displayed
        colored : bool, default True
            Whether points are colored according to their timestamps
        correlation: bool, default False
            Whether tag correlations are given
        """
        return self.tm_class(
            client=self.client,
            locked=locked,
            y_axis_visibility={},
            grid=grid,
            histogram=histogram,
            colored=colored,
            correlation=correlation,
            mode={"type": "MULTI"},
        )

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        ScatterChartProperties
        """
        return self.tm_class(
            client=self.client,
            locked=data["focusTimeSpanLocked"],
            y_axis_visibility=data["yAxisVisibility"],
            grid=data["chartSettings"]["stackedGridLines"],
            histogram=data["chartSettings"]["scatterHistogram"],
            colored=data["chartSettings"]["scatterColoredPoints"],
            correlation=data["chartSettings"]["scatterCorrelation"],
            mode=data["chartSettings"]["scatterMode"],
        )

    @property
    def _get_methods(self):
        return ()

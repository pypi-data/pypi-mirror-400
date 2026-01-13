from .base import ChartingPropertiesBase
from trendminer_interface.base import FactoryBase


class TrendChartProperties(ChartingPropertiesBase):
    """Trend chart configuration

    Attributes
    ----------
    grid : bool
        Whether gridlines are shown
    filling : bool
        Whether the area under the trendlines is shaded
    context : bool
        Whether context items are displayed on the chart
    """
    chart_type = "TREND_CHART"

    def __init__(self, client, locked, y_axis_visibility, grid, filling, context):
        super().__init__(client=client, locked=locked, y_axis_visibility=y_axis_visibility)
        self.grid = grid
        self.filling = filling
        self.context = context

    def _json_settings(self):
        return {
            "trendGridLines": self.grid,
            "trendFilling": self.filling,
            "trendContextItems": self.context,
        }


class TrendChartPropertiesFactory(FactoryBase):
    """Factory for creating trend chart properties instances"""
    tm_class = TrendChartProperties

    def __init__(self, client):
        super().__init__(client=client)

    def __call__(self, locked=True, grid=False, filling=False, context=False):
        """Create new trend chart configuration

        Attributes
        ----------
        locked : bool, default True
            Whether the focus chart timespan is locked
        grid : bool, default False
            Whether gridlines are shown
        filling : bool, False
            Whether the area under the trendlines is shaded
        context : bool, False
            Whether context items are displayed on the chart
        """
        return self.tm_class(
            client=self.client,
            locked=locked,
            y_axis_visibility={},
            grid=grid,
            filling=filling,
            context=context
        )

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        TrendChartProperties
        """
        return self.tm_class(
            client=self.client,
            locked=data["focusTimeSpanLocked"],
            y_axis_visibility=data["yAxisVisibility"],
            grid=data["chartSettings"]["trendGridLines"],
            filling=data["chartSettings"]["trendFilling"],
            context=data["chartSettings"]["trendContextItems"]
        )

    @property
    def _get_methods(self):
        return ()

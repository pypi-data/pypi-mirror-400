from trendminer_interface.base import FactoryBase
from .scatter import ScatterChartPropertiesFactory
from .stacked import StackedChartPropertiesFactory
from .trend import TrendChartPropertiesFactory
from .base import ChartingPropertiesBase


factory_dict = {factory.tm_class.chart_type: factory for factory in [
    ScatterChartPropertiesFactory,
    StackedChartPropertiesFactory,
    TrendChartPropertiesFactory,
]}


# TODO: should be MultiFactory
class ChartingPropertiesFactory(FactoryBase):
    """Parent factory for charting properties"""
    tm_class = ChartingPropertiesBase

    @property
    def scatter(self):
        """Scatter chart properties factory

        Returns
        -------
        ScatterChartPropertiesFactory
        """
        return ScatterChartPropertiesFactory(client=self.client)

    @property
    def stacked(self):
        """Stacked chart properties factory

        Returns
        -------
        StackedChartPropertiesFactory
        """
        return StackedChartPropertiesFactory(client=self.client)

    @property
    def trend(self):
        """Trend view properties factory

        Returns
        -------
        TrendChartPropertiesFactory
        """
        return TrendChartPropertiesFactory(client=self.client)

    @property
    def _get_methods(self):
        return ()

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        Any
        """
        return factory_dict[data["chartType"]](client=self.client)._from_json(data)

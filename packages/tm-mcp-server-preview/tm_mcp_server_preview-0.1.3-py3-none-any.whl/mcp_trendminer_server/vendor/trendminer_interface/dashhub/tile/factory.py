from trendminer_interface.base import MultiFactoryBase, to_subfactory
from .trend import TrendHubViewTileFactory
from .context import CounterTileFactory, GanttTileFactory, TableTileFactory
from .monitor import MonitorTileFactory
from .external import ExternalContentTileFactory
from .value import CurrentValueTileFactory
from .text import TextTileFactory


class TileMultiFactory(MultiFactoryBase):
    """Factory for creating dashboard tile instances out of json responses"""

    # Class is determined not only by visualization type, but also by display mode; use tuple key
    factories = {
        (factory.tm_class.visualization_type, factory.tm_class.display_mode): factory
        for factory in [
            TrendHubViewTileFactory,
            CounterTileFactory,
            GanttTileFactory,
            TableTileFactory,
            MonitorTileFactory,
            ExternalContentTileFactory,
            CurrentValueTileFactory,
            TextTileFactory,
        ]
    }

    @to_subfactory
    def _from_json(self, data):
        return data["visualizationType"], data["configuration"].get("displayMode")

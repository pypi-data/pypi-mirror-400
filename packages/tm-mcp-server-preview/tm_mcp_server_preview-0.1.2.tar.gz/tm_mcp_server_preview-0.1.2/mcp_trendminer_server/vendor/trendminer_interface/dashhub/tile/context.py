import abc

from .base import TileBase, TileFactoryBase
from trendminer_interface.context import ContextHubViewFactory


class ContextTileBase(TileBase, abc.ABC):
    """ContextHub tile base class

    Tile content is a ContextHub view
    """
    visualization_type = "CONTEXT_HUB_VIEW"
    display_mode = None
    min_size = (1, 2)

    def __init__(self, client, content, x, y, title, refresh_rate, rows, cols,
                 display_mode=None, show_colored_points_legend=None, show_time_frame=None, show_title=None):
        super().__init__(client, content, x, y, title, refresh_rate, rows, cols)
        self.display_mode = display_mode
        self.show_colored_points_legend = show_colored_points_legend
        self.show_time_frame = show_time_frame
        self.show_title = show_title

    def _get_content(self, content):
        """Convert content into ContextHub view

        Attributes
        ----------
        content : ContextHubView or Any

        Returns
        -------
        ContextHub view
        """
        return ContextHubViewFactory(client=self.client)._get(content)

    def _json_configuration(self):
        return {
            "displayMode": self.display_mode,
            "configurationType": self.visualization_type,
            "contextViewId": self.content.identifier,
            "showColoredPointsLegend": self.show_colored_points_legend,
            "showTimeFrame": self.show_time_frame,
            "showTitle": self.show_title,
        }


class ContextTileFactoryBase(TileFactoryBase, abc.ABC):
    """ContextHub tile parent class"""
    tm_class = ContextTileBase

    def _from_json(self, data):
        config = data["configuration"]
        return self.tm_class(
            client=self.client,
            content=self._from_json_content(config),
            x=data["x"],
            y=data["y"],
            title=data["title"],
            refresh_rate=data["refreshRate"],
            rows=data["rows"],
            cols=data["cols"],
            display_mode=config.get("displayMode"),
            show_colored_points_legend=config.get("showColoredPointsLegend"),
            show_time_frame=config.get("showTimeFrame"),
            show_title=config.get("showTitle"),
        )

    def _from_json_content(self, data):
        return ContextHubViewFactory(client=self.client)._from_json_identifier_only(data["contextViewId"])


class CounterTile(ContextTileBase):
    """ContextHub view counter tile"""
    display_mode = "COUNT"


class CounterTileFactory(ContextTileFactoryBase):
    """ContextHub view counter tile factory"""
    tm_class = CounterTile


class TableTile(ContextTileBase):
    """ContextHub view table tile"""
    display_mode = "TABLE"


class TableTileFactory(ContextTileFactoryBase):
    """ContextHub view table tile factory"""
    tm_class = TableTile


class GanttTile(ContextTileBase):
    """ContextHub view Gantt tile"""
    display_mode = "GANTT"


class GanttTileFactory(ContextTileFactoryBase):
    """ContextHub view Gantt tile factory"""
    tm_class = GanttTile

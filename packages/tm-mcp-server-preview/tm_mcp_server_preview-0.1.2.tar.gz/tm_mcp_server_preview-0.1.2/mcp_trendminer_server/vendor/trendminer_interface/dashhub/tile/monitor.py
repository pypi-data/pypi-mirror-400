from trendminer_interface.constants import MONITOR_TILE_OPTIONS
from trendminer_interface.base import HasOptions
from trendminer_interface.monitor import MonitorFactory

from .base import TileBase, TileFactoryBase


class MonitorTile(TileBase):
    """Monitor state dashboard tile

    Attributes
    ----------
    active_icon : str
        Icon when the monitor is triggered. Options:
        "snowflake", "flame", "bucket", "ruler", "flask", "information", "waterdrops", "flow--line", "waves",
        "circle-success", "person", "arrows--round", "cracked", "wheelbarrow", "alert--circle", "clipboard", "wrench",
        "warning", "trending--down", "spoon", "wrench", "file--check"
    inactive_icon : str
        Icon when the monitor is not triggered. Options:
        "snowflake", "flame", "bucket", "ruler", "flask", "information", "waterdrops", "flow--line", "waves",
        "circle-success", "person", "arrows--round", "cracked", "wheelbarrow", "alert--circle", "clipboard", "wrench",
        "warning", "trending--down", "spoon", "wrench", "file--check"
    active_color : str
        Color when the monitor is triggered (e.g., "#FF0010")
    inactive_color : str
        Color when the monitor is not triggered (e.g., "#2BCE48")
    active_text : str
        Text displayed when the monitor is triggered
    inactive_text : str
        Text displayed when the monitor is not triggered
    """
    visualization_type = "ALERT"
    min_size = (1, 2)

    active_icon = HasOptions(MONITOR_TILE_OPTIONS)
    inactive_icon = HasOptions(MONITOR_TILE_OPTIONS)

    def __init__(
            self,
            client,
            content,
            active_color,
            active_text,
            active_icon,
            inactive_color,
            inactive_text,
            inactive_icon,
            x,
            y,
            title,
            refresh_rate,
            rows,
            cols,
            fill_background=None,
            show_title=None,
            type_=None,
    ):
        super().__init__(
            client=client,
            content=content,
            x=x,
            y=y,
            title=title,
            refresh_rate=refresh_rate,
            rows=rows,
            cols=cols,
        )
        self.active_color = active_color
        self.active_text = active_text
        self.active_icon = active_icon
        self.inactive_color = inactive_color
        self.inactive_text = inactive_text
        self.inactive_icon = inactive_icon
        self.fill_background = fill_background
        self.show_title = show_title
        self.type_ = type_

    def _get_content(self, content):
        return MonitorFactory(client=self.client)._get(content)

    def _json_configuration(self):
        return {
            "configurationType": self.visualization_type,
            "identifier": None,
            "monitorId": int(self.content.identifier),
            "stateDefinitions": {
                "TRIGGERED": {
                    "color": self.active_color.lower(),  # tile color is in lower case
                    "definition": self.active_text,
                    "icon": self.active_icon,
                },
                "NOT_TRIGGERED": {
                    "color": self.inactive_color.lower(),  # tile color is in lower case
                    "definition": self.inactive_text,
                    "icon": self.inactive_icon,
                }
            },
            "fillBackground": self.fill_background,
            "showTitle": self.show_title,
            "type": self.type_,
        }


class MonitorTileFactory(TileFactoryBase):
    """Factory for creating and retrieving monitor tiles"""
    tm_class = MonitorTile

    def __call__(
        self,
        content,
        x,
        y,
        rows=4,
        cols=4,
        title="",
        refresh_rate="5m",
        active_color="#FF0010",
        active_text="",
        active_icon="alert--circle",
        inactive_color="#2BCE48",
        inactive_text="",
        inactive_icon="circle-success",
        fill_background=None,
        show_title=None,
        type_=None,
    ):
        """Instantiate new monitor tile

        Parameters
        ----------
        x : int
            Horizontal position of the tile. Leftmost column is 0.
        y : int
            Vertical position of the tile. Top row is 0.
        title : str, default ""
            Tile title
        rows : int, default 4
            Number of rows (vertical) taken up by the tile. Tile has a minimal size defined by class attribute `min_size`.
        cols : int, default 4
            Number of columns (horizontal) taken up by the tile. Tile has a minimal size defined by class attribute
            `min_size`.
        refresh_rate : pandas.Timedelta, default '5m'
            How often the tile is refreshed if the dashboard is live.
        active_icon : str, default 'alert--circle'
            Icon when the monitor is triggered. Options:
            "snowflake", "flame", "bucket", "ruler", "flask", "information", "waterdrops", "flow--line", "waves",
            "circle-success", "person", "arrows--round", "cracked", "wheelbarrow", "alert--circle", "clipboard",
            "wrench", "warning", "trending--down", "spoon", "wrench", "file--check"
        inactive_icon : str, default 'circle--success'
            Icon when the monitor is not triggered. Options:
            "snowflake", "flame", "bucket", "ruler", "flask", "information", "waterdrops", "flow--line", "waves",
            "circle-success", "person", "arrows--round", "cracked", "wheelbarrow", "alert--circle", "clipboard",
            "wrench", "warning", "trending--down", "spoon", "wrench", "file--check"
        active_color : str, default '#FF0010'
            Color when the monitor is triggered
        inactive_color : str, default '#2BCE48'
            Color when the monitor is not triggered
        active_text : str, default ''
            Text displayed when the monitor is triggered
        inactive_text : str, default ''
            Text displayed when the monitor is not triggered
        """
        return self.tm_class(
            client=self.client,
            content=content,
            active_color=active_color,
            active_text=active_text,
            active_icon=active_icon,
            inactive_color=inactive_color,
            inactive_text=inactive_text,
            inactive_icon=inactive_icon,
            x=x,
            y=y,
            title=title,
            refresh_rate=refresh_rate,
            rows=rows,
            cols=cols,
            fill_background=fill_background,
            show_title=show_title,
            type_=type_,
        )

    def _from_json_content(self, data):
        return MonitorFactory(client=self.client)._from_json_identifier_only(data["monitorId"])

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        MonitorTile
        """
        config = data["configuration"]
        return self.tm_class(
            client=self.client,
            content=self._from_json_content(config),
            active_color=config["stateDefinitions"]["TRIGGERED"]["color"].upper(),  # json is in lower case
            active_text=config["stateDefinitions"]["TRIGGERED"]["definition"],
            active_icon=config["stateDefinitions"]["TRIGGERED"]["icon"],
            inactive_color=config["stateDefinitions"]["NOT_TRIGGERED"]["color"].upper(),  # json is in lower case
            inactive_text=config["stateDefinitions"]["NOT_TRIGGERED"]["definition"],
            inactive_icon=config["stateDefinitions"]["NOT_TRIGGERED"]["icon"],
            x=data["x"],
            y=data["y"],
            title=data["title"],
            refresh_rate=data["refreshRate"],
            rows=data["rows"],
            cols=data["cols"],
            fill_background=config.get("fillBackground"),
            show_title=config.get("showTitle"),
            type_=config.get("type"),
        )

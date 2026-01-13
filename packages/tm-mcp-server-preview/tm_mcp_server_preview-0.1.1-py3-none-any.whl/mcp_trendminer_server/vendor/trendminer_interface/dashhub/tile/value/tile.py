import math
import pandas as pd

from trendminer_interface.dashhub.tile.base import TileBase, TileFactoryBase
from .condition import CurrentValueConditionFactory
from .entry import CurrentValueEntryFactory


def tile_timespan_string(td):
    """Convert Timedelta into custom string required for value tile duration

    Parameters
    ----------
    td : pd.Timedelta or None
         Duration as a Timedelta, defaults to 1h if input is None

    Returns
    -------
    str
        Duration in custom string format used for current value tile, e.g. '010000'
    """
    if td is None:
        return "010000"  # default value
    hours = math.floor(td.total_seconds()/3600)
    minutes = math.floor((td.total_seconds()-(hours*3600))/60)
    seconds = int(td.total_seconds()-hours*3600-minutes*60)
    return f"{hours:02}{minutes:02}{seconds:02}"


def tile_timespan_timedelta(s):
    """Convert value tile duration string to Timedelta

    Parameters
    ----------
    s : str
        Duration in string format custom to current value tile, e.g. '010000'

    Returns
    -------
    pandas.Timedelta
        Duration
    """
    return pd.Timedelta(
        hours=int(s[0:2]),
        minutes=int(s[2:4]),
        seconds=int(s[4:6]),
    )


class CurrentValueTile(TileBase):
    """Current value dashboard tile

    Attributes
    ----------
    graph : bool
        Trend shown for the tags
    accuracy : float or None
        Value accuracy (e.g., 0.1, 0.01) for the values displayed
    timestamp : bool
        Show the timestamp of the latest datapoint (for which the value is displayed)

    """
    visualization_type = "VALUE"
    min_size = (1, 2)

    def __init__(self,
                 client,
                 content,
                 graph,
                 graph_duration,
                 accuracy,
                 timestamp,
                 x,
                 y,
                 title,
                 refresh_rate,
                 rows,
                 cols,
                 fill_background=None,
                 show_component_names=None,
                 show_title=None,
                 use_chart_alias=None):
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

        self.graph = graph
        self.graph_duration = graph_duration
        self.accuracy = accuracy
        self.timestamp = timestamp
        self.fill_background = fill_background
        self.show_component_names = show_component_names
        self.show_title = show_title
        self.use_chart_alias = use_chart_alias

    @property
    def graph_duration(self):
        """Range of the trend shown (if `graph=True`)

        Returns
        -------
        pd.Timedelta
            Range of the trend shown on the tile
        """
        return self._graph_duration

    @graph_duration.setter
    def graph_duration(self, duration):
        duration = pd.Timedelta(duration)
        if duration.total_seconds() > 86400:
            raise ValueError("Maximal graph length is 24h")
        self._graph_duration = duration

    def _get_content(self, content):
        return CurrentValueEntryFactory(client=self.client)._list(content)

    def _json_configuration(self):
        return {
            "components": [entry._json() for entry in self.content],
            "configurationType": self.visualization_type,
            "identifier": None,
            "miniGraph": {
                "show": self.graph,
                "timeSpan": tile_timespan_string(self.graph_duration)
            },
            "accuracy": self.accuracy,
            "showTimestamp": self.timestamp,
            "fillBackground": self.fill_background,
            "showComponentNames": self.show_component_names,
            "showTitle": self.show_title,
            "useChartAlias": self.use_chart_alias,
        }


class CurrentValueTileFactory(TileFactoryBase):
    tm_class = CurrentValueTile

    def __call__(self,
                 content,
                 x,
                 y,
                 rows=3,
                 cols=2,
                 title="",
                 refresh_rate="1m",
                 graph=True,
                 graph_duration="1h",
                 accuracy=None,
                 timestamp=True,
                 fill_background=None,
                 show_component_names=None,
                 show_title=None,
                 use_chart_alias=None):
        """Instantiate new current value tile

        Parameters
        ----------
        content : list
            Tags and/or attributes to display
        x : int
            x-position on the dashboard grid
        y : int
            y-position on the dashboard grid
        rows : int
            Number of rows occupied on the dashboard grid
        cols : int
            Number of columns occupied on the dashboard grid
        title : str, optional
            Tile title
        refresh_rate : pandas.Timedelta, default '1m'
            How often the tile is refreshed when the dashboard is live
        graph : bool, default True
            If miniature trends are displayed
        graph_duration : pandas.Timedelta, default '1h'
            The length fo the displayed graphs (if `graph=True`)
        accuracy : float or None, default None
            Value accuracy (e.g., 0.1, 0.01) for the values displayed
        timestamp : bool, default True
            If the timestamp of the latest point (which is displayed) is given as additional information
        """
        return self.tm_class(client=self.client,
                             content=content,
                             x=x,
                             y=y,
                             title=title,
                             refresh_rate=refresh_rate,
                             rows=rows,
                             cols=cols,
                             graph=graph,
                             graph_duration=graph_duration,
                             accuracy=accuracy,
                             timestamp=timestamp,
                             fill_background=fill_background,
                             show_component_names=show_component_names,
                             show_title=show_title,
                             use_chart_alias=use_chart_alias
                             )

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        CurrentValueTile
        """
        config = data["configuration"]
        return self.tm_class(
            client=self.client,
            content=[
                CurrentValueEntryFactory(client=self.client)._from_json(entry)
                for entry in config["components"]
            ],
            graph=config["miniGraph"]["show"],
            graph_duration=tile_timespan_timedelta(config["miniGraph"]["timeSpan"]),
            accuracy=config.get("accuracy"),
            timestamp=config["showTimestamp"],
            x=data["x"],
            y=data["y"],
            title=data["title"],
            refresh_rate=data["refreshRate"],
            rows=data["rows"],
            cols=data["cols"],
            fill_background=config.get("fillBackground"),
            show_component_names=config.get("showComponentNames"),
            show_title=config.get("showTitle"),
            use_chart_alias=config.get("useChartAlias"),
        )

    @property
    def condition(self):
        return CurrentValueConditionFactory(client=self.client)

    @property
    def entry(self):
        return CurrentValueEntryFactory(client=self.client)

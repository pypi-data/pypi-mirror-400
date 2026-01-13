import abc
import pandas as pd
from trendminer_interface.base import SerializableBase, FactoryBase, AsTimedelta


class TileBase(SerializableBase, abc.ABC):
    """DashHub Tile base class

    Attributes
    ----------
    title : str
        Tile title
    rows : int
        Number of rows (vertical) taken up by the tile. Tile has a minimal size defined by class attribute `min_size`.
    cols : int
        Number of columns (horizontal) taken up by the tile. Tile has a minimal size defined by class attribute
        `min_size`.
    x : int
        Horizontal position of the tile. Leftmost column is 0.
    y : int
        Vertical position of the tile. Top row is 0.
    refresh_rate : pandas.Timedelta
        How often the tile is refreshed if the dashboard is live.
    """
    visualization_type = abc.abstractmethod(lambda: None)
    display_mode = None
    min_size = abc.abstractmethod(lambda: None)
    refresh_rate = AsTimedelta()

    def __init__(
            self,
            client,
            content,
            x,
            y,
            title,
            refresh_rate,
            rows,
            cols,
    ):
        super().__init__(client=client)
        self.content = content
        self.title = title
        self.rows = rows
        self.cols = cols
        self.x = x
        self.y = y
        self.refresh_rate = refresh_rate

    @property
    def content(self):
        """Underlying TrendMiner object(s).

        Depends on tile type. Content is managed through a setter with the `_get_content` method

        Returns
        -------
        content : Any
        """
        return self._content

    @content.setter
    def content(self, content):
        self._content = self._get_content(content)

    def _get_content(self, content):
        """Make sure underlying content is of the correct type

        Setter for `content` property runs through `_get_content`.

        Attributes
        ----------
        content : Any
            Content input. Must be convertible into content type matching the tile type.

        Returns
        -------
        content : Any
            Tile content in matching the tile type
        """
        return content

    @abc.abstractmethod
    def _json_configuration(self):
        pass

    def _json(self):
        return {
            "cols": self.cols,
            "configuration": self._json_configuration(),
            "refreshRate": int(self.refresh_rate.total_seconds()),
            "rows": self.rows,
            "title": self.title,
            "visualizationType": self.visualization_type,
            "x": self.x,
            "y": self.y,
        }


class TileFactoryBase(FactoryBase, abc.ABC):
    """Base class for DashHub tile factories"""
    tm_class = TileBase

    def __call__(self, content, x, y, rows=4, cols=4, title="", refresh_rate="5m"):
        """Create new tile

        Parameters
        ----------
        content : Any
            Underlying tile content
        x : int
            Horizontal position of the tile. Leftmost column is 0.
        y : int
            Vertical position of the tile. Top row is 0.
        title : str, default ''
            Tile title
        rows : int, default 4
            Number of rows (vertical) taken up by the tile. Minimal size is dependent on the tile type.
        cols : int, default 4
            Number of columns (horizontal) taken up by the tile. Minimal size is dependent on the tile type.
        refresh_rate : pandas.Timedelta or Any, default '5m'
            How often the tile is refreshed if the dashboard is live.
        """
        if (rows < self.tm_class.min_size[0]) or (cols < self.tm_class.min_size[1]):
            raise ValueError(f"Minimal size for {self.tm_class.visualization_type} tile is {self.tm_class.min_size}")
        return self.tm_class(
            client=self.client,
            content=content,
            x=x,
            y=y,
            title=title,
            refresh_rate=refresh_rate,
            rows=rows,
            cols=cols,
        )

    def _from_json_content(self, data):
        return data

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
        return self.tm_class(
            client=self.client,
            content=self._from_json_content(data["configuration"]),
            x=data["x"],
            y=data["y"],
            title=data["title"],
            refresh_rate=pd.Timedelta(seconds=data["refreshRate"]),
            rows=data["rows"],
            cols=data["cols"],
            )

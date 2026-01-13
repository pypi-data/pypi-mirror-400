from .base import TileBase, TileFactoryBase


class TextTile(TileBase):
    """External content dashboard tile"""
    visualization_type = "RICH_TEXT"
    min_size = (1, 1)

    def __init__(self, client, content, x, y, title, refresh_rate, rows, cols, show_title=None):
        super().__init__(client, content, x, y, title, refresh_rate, rows, cols)
        self.show_title = show_title

    def _json_configuration(self):
        return {
            "configurationType": self.visualization_type,
            "content": self.content,
            "showTitle": self.show_title,
        }


class TextTileFactory(TileFactoryBase):
    """Factory for creating external conten dahboard tiles"""
    tm_class = TextTile

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
            show_title=config.get("showTitle"),
        )

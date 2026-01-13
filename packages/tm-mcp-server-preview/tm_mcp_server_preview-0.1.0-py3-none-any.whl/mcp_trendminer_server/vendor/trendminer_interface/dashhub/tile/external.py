from .base import TileBase, TileFactoryBase


class ExternalContentTile(TileBase):
    """External content dashboard tile"""
    visualization_type = "EXTERNAL_CONTENT"
    min_size = (1, 2)

    def __init__(self, client, content, x, y, title, refresh_rate, rows, cols, show_title=None):
        super().__init__(client, content, x, y, title, refresh_rate, rows, cols)
        self.show_title = show_title

    def _json_configuration(self):
        return {
            "url": self.content,
            "showTitle": self.show_title,
        }


class ExternalContentTileFactory(TileFactoryBase):
    """Factory for creating external content dashboard tiles"""
    tm_class = ExternalContentTile

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

from trendminer_interface.trendhub import TrendHubViewFactory
from .base import TileBase, TileFactoryBase


class TrendHubViewTile(TileBase):
    visualization_type = "TREND_HUB_VIEW"
    min_size = (2, 4)

    def __init__(self, client, content, x, y, title, refresh_rate, rows, cols,
                 trend_view_id=None, show_colored_points_legend=None, show_context_items=None, show_data_reference_labels=None, show_time_frame=None, show_title=None):
        super().__init__(client, content, x, y, title, refresh_rate, rows, cols)
        self.trend_view_id = trend_view_id
        self.show_colored_points_legend = show_colored_points_legend
        self.show_context_items = show_context_items
        self.show_data_reference_labels = show_data_reference_labels
        self.show_time_frame = show_time_frame
        self.show_title = show_title

    def _get_content(self, content):
        return TrendHubViewFactory(client=self.client)._get(content)

    def _json_configuration(self):
        return {
            "trendViewId": self.trend_view_id or (self.content.identifier if self.content else None),
            "showColoredPointsLegend": self.show_colored_points_legend,
            "showContextItems": self.show_context_items,
            "showDataReferenceLabels": self.show_data_reference_labels,
            "showTimeFrame": self.show_time_frame,
            "showTitle": self.show_title,
        }


class TrendHubViewTileFactory(TileFactoryBase):
    tm_class = TrendHubViewTile

    def _from_json_content(self, data):
        return TrendHubViewFactory(client=self.client)._from_json_identifier_only(data["trendViewId"])

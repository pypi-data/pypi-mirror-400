from trendminer_interface.base import ByFactory, kwargs_to_class
from trendminer_interface.work import WorkOrganizerObjectBase, WorkOrganizerObjectFactoryBase

from .tile import (TileMultiFactory, TrendHubViewTileFactory,
                   CounterTileFactory, TableTileFactory,
                   GanttTileFactory, MonitorTileFactory,
                   ExternalContentTileFactory, CurrentValueTileFactory,
                   TextTileFactory)

# TODO : handle the new global dashboard settings
class Dashboard(WorkOrganizerObjectBase):
    """TrendMiner dashboard (DashHub view)

    Attributes
    ----------
    live : bool
        Whether the dashboard is updating live
    scrollable : bool
        Whether the dashboard is scrollable
    tiles : list
        Tiles that are on the dashboard
    global_timeframe : dict
        Global timeframe configuration for the dashboard
    configuration : dict
        Dashboard configuration settings
    chart_aliases : dict or None
        Chart aliases for the dashboard
    """
    content_type = "DASHBOARD"
    tiles = ByFactory(TileMultiFactory, "_list")

    # pylint: disable=too-many-arguments
    def __init__(
            self,
            client,
            identifier,
            name,
            description,
            parent,
            owner,
            last_modified,
            version,
            tiles,
            live,
            global_timeframe,
            configuration,
            chart_aliases=None,
    ):

        # if global_timeframe is None:
        #     global_timeframe = {"type": "DEFAULT"}
        # if configuration is None:
        #     configuration = {'ALERT': {'fillBackground': False, 'showTitle': True}, 'CONTEXT_HUB_VIEW': {'showColoredPointsLegend': True, 'showTimeFrame': True, 'showTitle': True}, 'EXTERNAL_CONTENT': {'showTitle': True}, 'NOTEBOOK_PIPELINE': {'showTitle': True}, 'RICH_TEXT': {'showTitle': True}, 'TREND_HUB_VIEW': {'showColoredPointsLegend': True, 'showContextItems': True, 'showDataReferenceLabels': True, 'showTimeFrame': True, 'showTitle': True}, 'VALUE': {'fillBackground': False, 'miniGraph': {'show': True, 'timeSpan': '010000'}, 'showComponentNames': True, 'showTimestamp': True, 'showTitle': True, 'useChartAlias': False}, 'dynamicFontSizing': False, 'overrideTileSettings': False}

        WorkOrganizerObjectBase.__init__(self, client=client, identifier=identifier, name=name, description=description,
                                         parent=parent, owner=owner, last_modified=last_modified, version=version)

        self.live = live
        self.tiles = tiles
        self.global_timeframe = global_timeframe
        self.configuration = configuration
        self.chart_aliases = chart_aliases

    def _json_data(self):
        json_data = {
            "autoRefreshEnabled": self.live,
            "tiles": [tile._json() for tile in self.tiles],
        }
        
        if self.global_timeframe is not None:
            json_data["globalTimeframe"] = self.global_timeframe
            
        if self.configuration is not None:
            json_data["configuration"] = self.configuration
            
        return json_data

    def _full_instance(self):
        return DashboardFactory(client=self.client).from_identifier(self.identifier)


class DashboardFactory(WorkOrganizerObjectFactoryBase):
    """Factory for initializing and retrieving dashboards"""
    tm_class = Dashboard

    def __call__(self,
                 tiles,
                 name='New Dashboard',
                 description='',
                 parent=None,
                 live=False,
                 global_timeframe=None,
                 configuration=None,
                 ):
        """Initialize a new dashboard

        Parameters
        ----------
        tiles : list
            Tiles to add to the dashboard
        name : str, default "New Dashboard"
            Name of the dashboard
        description : str, optional
            Dashboard description
        parent : Folder or str
            Folder in which the dashboard needs to be saved
        live : bool
            Whether the dashboard will be updated live
        scrollable : bool
            Whether the dashboard needs to be scrollable
        global_timeframe : dict
            Global timeframe configuration for the dashboard
        configuration : dict
            Dashboard configuration settings

        Returns
        -------
        Dashboard
        """

        if global_timeframe is None:
            global_timeframe = {"type": "DEFAULT"}
        if configuration is None:
            configuration = {'ALERT': {'fillBackground': False, 'showTitle': True}, 'CONTEXT_HUB_VIEW': {'showColoredPointsLegend': True, 'showTimeFrame': True, 'showTitle': True}, 'EXTERNAL_CONTENT': {'showTitle': True}, 'NOTEBOOK_PIPELINE': {'showTitle': True}, 'RICH_TEXT': {'showTitle': True}, 'TREND_HUB_VIEW': {'showColoredPointsLegend': True, 'showContextItems': True, 'showDataReferenceLabels': True, 'showTimeFrame': True, 'showTitle': True}, 'VALUE': {'fillBackground': False, 'miniGraph': {'show': True, 'timeSpan': '010000'}, 'showComponentNames': True, 'showTimestamp': True, 'showTitle': True, 'useChartAlias': False}, 'dynamicFontSizing': True, 'overrideTileSettings': False}

        return self.tm_class(
            client=self.client,
            identifier=None,
            name=name,
            description=description,
            parent=parent,
            owner=None,
            last_modified=None,
            version=None,
            tiles=tiles,
            live=live,
            global_timeframe=global_timeframe,
            configuration=configuration,
        )

    def _json_data(self, data):
        """Enriched response json to dashboard

        Parameters
        ----------
        data : dict
            Response json

        Returns
        -------
        Dashboard
        """
        return {
            "live": data["data"].get("autoRefreshEnabled", False),
            "tiles": [
                TileMultiFactory(client=self.client)._from_json(tile)
                for tile in data["data"]["tiles"]
            ],
            "global_timeframe": data["data"].get("globalTimeframe"),
            "configuration": data["data"].get("configuration"),
            "chart_aliases": data["data"].get("chartAliases"),
        }

    @property
    def trend(self):
        """TrendHub view tile factory

        Returns
        -------
        TrendHubViewTileFactory
        """
        return TrendHubViewTileFactory(client=self.client)

    @property
    def count(self):
        """ContextHub view counter tile factory

        Returns
        -------
        CounterTileFactory
        """
        return CounterTileFactory(client=self.client)

    @property
    def table(self):
        """ContextHub view table tile factory

        Returns
        -------
        TableTileFactory
        """
        return TableTileFactory(client=self.client)

    @property
    def gantt(self):
        """ContextHub view gantt tile factory

        Returns
        -------
        GanttTileFactory
        """
        return GanttTileFactory(client=self.client)

    @property
    def monitor(self):
        """Monitor tile factory

        Returns
        -------
        MonitorTileFactory
        """
        return MonitorTileFactory(client=self.client)

    @property
    def external(self):
        """External content tile factory

        Returns
        -------
        ExternalContentTileFactory
        """
        return ExternalContentTileFactory(client=self.client)

    @property
    def text(self):
        """Text tile factory

        Returns
        -------
        TextTileFactory
        """
        return TextTileFactory(client=self.client)

    @property
    def values(self):
        """Current value tile factory

        Returns
        -------
        CurrentValueTileFactory
        """
        return CurrentValueTileFactory(client=self.client)

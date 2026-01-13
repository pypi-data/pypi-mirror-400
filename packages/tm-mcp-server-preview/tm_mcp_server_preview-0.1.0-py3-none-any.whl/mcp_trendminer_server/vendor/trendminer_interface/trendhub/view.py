import pandas as pd
from urllib.parse import urljoin

from trendminer_interface.tag import Tag
from trendminer_interface.asset import Attribute
from trendminer_interface.base import ByFactory
from trendminer_interface.work import WorkOrganizerObjectBase, WorkOrganizerObjectFactoryBase
from .entry import TrendHubEntryMultiFactory
from .group import TrendHubEntryGroup
from .context_interval import ContextChartIntervalFactory
from .layer import LayerFactory, Layer
from .chart import ChartingPropertiesFactory, StackedChartPropertiesFactory


class TrendHubView(WorkOrganizerObjectBase):
    """TrendHub view

    Attributes
    ----------
    live : bool

    entries : list
        List of Tag, Attribute or EntryGroup
    chart : StackedChartProperties or TrendChartProperties or ScatterChartProperties
        Chart configuration as object
    context_interval : ContextInterval
        Context bar interval
    filters : list of dict
        Filters in raw json format. Setting or changing view filters is currently not supported.
    fingerprints : list of dict
        Fingerprints in raw json format. Setting or changing view fingerprints is currently not supported.
    """
    content_type = "TREND_HUB_2_VIEW"
    entries = ByFactory(TrendHubEntryMultiFactory, "_list")
    chart = ByFactory(ChartingPropertiesFactory)
    context_interval = ByFactory(ContextChartIntervalFactory)

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
            entries,
            layers,
            context_interval,
            live,
            chart,
            filters,
            fingerprints,
    ):

        WorkOrganizerObjectBase.__init__(self, client=client, identifier=identifier, name=name, description=description,
                                         parent=parent, owner=owner, last_modified=last_modified, version=version)

        self.live = live
        self.entries = entries
        self.chart = chart
        self.layers = layers
        self.context_interval = context_interval
        self.filters = filters
        self.fingerprints = fingerprints

    @property
    def tags(self):
        """Flat list of underlying tags in the view

        Underlying tags are extracted from attributes and groups

        Returns
        -------
        list of Tag
        """
        tags = []
        for entry in self.entries:
            if isinstance(entry, Tag):
                tags.append(entry)
            elif isinstance(entry, Attribute):
                tags.append(entry.tag)
            elif isinstance(entry, TrendHubEntryGroup):
                for group_tag in entry.tags:
                    tags.append(group_tag)
            else:
                raise NotImplementedError
        return tags

    @property
    def layers(self):
        """View layers

        When setting, a single layers can be configured as the base layer by setting the `base` attribute to `True`. If
        none of the layers is explicitly set as base layer, it is assumed the first layer is the base layer.

        The layers can be set by passing Layer instances, but Interval instances work too. These are turned into layers
        with default configuration.

        Returns
        -------
        list of Layer
        """
        return self._layers

    @layers.setter
    def layers(self, layers):
        if not (isinstance(layers, list) and all([isinstance(layer, Layer) for layer in layers])):
            layers = LayerFactory(client=self.client, view=self).from_intervals(layers)
        self._layers = layers

    def _trim_layer_display_intervals(self, align_trailing=False):
        """Trim display intervals to the base layer. The display interval duration of secondary layers should always be
        the same as that of the base layer. This function needs to be invoked whenever layers are input manually by a
        user"""
        for layer in self.layers:
            if align_trailing:
                layer._display_timespan = pd.Interval(
                    left=layer.interval.right - self.base_layer.interval.length,
                    right=layer.interval.right,
                    closed=layer.interval.closed,
                )
            else:
                layer._display_timespan = pd.Interval(
                    left=layer.interval.left,
                    right=layer.interval.left + self.base_layer.interval.length,
                    closed=layer.interval.closed,
                )

    @property
    def base_layer(self):
        """The base layer

        Returns
        -------
        Layer
        """
        return [layer for layer in self.layers if layer.base][0]

    def get_data(self, freq=None):
        """Retrieve interpolated timeseries data for underlying tags and layers

        Parameters
        ----------
        freq : pandas.Timedelta or str or float, optional
            Data resolution as a Timedelta, duration-like string (e.g. '2h', '1d') or number of seconds. Defaults to
            TrendMiner index resolution.

        Returns
        -------
        list of DataFrame
            Dataframe for every layer in the view, which have a DatetimeIndex and tag names as columns

        Notes
        -----
        Data is obtained from linear interpolation of the indexed data in TrendMiner. Asking for a high resolution data
        will not perform a datasource call to obtain datapoints that are not in the index.

        The interval is rounded to the resolution, to obtain regular timestamps (e.g., 9:15:00, 9:15:30, ...). This
        is an important step especially when asking for data for the 'last x time', which would otherwise generally
        yield irregular timestamps (e.g., 9:15:17.032, 19:15:47.032).

        Any tag time shift will be taken into account: the returned data will be for the shifted tag.

        A call to get TrendMiner data does not automatically trigger indexing of the tag. It is up to the user to ensure
        the tag is indexed for the required period prior to requesting the data (cfr. Tag.index).
        """
        return [layer.get_data(freq=freq) for layer in self.layers]

    def _json_data(self):
        return {
            "contextTimeSpan": self.context_interval._json(),
            "data": {
                "chartingProperties": self.chart._json(),
                "filterEntries": self.filters,
                "fingerprintEntries": self.fingerprints,
                "layers": [layer._json() for layer in self.layers],
                "listEntries": [entry._json_trendhub() for entry in self.entries],
            },
            "liveMode": self.live,
            "timeSpan": {
                "startDate": self.base_layer._display_timespan.left.isoformat(timespec="milliseconds"),
                "endDate": self.base_layer._display_timespan.right.isoformat(timespec="milliseconds"),
            },
        }

    def _full_instance(self):
        return TrendHubViewFactory(client=self.client).from_identifier(self.identifier)

    def get_session_url(self):
        """Generate unique session url for sharing the view via link

        Returns
        -------
        str
            The url leading to the specified view
        """
        response = self.client.session.post(
            url="work/sessions",
            json={"data": self._json_data()},
        )
        session_id = response.json()["identifier"]
        return urljoin(self.client.url, f"/trendhub/#/share/{session_id}")


class TrendHubViewFactory(WorkOrganizerObjectFactoryBase):
    tm_class = TrendHubView

    def __call__(self,
                 entries,
                 layers,
                 context_interval,
                 live=False,
                 chart=None,
                 name='New View',
                 description='',
                 parent=None,
                 align_trailing=False,
                 ):
        """Instantiate a new TrendHub view

        Parameters
        ----------
        entries : list of Any
            List of Tag, Attribute or EntryGroup. Strings are interpreted as tags or assets
        layers : list of pandas.Interval
            Intervals to be converted into Layer instances. Creating and passing Layer instances directly is currently
             not supported. The layers need to created before first, and then they can be customized (e.g. visibility,
             linestyle, name). The first interval in the list will become the base layer. All other layers will be
             trimmed or extended to match the base layer length if layers are not the same size.
        chart : StackedChartProperties or TrendChartProperties or ScatterChartProperties
            Chart configuration as object
        context_interval : ContextInterval | pandas.Interval
            Context period Interval
        live : bool, default False
            Whether the view should be live
        name : str, default 'New View'
            The view name
        description : str, default ''
            The view description
        parent : Folder or str
            Folder in which the view would be saved (when doing a post or put request)
        align_trailing : bool, default False
            Whether the different layers should be aligned by their end date, rather than by their start date. Only
            matters if the different layers provided are not of the same length.

        Returns
        -------
        TrendHubView
        """

        chart = chart or StackedChartPropertiesFactory(client=self.client)()

        view = self.tm_class(
            client=self.client,
            identifier=None,
            name=name,
            description=description,
            parent=parent,
            owner=None,
            last_modified=None,
            version=None,
            entries=entries,
            layers=layers,
            context_interval=context_interval,
            live=live,
            chart=chart,
            filters=[],
            fingerprints=[],
        )

        view._trim_layer_display_intervals(align_trailing=align_trailing)

        return view

    def _json_data(self, data):
        return {
            "entries": [
                TrendHubEntryMultiFactory(client=self.client)._from_json_trendhub(entry)
                for entry in data["data"]["data"]["listEntries"]
            ],
            "layers": [
                LayerFactory(client=self.client, view=None)._from_json(layer)
                for layer in data["data"]["data"]["layers"]
            ],
            "context_interval": pd.Interval(
                left=pd.Timestamp(data["data"]["contextTimeSpan"]["startDate"]).tz_convert(tz=self.client.tz),
                right=pd.Timestamp(data["data"]["contextTimeSpan"]["endDate"]).tz_convert(tz=self.client.tz),
                closed="both",
            ),
            "live": data["data"]["liveMode"],
            "chart": ChartingPropertiesFactory(client=self.client)._from_json(data["data"]["data"]["chartingProperties"]),
            "filters": data["data"]["data"]["filterEntries"],  # TODO: create filter objects
            "fingerprints": data["data"]["data"]["fingerprintEntries"],  # TODO: create fingerprint objects
        }

    def _from_json(self, data):
        # The view needs to be set on the layers after instantiation.
        # TODO: this code is indicative of a design flaw that should be fixed properly
        view = super()._from_json(data)

        for layer in view.layers:
            layer.view = view

        return view

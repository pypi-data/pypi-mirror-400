import uuid
import pandas as pd

import trendminer_interface._input as ip

from trendminer_interface.base import RetrievableBase, FactoryBase, AsTimedelta, LazyAttribute
from trendminer_interface.constants import LINE_STYLES



class Layer(RetrievableBase):
    """TrendHub layer

    Attributes
    ----------
    view : TrendHubView
        TrendHub view the layer is attached to
    name : str
        Layer name
    """
    shift = AsTimedelta()

    def __init__(
            self,
            client,
            view,
            name,
            display_timespan,
            timespan,
            base,
            visible,
            line_style,
            hidden_references,
            identifier,
            shift,
            source,
    ):
        super().__init__(client=client, identifier=identifier)
        self.view = view
        self.name = name

        # DisplayTimeSpan is what really counts, this is the original timespan as viewed when saved by the user
        # timeSpan has less meaning, as it could be completely unrelated to what the user wants to visualize. Both
        # values do not update with the live view. The actual currently displayed interval of a view is derived from
        # the saved value, the current time, and the view settings (live, locked)
        self._display_timespan = display_timespan
        self._timespan = timespan

        self.line_style = line_style
        self.base = base
        self.visible = visible
        self.hidden_references = hidden_references
        self.name = name
        self.shift = shift
        self.source = source

    # TODO: How does a context item origin work?
    @property
    def origin(self):
        """Original interval of the layer. Can not be changed after layer has been made.

        The origin of an interval does not really matter. It can be completely different from the currently selected
        layer, which is under the `interval` property.

        Returns
        -------
        pandas.Interval
        """
        return self._timespan

    @property
    def interval(self):
        """Current interval described by the layer

        Returns
        -------
        pandas.Interval
        """
        return self._actualize_interval(self._display_timespan)

    def _actualize_interval(self, interval):
        """Bring originally saved interval (which does not change in the backend) to the currently displayed period

        Parameters
        ----------
        interval : pandas.Interval
            The original interval to actualize

        Returns
        -------
        pandas.Interval
            The original interval projected to current time based on live and locked settings
        """
        if self.view is None:
            return interval

        if not self.view.live:
            return interval

        shift = pd.Timestamp.now(tz=self.client.tz) - self.view.base_layer._display_timespan.right

        left = interval.left
        right = interval.right + shift

        if self.view.chart.locked:
            left = left + shift

        return pd.Interval(left=left, right=right, closed=interval.closed)

    def set_interval(self, interval, align_trailing=False):
        """Set the interval of the layer to a new value

        Updates the origin of the layer, as well as the displayed interval. The displayed interval depends on the base
        layer as it will assume the same length as the base layer (time can can be cut off or added).

        Setting the base layer itself will cause changes is the displayed intervals of all other layers, as they will
        need to match the length of the base layer.

        Parameters
        ----------
        interval : pandas.Interval
            Interval to reset the layer to
        align_trailing : bool, default False
            When True, the new layer will align with the end of the base layer of the underlying view. Otherwise, it
            will align with the start of the base layer. When the base layer is changed, all other layers will be
            aligned based on this parameter.
        """

        # Update the origin
        self._timespan = interval
        self.source = {"type": "MANUAL"}
        self.shift = pd.Timedelta(0)

        # Update the displayed interval, depends on the base layer
        base_duration = self.view.base_layer.interval.length
        if align_trailing:
            self._display_timespan = pd.Interval(
                left=interval.right - base_duration,
                right=interval.right,
                closed=interval.closed,
            )
        else:
            self._display_timespan = pd.Interval(
                left=interval.left,
                right=interval.right + base_duration,
                closed=interval.closed,
            )

        # If the base layer is changed, all layers need changes to the display interval
        if self.base:
            self.view._trim_layer_display_intervals(align_trailing=align_trailing)

    @property
    def line_style(self):
        """Display line style of the layer

        Always "SOLID" for the base layer. For the other layers, it can be "DASHED", "DOTTED", "DASHDOTDOTTED",
        "DASHDOTTED" or "LOOSEDASHDOTTED".

        Returns
        -------
        str
        """
        if self.base:
            return "SOLID"
        return self._line_style if self._line_style != "SOLID" else "DASHED"

    @line_style.setter
    @ip.options(LINE_STYLES)
    def line_style(self, line_style):
        self._line_style = line_style

    @property
    def visible(self):
        """Whether the layer is visible in the view

        Always `True` for the base layer

        Returns
        -------
        bool
        """
        return self._visible

    @visible.setter
    def visible(self, visible):
        self._visible = self.base or visible

    @property
    def base(self):
        """Whether the current layer is the base layer

        Setting `base=True` will automatically set `base=False` for the current base layer of the view, as there can
        only be a single base layer in a view.

        Returns
        -------
        bool
        """
        return self._base

    @base.setter
    def base(self, base):
        # Reset previous base layer
        if base:
            try:
                self.view.base_layer.base = False
            except AttributeError:
                pass  # layers not instantiated yet
        self._base = base

    def get_data(self, freq=None):
        """Retrieve interpolated timeseries data for underlying tags

        Parameters
        ----------
        freq : pandas.Timedelta, optional
            Data resolution. Defaults to TrendMiner index resolution.

        Returns
        -------
        DataFrame
            A dataframe with DatetimeIndex and tag names as columns

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
        return pd.concat(
            [tag.get_data(interval=self.interval, freq=freq) for tag in self.view.tags],
            axis=1,
        )

    def _json(self):
        return {
            "baseLayer": self.base,
            "displayTimeSpan": {
                "startDate": self._display_timespan.left.isoformat(timespec="milliseconds"),
                "endDate": self._display_timespan.right.isoformat(timespec="milliseconds"),
            },
            "id": self.identifier,
            "name": self.name,
            "options": {
                "hiddenDataReferences": self.hidden_references,
                "lineStyle": self.line_style,
                "shift": int(self.shift.total_seconds()*1000),
                "visible": self.visible
            },
            "source": self.source,
            "timeSpan": {
                "startDate": self._timespan.left.isoformat(timespec="milliseconds"),
                "endDate": self._timespan.right.isoformat(timespec="milliseconds"),
            },
        }

    def __repr__(self):
        return f"<< {self.__class__.__name__} | {self.interval.left} | {self.interval.length} >>"


class LayerFactory(FactoryBase):
    """Factory class for creating new layers

    As a layer is always attached to a TrenHub view, and cannot exist as independent object, this class is only intended
    for internal use. It is called from the TrendHubView instance.

    Attributes
    ----------
    view : TrendHubView
        TrendHub view to which the created layers will belong
    """
    tm_class = Layer

    def __init__(self, client, view):
        super().__init__(client=client)
        self.view = view

    def __call__(self, interval, base=True, name="", visible=True, line_style="SOLID"):
        """Instantiate a new layer

        Parameters
        ----------
        interval : pandas.Interval
            The layer interval
        base : bool, default True
            Whether the layer is a base layer
        visible : bool, default True
            Whether the layer is visible
        line_style : str, default "SOLID"
            Layer line style
        """
        return self.tm_class(
            client=self.client,
            view=self.view,
            name=name,
            display_timespan=interval,
            timespan=interval,
            base=base,
            visible=visible,
            line_style="SOLID",
            hidden_references=[],
            identifier=str(uuid.uuid4()),
            shift=pd.Timedelta(0),
            source={"type": "MANUAL"},
        )

    def from_interval(self, interval, base=False):
        """Create a Layer from a given Interval

        Intended to convert list of intervals into layers when the user creates a view.
        Layer will not be base by default, and have the "DASHED" line style.

        Parameters
        ----------
        interval : pandas.Interval
            Interval to be turned into a layer
        base : bool, default False
            Whether the layer is a base layer
        """
        return self.__call__(
            interval=interval,
            base=base,
            line_style='DASHED'
        )

    def from_intervals(self, intervals):
        """Create layers from multiple intervals

        This method is only intended to be called when setting view layers

        Unless otherwise specified, the first layer will be assigned as the base layer. All other layers will have the
        "DASHED" line style.

        Parameters
        ----------
        intervals : list[pandas.Interval] | pandas.IntervalIndex | pandas.DataFrame
            Intervals to be turned into layers. When a DataFrame is given, it should have IntervalIndex. The following
            DataFrame columns are taken into account for layer creation:
            - base (bool): whether the interval should become the base layer (should only be True for a single interval)
            - line_style (str): layer line style {"DASHED", "DOTTED", "DASHDOTDOTTED", "DASHDOTTED", "LOOSEDASHDOTTED"}
            - visible (bool): whether the layer should be visible or hidden
            - name (str): the layer name

        Returns
        -------
        layers : list of Layer
        """

        # Pass through lazy loading attributes
        if isinstance(intervals, LazyAttribute):
            return intervals

        # Turn input into DataFrame
        if isinstance(intervals, pd.Series):
            intervals = pd.DataFrame(intervals)

        if not isinstance(intervals, pd.DataFrame):
            intervals = pd.IntervalIndex(intervals)
            intervals = pd.DataFrame(index=intervals)

        # Add name column
        if "name" not in intervals:
            intervals["name"] = ""

        # Add line style column
        if "line_style" not in intervals:
            intervals["line_style"] = "DASHED"

        # Validate/add visible column
        if "visible" in intervals:
            intervals["visible"] = intervals["visible"].astype(bool)
        else:
            intervals["visible"] = True

        # Validate/add base column
        if "base" in intervals:
            intervals["base"] = intervals["base"].astype(bool)
            if not intervals["base"].sum() == 1:
                raise ValueError("`base` column should have only a single value which is True")
        else:
            intervals["base"] = False
            intervals.iloc[0, intervals.columns.get_loc("base")] = True  # First layer as base layer
            intervals.iloc[0, intervals.columns.get_loc("line_style")] = "SOLID"  # Overwrite base layer line style
            intervals.iloc[0, intervals.columns.get_loc("visible")] = True  # Overwrite base layer visibility

        return intervals.apply(
            lambda r: self.__call__(
                interval=r.name,
                base=r["base"],
                name=r["name"],
                visible=r["visible"],
                line_style=r["line_style"],
            ),
            axis=1,
        ).to_list()

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        Layer
        """
        return self.tm_class(
            client=self.client,
            view=self.view,
            name=data["name"],
            display_timespan=pd.Interval(
                left=pd.Timestamp(data["displayTimeSpan"]["startDate"]).tz_convert(self.client.tz),
                right=pd.Timestamp(data["displayTimeSpan"]["endDate"]).tz_convert(self.client.tz),
                closed="both",
            ),
            timespan=pd.Interval(
                left=pd.Timestamp(data["timeSpan"]["startDate"]).tz_convert(self.client.tz),
                right=pd.Timestamp(data["timeSpan"]["endDate"]).tz_convert(self.client.tz),
                closed="both",
            ),
            base=data["baseLayer"],
            visible=data["options"]["visible"],
            line_style=data["options"]["lineStyle"],
            hidden_references=data["options"]["hiddenDataReferences"],
            identifier=data["id"],
            shift=pd.Timedelta(milliseconds=data["options"]["shift"]),
            source=data["source"],
        )

    @property
    def _get_methods(self):
        return self.from_interval,

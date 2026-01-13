import abc
import itertools
import numpy as np
import pandas as pd
import json
import cachetools
import posixpath
import operator

from typing import NamedTuple, Union

from trendminer_interface import _input as ip
from trendminer_interface.base import (FactoryBase, LazyLoadingMixin, RetrievableBase, LazyAttribute, HasOptions,
                                       ByFactory, kwargs_to_class, ComponentMixin, ComponentFactoryMixin,
                                       TimeSeriesMixin, TimeSeriesFactoryBase, default_trendhub_attributes)
from trendminer_interface.constants import (MAX_TAG_CACHE, BUILTIN_DATASOURCES, MAX_GET_SIZE, TAG_TYPE_OPTIONS,
                                            MAX_INTERPOLATED_TAG_POINTS)
from trendminer_interface.exceptions import ResourceNotFound
from trendminer_interface.datasource import DatasourceFactory, Datasource

from .index import IndexStatusFactory, IndexStatus


class TagClient(abc.ABC):
    """Client with TagFactory"""
    @property
    def tag(self):
        """Factory for retrieving and instantiating tags"""
        return TagFactory(client=self)


class DataPoint(NamedTuple):
    """A time-series data point

    Attributes
    ----------
    ts : pandas.Timestamp
        Timestamp of the point
    value : float or str
        Value of the point (float for numeric tags, str for digital/string tags)
    """
    ts: pd.Timestamp
    value: Union[float,str]

    def __repr__(self):
        return f"<< {self.__class__.__name__} | {self.ts.__str__()} | {self.value} >>"


class Tag(RetrievableBase, TimeSeriesMixin, ComponentMixin, LazyLoadingMixin):
    """A tag is a named stream of timeseries data

    Tags are the basis of all timeseries operations in TrendMiner. They are use throughout the applications and are
    referenced by many other classes. Tags are typically only retrieved from the appliance. It is possible to
    instantiate a new tag, though the only direct application is to create a new csv-imported tag on the appliance.

    A Tag is a 'lazy' class, meaning some attributes will only be loaded from the appliance the moment they are
    accessed. This can cause waiting times or errors at unexpected times.

    Tag instances can be created, but they cannot be directly created, updated or deleted on the appliance (i.e., there
    are no post, put or delete methods). They can, however, be uploaded and deleted as imported tags via
    :attr:`client.io.tags`.

    Attributes
    ----------
    name : str
        tag name, must be unique
    description : str
        Provides additional info on the tag
    tag_type : str
        - **ANALOG**: numerical values, linear interpolation
        - **DISCRETE**: numerical values, step-after interpolation
        - **DIGITAL**: Selection from fixed set of string values, step-after interpolation
        - **STRING**: Any string value, step after interpolation

        STRING and DIGITAL tags are treated exactly the same in TrendMiner: a state is created for every new string tag
        value
    units : str
        Measurement physical units. Can be blank. Units are purely informative, they are not interpreted by the
        appliance.
    states : dict[int, str]
        Possible states for a digital or string tag. This data can be heavy to load for string tags, as they can have
        a very large number of 'states'. The key of a state in the dict is the index that the state has in the
        appliance. In case a state no longer exists at a given index, that key is not included in the dict.
    datasource : Datasource
        The datasource containing the tag
    """
    endpoint = "/ds/timeseries/"
    component_type = "TAG"
    tag_type = HasOptions(TAG_TYPE_OPTIONS)

    datasource = ByFactory(DatasourceFactory)

    def __init__(self, client, identifier, name, description, units, tag_type, datasource, states, color, scale,
                 shift, visible):

        RetrievableBase.__init__(self=self, client=client, identifier=identifier)
        TimeSeriesMixin.__init__(self=self, color=color, scale=scale, shift=shift, visible=visible)

        self.name = name
        self.tag_type = tag_type
        self.states = states
        self.description = description
        self.units = units
        self.datasource = datasource

    @property
    def index(self):
        """Interface to tag index status

        Returns
        -------
        IndexStatus
            Interface to the index status of the tag
        """
        return IndexStatusFactory(client=self.client).from_tag(tag=self)

    @property
    def numeric(self):
        """Whether the tag is numeric

        Tags with tag_type ANALOG and DISCRETE are numeric

        Returns
        -------
        bool
            Whether the tag is numeric
        """
        return self.tag_type in ["ANALOG", "DISCRETE"]

    @property
    def stepped(self):
        """Whether the tag is step-interpolated

        Tags with tag_type DISCRETE, DIGITAL and STRING are stepped

        Returns
        -------
        bool
            Whether the tag is step-interpolated
        """
        return self.tag_type in ["DISCRETE", "DIGITAL", "STRING"]

    @property
    def _interpolation_payload_str_lower(self):
        """Interpolation type a string, used in data calls

        Different interpolation syntax from the _interpolation_payload_str property

        Returns
        -------
        str
            'linear' or 'step-after'
        """
        return "step-after" if self.stepped else "linear"

    @property
    def _interpolation_payload_str(self):
        """Tag interpolation type

        Returns
        -------
        str
            LINEAR or STEPPED
        """
        return "STEPPED" if self.stepped else "LINEAR"

    def _get_state_index(self, state):
        """Returns index of given state

        Every state of a digital or string tag is assigned a unique index (an integer). For digital tags, this index
        would typically come from the historian. For a string tag, the index is assigned by TrendMiner, always taking
        the next integer value when a new string value is retrieved from the datasource.

        Parameters
        ----------
        state : str
            state for which we want to retrieve the index

        Returns
        -------
        index : int
            index of the given state in the appliance
        """

        # Make a dict of potential matches
        selection_dict = {
            state_name: index for index, state_name in self.states.items()
            if state_name.lower() == state.lower()
        }

        # Correct the case if needed (and throw an error if there are multiple case-sensitive matches)
        state = ip.case_correct(state, selection_dict.keys())

        return selection_dict[state]

    def get_data(self, interval, freq=None):
        """Retrieve interpolated time series data for the tag

        Parameters
        ----------
        interval : pandas.Interval
            Time interval for which the data needs to be retrieved. The `interval.closed` attribute is taken into
            account when returning datapoints.
        freq : pandas.Timedelta, optional
            Data resolution. Time between subsequent datapoints. If not provided, the TrendMiner index resolution is
            used.

        Returns
        -------
        data : pandas.Series
            Tag data with the the following properties:
            - **name** is equal to the tag name
            - **index** is a DatetimeIndex in the client timezone.
            - **dtype** is ``float64`` for numeric tags, ``str`` for string tags

        Notes
        -----
        Data is obtained from linear interpolation of the indexed data in TrendMiner. Asking for a high resolution data
        will not perform a datasource call to obtain datapoints that are not in the index.

        Any tag time shift will be taken into account: the returned data will be for the shifted tag.

        The returned timestamps result from the interval start time (interval.left) and the provided frequency. If the
        interval start time is irregular, the resulting timestamps will also be irregular (e.g., 9:15:17.032,
        19:15:47.032, ...). If regular intervals are required, it is the user's responsibility to provide a regular
        (rounded) input interval.

        A call to get TrendMiner data does not automatically trigger indexing of the tag. It is up to the user to ensure
        the tag is indexed for the required period prior to requesting the data (cfr. Tag.index).

        If an analog tag is not fully indexed for the requested interval. NaN values will be present for the interval.
        For stepped tags (discrete, digital and string), the values up to the current timestamp will be forward filled,
        and only timestamps after the current time will be NaN (discrete) or NA (digital, string).
        """

        # Process inputs
        freq = pd.Timedelta(freq) if freq is not None else self.client.resolution

        # Split the interval into parts to not exceed the maximum number of allowed points per call
        # The intervals need to be calculated in UTC as calculating them in a local timezone within a DST-transition
        # interval for certain frequencies can create a mismatch between expected_index timestamps and those returned by
        # TrendMiner (always UTC). For example, the a daily ('1d') frequency in a local timezone will put interval start
        # times at the same time each day, which means timestamps can be 23h or 25h apart during a DST transition. This
        # mismatch would lead to NaN values when the data returned by TrendMiner is reindexed to the expected_index
        # timestamps.
        granularity = freq * (MAX_INTERPOLATED_TAG_POINTS - 1)
        periods = int(np.ceil(interval.length/granularity))
        parts = pd.interval_range(
            start=interval.left.astimezone("UTC"),  # conversion to UTC necessary
            end=interval.right.astimezone("UTC"),
            periods=periods,
        )

        step_payload = int(freq.total_seconds())

        tag_payload = {
            "id": self.identifier,
            "interpolationType": self._interpolation_payload_str_lower,
            "shift": int(self.shift.total_seconds()),
        }

        payloads = parts.map(
            lambda x: {
                "step": step_payload ,
                "tag": tag_payload,
                "timePeriod": {
                    "startDate": x.left.isoformat(timespec="milliseconds"),
                    "endDate": x.right.isoformat(timespec="milliseconds"),
                }
            }
        ).to_list()

        responses = [
            self.client.session.post("/compute/interpolatedData", json=payload)
            for payload in payloads
        ]

        # Join the list of lists of dicts obtained from subsequent calls
        data = list(
            itertools.chain.from_iterable([response.json()["values"] for response in responses])
        )

        # Convert the list of dicts to a pandas dataframe
        ser = self._dict_to_series(data)

        # Duplicate timestamps can occur from the chaining. Checking for duplicates is very fast, so we do not need a
        # more complex implementation that avoids duplicate timestamps.
        ser = ser.loc[~ser.index.duplicated(keep="first")]

        # convert to client timezone
        ser.index = ser.index.tz_convert(self.client.tz)

        # Remove forward filled timestamps that go beyond the current time (should only be an issue for stepped tags)
        mask = ser.index < pd.Timestamp.now(tz=self.client.tz)
        ser = ser[mask]

        # Reindex to the expected timestamps, even if our tag is missing index data for the given interval. The
        # resulting NaN values will warn the user that the tag data was not complete for the interval, rather than
        # silently passing and leading to wrong calculations and unexpected results.
        expected_index = pd.date_range(
            start=parts[0].left,
            end=parts[-1].right,
            freq=freq,
        )
        ser = ser.reindex(expected_index)
        ser.index = ser.index.tz_convert(self.client.tz)

        # Prune values from the edges of the series
        operator_left = operator.gt if interval.closed in ["neither", "right"] else operator.ge
        operator_right = operator.lt if interval.closed in ["neither", "left"] else operator.le
        mask = operator_left(ser.index, interval.left) & operator_right(ser.index, interval.right)
        ser = ser[mask]

        # return output
        return ser

    def get_chart_data(self, interval, periods=300):
        """Get plot-optimized data from TrendMiner

        Chart data is plot-optimized data, giving the best representation of the the trend with a limited amount of
        datapoints. The interval is split into blocks of equal length, and for each block up to 4 datapoints from the
        TrendMiner index are returned: the start, end, minimum, and maximum datapoints. Note that some of these points
        can overlap (e.g. the start point can also be the minimum) or blocks can even be empty, leading to (on average)
        less than 4 datapoints per block.

        Interpolated edge values will be returned at the edges of the interval. The `interval.closed` attribute does NOT
        impact the data returned from this method.

        Parameters
        ----------
        interval : pandas.Interval
            Time interval for which the data needs to be retrieved. The `closed` has no impact on the returned data.
        periods : int, default 300
            The number of chart blocks in which to split the requested interval. For each block, start, end, minimum and
            maximum stored datapoints are returned.

        Returns
        -------
        data : pandas.Series
            Tag data with the the following properties:
            - **name** is equal to the tag name
            - **index** is a DatetimeIndex in the client timezone.
            - **dtype** is ``float64`` for numeric tags, ``str`` for string tags

        Notes
        -----
        This method only returns datapoints which are stored in the index in TrendMiner. In the TrendMiner application,
        in some cases, plot data can be loaded from periods that have not yet been indexed by directing the call to
        the underlying datasource. Through the same mechanism of directing the call to the datasource, higher resolution
        data than stored in the TrendMiner index can be obtained. This mechanism is NOT included in this method.

        Any tag time shift will be taken into account: the returned data will be for the shifted tag.

        A call to get TrendMiner data does not automatically trigger indexing of the tag. It is up to the user to ensure
        the tag is indexed for the required period prior to requesting the data (cfr. Tag.index).
        """

        # As the endpoint used does not support a tag time shift parameter, we need to manually take a time shift into
        # account. Remember that if the tag is shifted forwards (positive shift value), we will get data from the past.
        # First we make sure to get our data from the correct interval.
        interval = pd.Interval(
            left=interval.left-self.shift,
            right=interval.right-self.shift,
            closed=interval.closed,
        )

        params = {
            "endDate": interval.right.isoformat(timespec="milliseconds"),
            "interpolationType": self._interpolation_payload_str_lower,
            "numberOfIntervals": periods,
            "startDate": interval.left.isoformat(timespec="milliseconds"),
            "timeSeriesId": self.identifier,
        }

        response = self.client.session.get("/compute/data/index", params=params)
        data = [
            json.loads(line.decode("utf-8"))["points"] for line in response.iter_lines()
        ]

        data = list(itertools.chain.from_iterable(data))
        ser = self._dict_to_series(data)

        # If the tag was shifted in time, we got our data for a different interval than provided by the user, meaning
        # the timestamps are still wrong. We need to add the tag shift again to correct the timestamps.
        ser.index = ser.index + self.shift

        # Index can have duplicate values
        ser = ser.drop_duplicates(keep="first")

        # Timestamp should be in the timezone provided by the user (rather than UTC).
        ser.index = ser.index.tz_convert(self.client.tz)

        return ser

    def get_index_data(self, interval):
        """Get stored tag index data from TrendMiner

        Parameters
        ----------
        interval : pandas.Interval
            Time interval for which the data needs to be retrieved. The `interval.closed` attribute is taken into
            account when returning datapoints.

        Returns
        -------
        data : pandas.Series
            Tag data with the the following properties:
            - **name** is equal to the tag name
            - **index** is a DatetimeIndex in the client timezone.
            - **dtype** is ``float64`` for numeric tags, ``str`` for string tags

        Notes
        -----
        Any tag time shift will be taken into account: the returned data will be for the shifted tag.

        A call to get TrendMiner data does not automatically trigger indexing of the tag. It is up to the user to ensure
        the tag is indexed for the required period prior to requesting the data (cfr. Tag.index).
        """

        # Calculate the number of interval blocks for which to get data
        periods = int(np.ceil(interval.length / self.client.resolution))

        # The call to get index data returns interpolated edge values. For this method to only return data that is
        # actually in the index, as the user would expect, we need will need to trim the 2 edge values. To ensure that
        # the edge values are not actual datapoints, we first widen the interval on both edges with 1ms (which is the
        # TrendMiner timestamp resolution). The trimmed datapoints will thus be outside the requested interval, and real
        # datapoints at the edge of the requested interval will be returned to the user.
        interval = pd.Interval(
            left=interval.left-pd.Timedelta(milliseconds=1),
            right=interval.right+pd.Timedelta(milliseconds=1),
            closed=interval.closed,
        )

        # We get the data from the get_chart_data method, which implements the request to /compute/data/index
        ser = self.get_chart_data(interval=interval, periods=periods)

        # Drop the interpolated edge values
        ser = ser.iloc[1:-1]

        # Prune edge values if interval.closed is not 'both'
        if interval.closed in ["neither", "right"]:
            try:
                ser.pop(interval.left)
            except KeyError:
                pass

        if interval.closed in ["neither", "left"]:
            try:
                ser.pop(interval.right)
            except KeyError:
                pass

        return ser

    def get_last_point(self):
        """Get last known datapoint directly from the datasource

        The returned point should represent the current datapoint if the tag is kept up to date in the datasource.

        For stepped tags, which are assumed to stay at the last known value until a new point comes in, the last point
        returned from this method will always be at the current time.

        Returns
        -------
        point : DataPoint
            NamedTuple(ts, value)

        Notes
        -----
        As the point is obtained from the datasource directly, this method can return a point later than the
        `Tag.get_last_indexed_point` method, or when the tag is not indexed.
        """
        params = {
            "timeSeriesId": self.identifier,
            "interpolationType": self._interpolation_payload_str,
        }
        response = self.client.session.get(
            "/compute/data/last-value",
            params=params
        )
        data = response.json()
        ts = pd.Timestamp(data["ts"]).tz_convert(self.client.tz)
        if self.numeric:
            value = data["value"]
        else:
            value = self.states[data["value"]]

        return DataPoint(ts=ts, value=value)

    # TODO: should method not return None for non-indexed tags?
    def get_last_indexed_point(self):
        """Get the last datapoint stored in the index

        Knowing the last indexed timestamp can be useful to ensure a tag is indexed up to a certain date. Do note that
        this does not really apply for stepped tags, for which it is assumed the value stays constant until a new point
        comes in. For those stepped tags, the last indexed point could be the actual last known point, or there could be
        more recent points in the datasource which are not yet stored in the index.

        Returns
        -------
        point : DataPoint
            NamedTuple(ts, value)

        Notes
        -----
        If the tag is not yet indexed, this method will raise an error.
        """
        response = self.client.session.get(
            f"/compute/index/{self.identifier}/last-indexed-point",
        )
        data = response.json()
        ts = pd.Timestamp(data["ts"]).tz_convert(tz=self.client.tz)
        if self.numeric:
            value = data["value"]
        else:
            value = self.states[data["value"]]
        return DataPoint(ts=ts, value=value)

    def _dict_to_series(self, data):
        """Converts json tag data to pandas.Series

        Maps indices to string for string tags. Also takes care to return empty series in correct format if no data
        is present.
        """

        data = pd.DataFrame(data)

        if data.empty:
            return self._empty_series()

        data["ts"] = pd.to_datetime(data["ts"], format="ISO8601")
        data.set_index("ts", inplace=True)
        data = data["value"]
        data.name = self.name

        data = data.astype(float)

        if not self.numeric:
            data = data.map(self.states)
            data = data.astype("string")

        return data

    def _empty_series(self):
        """Empty series as a tag time series data placeholder

        The datatype of the series depends on the tag type

        Returns
        -------
        pd.Series
            Empty series, though with correct name, dtype, and index type
        """
        if self.numeric:
            dtype = "float64"
        else:
            dtype = 'str'
        return pd.Series(name=self.name, dtype=dtype, index=pd.DatetimeIndex([], tz=self.client.tz))

    def _full_instance(self):
        # Loading a full tag

        # If we do not know the name, we need to load from the identifier
        if "name" in self.lazy:
            tag = TagFactory(client=self.client).from_identifier(ref=self.identifier)

            # Most likely (or even 100%?) the states are still lazy and need to loaded from another call
            if "states" in self.lazy:
                tag._update(TagFactory(client=self.client).from_name(tag.name))

        # If the tag name is known, we can use that endpoint, which loads the states
        else:
            tag = TagFactory(client=self.client).from_name(ref=self.name)

            # For some datasource types, the datasource will be set to lazy, and needs to be loaded from another call.
            if "_datasource" in tag.lazy:
                tag._update(TagFactory(client=self.client).from_identifier(ref=self.identifier))

        return tag

    def _json(self):
        raise NotImplementedError("No default json method")

    def _json_trendhub(self):
        return {
            "dataReference": {
                "description": self.description,
                "id": self.identifier,
                "name": self.name,
                "options": self._json_options(),
                "type": "TIME_SERIES",
            },
            "type": "DATA_REFERENCE",
        }

    def _json_component(self):
        return {
            "reference": self.identifier,
            "type": self.component_type,
        }

    def _json_fingerprint(self):
        return {
            "identifier": self.identifier,
            "type": "TIME_SERIES",
            "properties": {
                "interpolationType": self._interpolation_payload_str,
                "visible": self.visible,
                "shift": int(self.shift.total_seconds()),
            }
        }

    def __str__(self):
        return self.name

    def __repr__(self):
        shift_print = ""
        if self.shift.total_seconds() != 0:
            shift_print = f" | {self.shift} "
        return f"<< Tag | {self._repr_lazy('name')} {shift_print}>>"


class TagFactory(TimeSeriesFactoryBase, ComponentFactoryMixin):
    """Implements methods for tag retrieval and construction

    ``client.tag`` returns a TagFactory instance
     """
    tm_class = Tag

    def __call__(self, name, description="", units="", tag_type="ANALOG"):
        """
        Creates a new Tag instance

        The main use case to create a tag directly is when we want to upload a new csv tag.

        Parameters
        ----------
        name: str
            tag name, needs to be unique on the appliance
        description: str, default ""
            description providing additional info
        units: str, default ""
            Measurement physical units
        tag_type: {'ANALOG', 'DISCRETE' or 'STRING'}
            Type of tag

        Returns
        -------
        Tag
            Tag with the given properties. Can be imported through the csv endpoint using ``client.io.tag.post``, but
            has no immediate use other than that.
        """
        return self.tm_class(
            client=self.client,
            name=name,
            description=description,
            units=units,
            tag_type=tag_type,
            identifier=None,
            datasource=None,
            states=None,
            color=None,
            scale=None,
            shift=None,
            visible=True,
        )

    @cachetools.cached(cache=cachetools.LRUCache(maxsize=MAX_TAG_CACHE), key=FactoryBase._cache_key_ref)
    def from_identifier(self, ref):
        """Retrieve tag from its universally unique identifier (uuid)

        This function is cached. Tag metadata is not expected to change during the client lifetime.

        Parameters
        ----------
        ref : str
            Tag uuid

        Returns
        -------
        tag : Tag
            retrieved tag
        """
        if not ip.is_uuid(ref):  # saves us a request when using a name as ref
            raise ResourceNotFound(f"{ref} is not in UUID format")

        link = posixpath.join(self._endpoint, ref)
        response = self.client.session.get(link)

        return self._from_json(response.json())

    @cachetools.cached(cache=cachetools.LRUCache(maxsize=MAX_TAG_CACHE), key=FactoryBase._cache_key_ref)
    def from_name(self, ref):
        """Retrieve tag from its name

        This function is cached. Tag metadata is not expected to change during the client lifetime.

        Parameters
        ----------
        ref : str
            Tag name

        Returns
        -------
        tag : Tag
            retrieved tag
        """
        params = {"tagName": ref}
        response = self.client.session.get("hps/api/tags/details", params=params)
        return self._from_json_name(response.json())

    @cachetools.cached(cache=cachetools.LRUCache(maxsize=MAX_TAG_CACHE), key=FactoryBase._cache_key_ref)
    def from_attribute(self, ref):
        """Retrieve tag from an attribute.

        An attribute maps to a single tag.
        This function is cached. Tag metadata is not expected to change during the client lifetime.

        Parameters
        ----------
        ref : Attribute or str
            Attribute or reference to an Attribute

        Returns
        -------
        tag : Tag
            retrieved tag
        """
        from trendminer_interface.asset import AttributeFactory
        attribute = AttributeFactory(client=self.client)._get(ref)
        return attribute.tag

    def search(self, name=None, description=None, datasources=None):
        """Search tags

        Parameters
        ----------
        name : str, optional
            Tag name filter, can use '*' as wildcard
        description : str
            Tag description filter, can use '*' as wildcard
        datasources : list of Datasource, optional
            List of (references to) datasources to which to limit the search. By default, all accessible datasources are
            searched.

        Returns
        -------
        list of Tag
            tags meeting the search criteria
        """
        params = {
            "size": MAX_GET_SIZE,
            "deletedAllowed": False,
        }

        payload = {}
        filters = []
        if name is not None:
            filters.append(f"name=='{name}'")
        if description is not None:
            filters.append(f"description=='{description}'")
        if datasources is not None:
            datasources = DatasourceFactory(client=self.client)._list(datasources)
            datasource_ids = [ds.identifier for ds in datasources]
            datasource_ids_str = "('" + "','".join(datasource_ids) + "')"
            filters.append(f"datasource.id=in={datasource_ids_str}")

        if filters:
            payload.update({"query": ";".join(filters)})

        content = self.client.session.paginated(keys=["content"]).post(
            "ds/timeseries/search",
            json=payload,
            params=params
        )

        return [self._from_json(data) for data in content]

    @kwargs_to_class
    def _from_json(self, data):
        """Assemble tag from call directly to tag UUID

        returns everything except digital tag states
        """
        return {
            "identifier": data["id"],
            "name": data["name"],
            "description": data.get("description", ""),
            "units": data.get("units"),
            "tag_type": data["type"],
            "datasource": DatasourceFactory(client=self.client)._from_json_identifier_only(data["datasourceId"]),
            **default_trendhub_attributes,
        }

    @kwargs_to_class
    def _from_json_name(self, data):
        """Assemble tag from call directly to tag name

        Returns most information, including digital tag states. Does not return non-historian, non-built-in datasource
        identifier.
        """

        # What datasource information is included depends on the datasource type. For some datsource types, only the
        # type is returned, but no identifier. In that case, we need to use lazy loading for the datasource attribute.
        if "historian" in data:
            # historian datasource
            datasource = DatasourceFactory(client=self.client)._from_json_identifier_only(data["historian"]["dbId"])
        else:
            try:
                # built-in datasource
                datasource = BUILTIN_DATASOURCES[data["source"]]
            except KeyError:
                # no datasource identifier provided -> need to load tag from identifier
                datasource = LazyAttribute()


        # Create a state dictionary for string/digital tags.
        if "States" in data:
            states = {s["Code"]: s["Name"] for s in data["States"]}
        else:
            states = None

        return {
            "identifier": data["id"],
            "name": data["name"],
            "description": data.get("description", ""),
            "units": data.get("units"),
            "tag_type": data["type"],
            "datasource": datasource,
            "states": states,
            **default_trendhub_attributes,
        }

    @kwargs_to_class
    def _from_json_context_item(self, data):
        """Assemble tag from limited info returned from ContextHub components"""
        return {
            "identifier": data["reference"],
            "name": data["name"],
            "description": data.get("description", ""),
            **default_trendhub_attributes,
        }

    @kwargs_to_class
    def _from_json_calculation(self, data):
        """Assemble tag from limited info returned from a search calculation reference"""
        return {
            "identifier": data["id"],
            "name": data["name"],
            "color": None,
            "scale": None,
            "shift": data["shift"] / 1000,
            "visible": True,
        }

    @kwargs_to_class
    def _from_json_search_query(self, data):
        """Assemble tag from limited info returned from a search query reference"""
        return {
            "name": data["tagName"],
            "color": None,
            "scale": None,
            "shift": data["shift"],
            "visible": True,
        }

    @kwargs_to_class
    def _from_json_formula(self, data):
        """Assemble tag from limited info returned from a reference in a formula"""
        return {
            "identifier": data["timeSeriesDefinitionId"],
            "name": data["timeSeriesName"],
            "color": None,
            "scale": None,
            "shift": data["shift"],
            "visible": True,
        }

    @kwargs_to_class
    def _from_json_aggregation(self, data):
        return {
            "identifier": data["timeSeriesDefinitionId"],
            "name": data["timeSeriesName"],
            **default_trendhub_attributes,
        }

    @kwargs_to_class
    def _from_json_identifier_only(self, data):
        """Assemble tag only from its identifier. All other attributes will be lazy."""
        return {
            "identifier": data,
            **default_trendhub_attributes,
        }

    @kwargs_to_class
    def _from_json_name_only(self, data):
        """Assemble tag only from its name. All other attributes will be lazy."""
        return {
            "name": data,
            **default_trendhub_attributes,
        }

    @kwargs_to_class
    def _from_json_current_value_tile(self, data):
        """Assemble tag from limited data returned from current value tile"""
        return {
            "identifier": data["identifier"],
            **default_trendhub_attributes,
        }

    @kwargs_to_class
    def _from_json_index_status(self, data):
        """Assemble tag from limited data returned from tag index status"""
        return {
            "identifier": data["timeSeriesId"],
            "name": data["name"],
            **default_trendhub_attributes,
        }

    @kwargs_to_class
    def _from_json_fingerprint(self, data):
        return {
            "identifier": data["identifier"],
            "color": None,
            "scale": None,
            "shift": data["properties"]["shift"],
            "visible": data["properties"]["visible"],
        }

    @kwargs_to_class
    def _from_json_similarity_search_source(self, data):
        """From the similarity search as the source tag"""

        # MinScale can be missing when tags were auto-scaled
        # When tag has no scale, its scale is calculated from an aggregation when used in a similarity search
        if "minScale" in data:
            scale = [data["minScale"], data["minScale"]+data["range"]]
        else:
            scale = None

        return {
            "name": data["name"],
            "color": None,
            "scale": scale,
            "shift": data["shift"],
            "visible": True,
        }

    @kwargs_to_class
    def _from_json_similarity_search_target(self, data):
        """From the similarity search as the target tag"""
        return {
            "name": data["tagName"],
            "color": None,
            "scale": None,
            "shift": data["shift"],
            "visible": True,
        }

    @kwargs_to_class
    def _from_json_imported(self, data):
        """From the response when loading all imported tags"""
        return {
            "name": data["name"],
            "tag_type": data["timeSeriesType"],
            "datasource": DatasourceFactory(client=self.client)._from_json_identifier_only(
                BUILTIN_DATASOURCES["IMPORTED"]
            ),
            **default_trendhub_attributes,
        }

    @property
    def _get_methods(self):
        return self.from_identifier, self.from_name, self.from_attribute

    @property
    def index(self):
        """Interface to factory for retrieving tag statuses

        Returns
        -------
        IndexStatusFactory
            Factory for retrieving tag statuses
        """
        return IndexStatusFactory(client=self.client)

import abc
import time

import pandas as pd
import numpy as np

from trendminer_interface.base import ByFactory, kwargs_to_class
from trendminer_interface.work import WorkOrganizerObjectBase, WorkOrganizerObjectFactoryBase
from trendminer_interface.constants import SEARCH_REFRESH_SLEEP, MAX_GET_SIZE
from trendminer_interface.user import UserFactory

import trendminer_interface._input as ip

from .calculation import SearchCalculationFactory


class SearchBase(WorkOrganizerObjectBase, abc.ABC):
    """Base class for searches

    Attributes
    ----------
    search_request_identifier : str
        UUID of the latest search request, required to extract the search results. Automatically added/updated when
        executing the search.
    calculations : list of SearchCalculation
        Calculations added to the search
    identifier_complex : str
        UUID that is used for retrieving a monitor; "complexId" in the backend
    """
    search_type = abc.abstractmethod(lambda: None)
    refresh_sleep = SEARCH_REFRESH_SLEEP

    calculations = ByFactory(SearchCalculationFactory, "_list")

    def __init__(
            self,
            client,
            identifier,
            identifier_complex,
            name,
            description,
            parent,
            owner,
            last_modified,
            version,
            calculations,
    ):
        super().__init__(client=client, identifier=identifier, name=name, description=description, parent=parent,
                         owner=owner, last_modified=last_modified, version=version)

        self.search_request_identifier = None
        self.calculations = calculations
        self.identifier_complex = identifier_complex

    def _full_instance(self):
        from .client import SearchMultiFactory
        if "identifier" not in self.lazy:
            return SearchMultiFactory(client=self.client).from_identifier(self.identifier)

        # Identifier is lazy when we get a search from a monitor
        # If name is also lazy, the name is loaded when we load the monitor
        if "name" in self.lazy:
            self.get_monitor()
            assert "name" not in self.lazy

        # Retrieve potential matches by name; match exactly on the complex identifier
        return ip.object_match_nocase(
            SearchMultiFactory(client=self.client).search(ref=self.name),
            "identifier_complex",
            self.identifier_complex
        )

    @property
    @abc.abstractmethod
    def tags(self):
        """Tags used in the search"""
        pass

    def _post_updates(self, response):
        super()._post_updates(response)
        self.identifier_complex = response.json()["complexId"]

    def _put_updates(self, response):
        super()._put_updates(response)
        self.identifier_complex = response.json()["complexId"]

    def _json_definition(self):
        return {
            "calculations": [calculation._json() for calculation in self.calculations],
            "type": self.content_type,
        }

    def _execute(self, intervals):
        """Execute the search on the server

        Does not retrieve the results. Only retrieves the `search_request_identifier` attribute, allowing the results
        can be extracted with the `extract_results` method.

        Parameters
        ----------
        intervals : pandas.DataFrame
            DataFrame with IntervalIndex to search in
        """

        if intervals.interval.has_overlaps():
            raise ValueError("Search input must be none-overlapping intervals")

        interval = pd.Interval(
            left=intervals.index.left.min() + pd.Timedelta(milliseconds=int(intervals.index.closed in ["right", "neither"])),
            right=intervals.index.right.max() - pd.Timedelta(milliseconds=int(intervals.index.closed in ["left", "neither"])),
            closed=intervals.index.closed,
        )

        excluded_intervals = intervals.interval.invert(name="excluded")
        if excluded_intervals.index.closed in ["left", "both"]:
            excluded_intervals = excluded_intervals.interval.grow(left=pd.Timedelta(milliseconds=1))
        elif excluded_intervals.index.closed in ["right", "both"]:
            excluded_intervals = excluded_intervals.interval.grow(right=pd.Timedelta(milliseconds=1))

        excluded_interval_data = excluded_intervals.index.map(
            lambda x: {
                "startDate": x.left.isoformat(timespec="milliseconds"),
                "endDate": x.right.isoformat(timespec="milliseconds"),
            }
        ).to_list()

        json_search = {
            "contextTimePeriod": {
                "startDate": interval.left.isoformat(timespec="milliseconds"),
                "endDate": interval.right.isoformat(timespec="milliseconds"),
            },
            "definition": self._json_definition(),
            "exclusionPeriods": excluded_interval_data,
        }

        response = self.client.session.post("/compute/search-requests", json=json_search)

        self.search_request_identifier = response.json()["id"]

    @property
    def _empty_result_df(self):
        dtype = f"interval[datetime64[ns, {self.client.tz}], both]"
        df = pd.DataFrame(index=pd.IntervalIndex([], closed="both", dtype=dtype))
        df = self._add_missing_calc_columns(df)
        return df

    def _add_missing_calc_columns(self, df):
        """Make sure all calculation columns are present

        Fills missing columns with nan or NA values depending on the type of the Tag being calculated on
        """
        for calc in self.calculations:
            if calc.key in df:
                continue
            if calc.tag.numeric:
                df[calc.key] = np.nan
            else:
                df[calc.key] = pd.NA

        return df


    def _extract_results(self):
        """Extract the results of the latest search execution

        Uses the `search_request_identifier` attribute to extract the results. Search must have been executed first
        using the `execute` method, and execution must have finished. Readiness can be checked with the `ready` method.

        Returns
        -------
        DataFrame
            Search results, including calculations
        """
        content = self.client.session.paginated(keys=["content"]).get(
            f"/compute/search-requests/{self.search_request_identifier}/results",
            params={"size": MAX_GET_SIZE},
        )

        # Return empty DataFrame
        if not content:
            return self._empty_result_df

        df = (
            pd.DataFrame([
                {
                    "left": c["start"],
                    "right": c["end"],
                    **c["properties"],
                    **c["calculations"],
                }
                for c in content
            ])
            .drop("openEnded", axis=1)  # Remove openEnded information that comes from properties
            .assign(
                left=lambda df: pd.to_datetime(df["left"]).dt.tz_convert(self.client.tz),
                right=lambda df: pd.to_datetime(df["right"]).dt.tz_convert(self.client.tz),
            )
            .pipe(lambda df: df.set_index(
                pd.IntervalIndex.from_arrays(
                    left=df.pop("left"),
                    right=df.pop("right"),
                    closed="both",
                    name=self.name
                )
            ))
            .sort_index()
            .pipe(self._add_missing_calc_columns)
        )

        return df

    def _ready(self):
        """Checks whether the latest search execution has finished

        Results can only be retrieved after execution has finished on the server.

        Returns
        -------
        ready : bool
            Whether the latest search execution has finished
        """
        response = self.client.session.get(
            f"/compute/search-requests/{self.search_request_identifier}",
        )
        return response.json()["status"].upper() != "IN_PROGRESS"

    def get_results(self, intervals, drop=True):
        """Executes search and extracts results from the server

        Parameters
        ----------
        intervals : pandas.DataFrame or pandas.Interval
            Interval(s) to search in. If the input is a DataFrame, it must have IntervalIndex.
        drop : bool, default True
            Whether to drop the original index if `intervals` is a DataFrame

        Returns
        -------
        results : DataFrame

            DataFrame with pandas.IntervalIndex, which will have `index.left` and `index.right` the start and end
            timestamps of the result. Each result is a row in the DataFrame.

            Search calculations will be added as columns to the results. Column names will be the keys of the
            `calculations` dictionary.

            For SimilaritySearch, a `score` column with similarity score will be added (value between 0 and 100)

            If the input to `get_results` was a DataFrame with IntervalIndex, data columns of this intervals-DataFrame
            will be  preserved in the output 'results' DataFrame. I.e., every result will have the data from the
            interval it was found in. When the parameter `drop=False` is entered, the index from the intervals-DataFrame
            will be kept as a pandas.array.IntervalArray, with column name the name fo the index.

        Notes
        -----
        You can easily save search results as context items. The minimal requirements to have a valid structure for
        creating context items is to add the columns below to the DataFrame.
        - **type** (object, ContextType)
        - **component** (object, Tag or Attribute or Asset)
        For a more extensive description of the structure of context item DataFrames, check `ContextHubView.get_results`
        """

        if isinstance(intervals, pd.Interval):
            intervals = pd.IntervalIndex(data=[intervals])

        elif isinstance(intervals, pd.Series):
            intervals = pd.DataFrame([intervals])

        if isinstance(intervals, pd.IntervalIndex):
            intervals = pd.DataFrame(index=intervals)
            drop = True  # overwrite drop

        self._execute(intervals=intervals)

        time.sleep(self.refresh_sleep)
        while not self._ready():
            time.sleep(self.refresh_sleep)

        results = self._extract_results()

        # Merge original and results DataFrames
        reset_df = intervals.reset_index(drop=drop)
        if len(results) == 0:
            mapped_df = reset_df[0:0]  # required since from_records cannot handle empty index in pandas 2 (fixed in 3)
        else:
            mapped_df = pd.DataFrame.from_records(
                index=results.index,
                data=results.index.map(
                    lambda x: reset_df[intervals.index.overlaps(x)].iloc[0, :]
                )
            )

        return pd.concat([results, mapped_df], axis=1)

    def get_monitor(self):
        """Retrieve the monitor belonging to the search

        Returns
        -------
        Monitor
        """
        from trendminer_interface.monitor import MonitorFactory
        return MonitorFactory(client=self.client).from_search(self)


class SearchFactoryBase(WorkOrganizerObjectFactoryBase, abc.ABC):
    """Base factory for searches"""

    @kwargs_to_class
    def _from_json_monitor(self, data):
        """Construct search from monitor json

        For when getting monitor from search id
        """
        return {
            "identifier_complex": data["searchId"],
            "owner": UserFactory(client=self.client)._from_json_name_only(data["username"]),
            "name": data["name"],
        }

    @kwargs_to_class
    def _from_json_monitor_all(self, data):
        """Construct search from monitor json when getting a list of all monitors

        Contrary to when getting a single monitor, no info on the owner is returned. In theory, this should always be
        the `client.user`, but for robustness we only work with the info that is actually returned and leave the owner
        as a LazyAttribute.
        """
        return {
            "identifier_complex": data["searchId"],
            "name": data["name"],
        }

    @kwargs_to_class
    def _from_json_monitor_nameless(self, data):
        """Construct search from direct call to monitor ID. Does not retrieve monitor name."""
        return {
            "identifier_complex": data["searchId"],
            "owner": UserFactory(client=self.client)._from_json_name_only(data["username"]),
        }

    @kwargs_to_class
    def _from_json_filter(self, data):
        return {
            "identifier_complex": data["properties"]["searchIdentifier"],
            "name": data["properties"]["searchMetaData"]["name"],
            "description": data["properties"]["searchMetaData"]["description"]
        }

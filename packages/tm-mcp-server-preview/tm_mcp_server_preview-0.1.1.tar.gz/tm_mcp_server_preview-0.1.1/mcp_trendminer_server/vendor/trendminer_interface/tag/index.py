import pandas as pd

from trendminer_interface import _input as ip

from trendminer_interface.base import RetrievableBase, FactoryBase, LazyLoadingMixin, LazyAttribute, AsTimestamp
from trendminer_interface.authentication.response_hooks import ignore_404
from trendminer_interface.constants import INDEX_STATUS_OPTIONS, MAX_GET_SIZE
from trendminer_interface.datasource import DatasourceFactory


# TODO : add the index integration on datasource level
class IndexStatus(RetrievableBase, LazyLoadingMixin):
    """Index status for a particular tag

    The index for a tag can be considered a cache of the time series data of that tag. Once the data for a tag has been
    retrieved and cached on the appliance, it is automatically kept up-to-date from the tag datasource.

    Can only be retrieved and deleted, but not edited.

    Attributes
    ----------
    tag : Tag
        Tag for which the instance gives the index status
    status : str
        "OK", "FAILED", "INCOMPLETE", "IN_PROGRESS", "OUT_OF_DATE", "STALE", "NOT_INDEXED", "DORMANT"

        Information on what index states mean can be found here:
        https://documentation.trendminer.com/en/63122-index-manager-screen.html

        NOT_INDEXED is an artificial state, it does not exist on the appliance. It simply signifies the absence of index
        data on the appliance.
    progress : float
        Tag historic indexing progress percentage
    last_update : pandas.Timestamp or None
        Timestamp the index data was last updated
    index_start : pandas.Timestamp
         The point in time up to which the tag has been backwards indexed. For tags that have been successfully indexed,
         this date should align with the configured index horizon.
    index_end : pandas.Timestamp or None
        The time up to when the tag has received index requests.
    data_start : pandas.Timestamp
        Timestamp of the first indexed point in the TrendMiner index storage. This timestamp should be greater than or
        equal to index_start.
    data_end : pandas.Timestamp or None
        Date of the last known index point in the TrendMiner index storage. This timestamp is updated when new data
        points are added to the index, and should be smaller than or equal to the index_end.

    """
    endpoint = '/indexScheduler/indexableItems'
    # TODO: find a cleaner solution to convert to timestamp
    last_update = AsTimestamp()
    data_start = AsTimestamp()
    data_end = AsTimestamp()
    index_start = AsTimestamp()
    index_end = AsTimestamp()

    # TODO: last_update seems to be going unused

    def __init__(self, tag, status, progress, last_update, data_start, data_end, index_start, index_end):
        RetrievableBase.__init__(self, client=tag.client, identifier=tag.identifier)

        self.tag = tag
        self.status = status
        self.progress = progress
        self.last_update = last_update
        self.data_start = data_start
        self.data_end = data_end
        self.index_start = index_start
        self.index_end = index_end

    def __call__(self):
        """Sends an index request for the current tag

        If the tag was already indexed, or in the process of indexing, this request will only update the index with the
        new data available in the datasource. If no historic index data was yet present, this request will also start
        the backward indexing to retrieve the historic data.
        """
        self.client.session.post(self.endpoint, json={"timeSeriesId": self.tag.identifier})

    def _full_instance(self):
        return IndexStatusFactory(client=self.client).from_identifier(self.tag.identifier)

    def refresh(self):
        """Refreshes the index for the current tag
        """
        self.client.session.post(self.link + "/refresh")

    def delete(self):
        """Removes the index data for the current tag
        """
        self.client.session.delete(self.link)

    def _json(self):
        return {"id": self.identifier}

    def __repr__(self):
        return f"<< IndexStatus | {self._repr_lazy('status')} | {self._repr_lazy('progress')} >>"


class IndexStatusFactory(FactoryBase):
    """Implements methods for retrieval of tag index statuses

    ``client.tag.index`` returns a IndexStatusFactory instance
     """
    tm_class = IndexStatus

    def from_identifier(self, ref):
        """Retrieve index status from its uuid

        The index status uuid is equal to the tag uuid.

        Parameters
        ----------
        ref : str
            Tag uuid
        """
        response = self.client.session.get(f"{self.tm_class.endpoint}/{ref}", hooks={"response": [ignore_404]})
        if response.status_code == 404:
            return self.not_indexed(identifier=ref)
        return self._from_json(response.json())

    def not_indexed(self, identifier):
        """Returns a 'not indexed' status

        This is a placeholder status. This status does not actually exist on the server. It is the absence of an index
        status for a given tag on the appliance that tells us a tag is not indexed.

        Parameters
        ----------
        identifier : str
            uuid of the tag which is not indexed

        Returns
        -------
        IndexStatus
            'NOT INDEXED' status for tag with the given identifier
        """
        from .tag import TagFactory
        return self.tm_class(
            tag=TagFactory(client=self.client)._from_json_identifier_only(identifier),
            status="NOT_INDEXED",
            progress=0,
            last_update=None,
            data_start=None,
            data_end=None,
            index_start=None,
            index_end=None,
        )

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        IndexStatus
        """
        from .tag import TagFactory
        return self.tm_class(
            tag=TagFactory(client=self.client)._from_json_index_status(data),
            status=data["indexingDetails"]["status"],
            progress=data["indexingDetails"]["indexingProgress"],
            last_update=data["indexingDetails"].get("lastIndexUpdateAt"),
            data_start = data["indexingDetails"]["startOfData"],
            data_end = data["indexingDetails"].get("endOfData"),
            index_start = data["indexingDetails"]["startOfIndex"],
            index_end = data["indexingDetails"].get("endOfIndex"),
        )

    # TODO : get rid of lazy attributes
    def from_tag(self, tag):
        """Returns the index status for a given tag

        Parameters
        ----------
        tag : Tag or str
            A (reference to the) tag for which we want to retrieve the index status

        Returns
        -------
        IndexStatus
            Index status for the given tag
        """
        return self.tm_class(
            tag=tag,
            status=LazyAttribute(),
            progress=LazyAttribute(),
            last_update=LazyAttribute(),
            data_start=LazyAttribute(),
            data_end=LazyAttribute(),
            index_start=LazyAttribute(),
            index_end=LazyAttribute(),
        )

    def search(self, name=None, statuses=None, datasources=None, delayed=None, freq=None):
        """Search index statuses

        Parameters
        ----------
        name : str, optional
            Tag name search query
        statuses : list of str, optional
            Allowed values are "OK", "FAILED", "INCOMPLETE", "IN_PROGRESS", "OUT_OF_DATE", and "STALE"
        datasources : list of Datasource, optional
            Filter on specific datasources
        delayed : bool, optional
            Filter on only delayed or non-delayed indexes
        freq : pandas.Timedelta or tuple of Pandas.Timedelta, optional
            The configured index update frequency:
            - 2m as the monitor policy
            - 1h as a default policy
            - 24h for reduced policy
            When a tuple is given, the first value is considered the minimum, the second value the maximum.

        Returns
        -------
        list of IndexStatus
            Index statuses matching the search criteria

        Notes
        -----
        If no parameters are given, all indexes are returned.
        """
        payload = {
            "size": MAX_GET_SIZE,
            "sort": ["NAME", "ASC"],
        }

        if name is not None:
            payload["name"] = name
        if statuses is not None:
            payload["statuses"] = [ip.correct_value(status, INDEX_STATUS_OPTIONS) for status in statuses]
        if datasources is not None:
            datasources = DatasourceFactory(client=self.client)._list(datasources)
            payload["datasourceIds"] = [datasource.identifier for datasource in datasources]
        if delayed is not None:
            payload["delayed"] = delayed
        if freq is not None:
            if isinstance(freq, (list, tuple)):
                min_frequency = pd.Timedelta(freq[0])
                max_frequency = pd.Timedelta(freq[1])
            else:
                min_frequency = pd.Timedelta(freq)
                max_frequency = min_frequency
            payload["indexFrequencyInSeconds"] = {
                "min": min_frequency.total_seconds(),
                "max": max_frequency.total_seconds(),
            }

        content = self.client.session.paginated(keys=["content"]).post(
            "/indexScheduler/indexableItems/search", json=payload,
        )

        return [self._from_json(data) for data in content]

    # TODO: find a better solution for this
    def from_name(self, ref):
        """Retrieve index status from tag name

        Parameters
        ----------
        ref : str
            Name of the tag for which the retrieve the index status. Does not need to be case-sensitive.

        Returns
        -------
        IndexStatus
            Index status of the given tag
        """
        return ip.object_match_nocase(self.search(name=ref), lambda idx_status: idx_status.tag.name, ref)

    @property
    def _get_methods(self):
        return self.from_tag, self.from_identifier, self.from_name

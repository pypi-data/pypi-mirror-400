import abc
import cachetools
import posixpath
import pandas as pd

from . import _input as ip

from .constants import MAX_DATASOURCE_CACHE, MAX_GET_SIZE
from .base import RetrievableBase, FactoryBase, LazyLoadingMixin, kwargs_to_class


class DatasourceClient(abc.ABC):
    """Client for datasource factory"""

    @property
    def datasource(self):
        """Datasource factory

        Returns
        -------
        DatasourceFactory
        """
        return DatasourceFactory(client=self)


class Datasource(RetrievableBase, LazyLoadingMixin):
    """Tag datasource

    Attributes
    ----------
    name : str
        Datasource name
    description : str
        Datasource description
    capabilities : list of str
        Capability types, e.g. "TIME_SERIES"
    raw : bool
        Whether the datasource only supports raw values (plots index points only, even when zooming in).
    granularity : pandas.Timedelta
        Chunk size for historic indexing
    connector_id : str or None
        Identifier of the connector containing the datasource. `None` for built-in datasources.
    source_type : str
        Datasource type
    created_on : datetime
        Data the datsource was created
    synced_on : datetime
        Last synced date for the datasource
    provider_properties : list of str
        Provider type properties
    builtin : bool
        Whether the datasource is one of the fixed applicance datasources (e.g., Formula tags)
    """
    endpoint = "/ds/datasources/"

    def __init__(
            self,
            client,
            identifier,
            name,
            capabilities,
            description,
            raw,
            granularity,
            connector_id,
            source_type,
            created_on,
            synced_on,
            provider_properties,
            builtin,
    ):

        super().__init__(client=client, identifier=identifier)

        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.raw = raw
        self.granularity = granularity
        self.connector_id = connector_id
        self.source_type = source_type
        self.created_on = created_on
        self.synced_on = synced_on
        self.provider_properties = provider_properties
        self.builtin = builtin

    def _full_instance(self):
        return DatasourceFactory(client=self.client).from_identifier(self.identifier)

    def _json(self):
        return self.identifier

    def __repr__(self):
        return f"<< Datasource | {self._repr_lazy('name')} | {self._repr_lazy('source_type')} >>"


class DatasourceFactory(FactoryBase):
    """Factory for datasources"""
    tm_class = Datasource

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        Datasource
        """
        return self.tm_class(
            client=self.client,
            identifier=data["datasourceId"],
            name=data["name"],
            capabilities=data["capabilityTypes"],
            description=data["description"],
            raw=data["onlySupportsRawValues"],
            granularity=pd.Timedelta(days=float(data["indexingGranularity"])),
            connector_id=data["connectorId"],
            source_type=data["type"],
            created_on=pd.Timestamp(data["createOn"]).tz_convert(self.client.tz),
            synced_on=pd.Timestamp(data["syncedOn"]).tz_convert(self.client.tz),
            provider_properties=data["providerTypeProperties"],
            builtin=data["builtin"],
        )

    @kwargs_to_class
    def _from_json_identifier_only(self, data):
        """Datasource where all attributes except the identifier are lazy

        Allows creating a datasource from its identifier only, avoiding a call to retrieve the datasource info when
        not needed.

        Parameters
        ----------
        data : str
            Datasource identifier

        Returns
        -------
        Datasource
        """
        return {"identifier": data}

    def from_name(self, ref):
        """Retrieve a datasource by its name

        Parameters
        ----------
        ref : str
            Datasource name

        Returns
        -------
        Datasource
        """
        return ip.object_match_nocase(self.all(), attribute="name", value=ref)

    @cachetools.cached(cache=cachetools.LRUCache(maxsize=MAX_DATASOURCE_CACHE), key=FactoryBase._cache_key_ref)
    def from_identifier(self, ref):
        """Retrieve a datasource by its identifier

        Parameters
        ----------
        ref : str
            Datasource identifier

        Returns
        -------
        Datasource
        """
        link = posixpath.join(self._endpoint, ref)
        response = self.client.session.get(link)
        return self._from_json(response.json())

    @cachetools.cached(cache=cachetools.LRUCache(maxsize=10), key=FactoryBase._cache_key_ref)
    def all(self):
        """Retrieve all datasources

        Returns
        -------
        list of Datasource
        """
        params = {"size": MAX_GET_SIZE}
        content = self.client.session.paginated(keys=["content"]).get(self._endpoint, params=params)
        return [self._from_json(data) for data in content]

    @property
    def _get_methods(self):
        return self.from_identifier, self.from_name

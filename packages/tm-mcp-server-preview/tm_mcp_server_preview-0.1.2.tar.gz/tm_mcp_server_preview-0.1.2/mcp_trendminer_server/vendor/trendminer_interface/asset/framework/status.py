from trendminer_interface.base import RetrievableBase, FactoryBase, HasOptions, ByFactory, AsTimestamp
from trendminer_interface.constants import ASSET_FRAMEWORK_SYNC_STATES


class AssetFrameworkSync(RetrievableBase):
    """Sync status for a specific asset framework

    Can only be retrieved.

    Attributes
    ----------
    framework : AssetFramework
        Asset framework for which the status is represented
    identifier : str
        Sync status uuid. This is different from the asset framework identifier.
    name : str
        Name of the uploaded csv file. This is not the name of the asset framework. None for non-csv frameworks.
    started : pandas.Timestamp
        Sync start date
    ended : pandas.Timestamp
        Sync end time
    status : str
        "DONE", "DONE_WITH_ERRORS", "RUNNING", or "FAILED". The failed state is reserved for a technical failure to
        sync. Incorrect structures will lead to the state "DONE_WITH_ERRORS".
    """

    endpoint = '/af/source/history'
    status = HasOptions(ASSET_FRAMEWORK_SYNC_STATES)
    started = AsTimestamp()
    ended = AsTimestamp()

    def __init__(self, identifier, framework, name, started, ended, status):
        RetrievableBase.__init__(self, client=framework.client, identifier=identifier)

        self.framework = framework
        self.status = status
        self.name = name
        self.started = started
        self.ended = ended

    def _json(self):  # pragma: no cover
        raise NotImplementedError

    def __repr__(self):
        return f"<< {self.__class__.__name__} | {self.name} | {self.status} >>"


class AssetFrameworkSyncFactory(FactoryBase):
    """Implements methods for retrieval of asset framework sync statuses

    ``client.asset.framework.sync`` returns a AssetFrameworkSyncFactory instance
     """
    tm_class = AssetFrameworkSync

    def from_frameworks(self, frameworks):
        """Retrieve sync states from list of asset frameworks

        Only a single call is made to retrieve the history of multiple asset frameworks.

        Parameters
        ----------
        frameworks : list
            List of (string references to) asset frameworks. A single input element is converted to a list with one
            element.

        Returns
        -------
        list of AssetFrameworkSync
            Sync statuses for given asset frameworks
        """
        frameworks = self.client.asset.framework._list(frameworks)
        id_list = [f.identifier for f in frameworks]
        response = self.client.session.post("/af/source/history", json=id_list)

        return [self._from_json(data, framework) for data, framework in zip(response.json(), frameworks)]

    def from_framework(self, framework):
        """Retrieve sync state of a given asset framework

        Parameters
        ----------
        framework : AssetFramework
            The (string references to) the asset framework.

        Returns
        -------
        AssetFrameworkSync
            Sync status for given asset framework
        """
        return self.from_frameworks(frameworks=[framework])[0]

    def _from_json(self, data, framework=None):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json
        framework : AssetFramework or Any, optional
            The asset framework to which the sync job belongs. Can save a request to retrieve the asset framework later.

        Returns
        -------
        AssetFrameworkSync
        """
        if "syncJob" not in data:  # pragma: no cover
            # for some reason, it can happen that there is no syncJob info present
            return None
        from .framework import AssetFrameworkFactory
        if framework is None:
            framework = AssetFrameworkFactory(client=self.client)._from_json(data["source"])
        else:
            framework = AssetFrameworkFactory(client=self.client)._get(framework)
        return self.tm_class(
            identifier=data["syncJob"]["identifier"],
            framework=framework,
            name=data["syncJob"].get("name"),
            started=data["syncJob"].get("started"),
            ended=data["syncJob"].get("ended"),
            status=data["syncJob"]["status"]
        )

    def from_identifier(self, ref):
        """We could retrieve the sync status from uuid + asset framework uuid, but there is no use cases to do so"""
        raise NotImplementedError("Sync status cannot be retrieved only from its identifier")

    def all(self):
        """Retrieve all asset framework Sync statuses

        Returns
        -------
        list of AssetFrameworkSync
            All asset framework sync statuses
        """
        return self.from_frameworks(frameworks=self.client.asset.framework.all())

    def _get_methods(self):
        return self.from_framework,

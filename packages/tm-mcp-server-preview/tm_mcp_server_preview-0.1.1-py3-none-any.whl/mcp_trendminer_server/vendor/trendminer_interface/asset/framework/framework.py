import io
import time
import posixpath
import pandas as pd

from trendminer_interface import _input as ip
from trendminer_interface.base import EditableBase, FactoryBase
from trendminer_interface.constants import MAX_GET_SIZE
from trendminer_interface.download_center import DownloadCenter
from .status import AssetFrameworkSyncFactory


class AssetFramework(EditableBase):
    """
    The configuration and data behind the asset tree structure

    Attributes
    ----------
    name : str
        Asset framework name, can be edited
    identifier : str
        Asset framework uuid
    published : bool
        Whether the framework is published to the users. Can be edited.
    af_type : str
        "CSV" or "DATASOURCE". Only for csv frameworks can the structure itself be edited.
    df : pandas.DataFrame
        Asset framework csv structure, can be edited
    """
    endpoint = '/af/source'

    def __init__(
            self,
            client,
            name,
            identifier,
            ordering,
            published,
            af_type,
            df,
    ):

        EditableBase.__init__(self, client=client, identifier=identifier)

        self.name = name
        self.identifier = identifier
        self._ordering = ordering
        self.published = published
        self.af_type = af_type
        self.df = df
        self._df_original = None

    @property
    def df_original(self):
        """Get the unedited framework as downloaded from TrendMiner

        The original asset framework is downloaded with the `export` method and cannot be edited. It is kept in memory
        to check if the user has edited the framework, as we do not want to send the entire framework in a PUT request
        if it was not edited.

        Returns
        -------
        pandas.DataFrame or None
            Returns the asset framework csv if it exists hand has been loaded. Otherwise, None is returned.
        """
        return self._df_original

    @property
    def ordering(self):
        """The index in the list of asset frameworks as shown to a user

        Currently, no interface is added to change the order via the SDK (complex; low value). It has to be done in the
        UX.

        Returns
        -------
        int
            Order of the framework in list of all frameworks
        """
        return self._ordering

    @property
    def sync(self):
        """Interface to framework sync status

        Returns
        -------
        AssetFrameworkSync
            Interface to the sync state of the asset framework
        """
        return AssetFrameworkSyncFactory(client=self.client).from_framework(framework=self)

    def wait_for_sync(self, sleep=1):
        """Wait until sync of an asset framework has completed

        Parameters
        ----------
        sleep : float
            Number of seconds to wait between checks on the sync status
        """
        while True:
            sync = self.sync

            # Status might not be available directly after creation; give grace period and retry once
            if sync is None:
                time.sleep(sleep)
                sync = self.sync

            if sync.status != "RUNNING":
                break

            time.sleep(sleep)

    def _post_updates(self, response):
        super()._post_updates(response)
        self._ordering = response.json()["ordering"]

    @property
    def edited(self):
        """Checks if the framework was edited by comparing the current to the original downloaded structure

        Returns
        -------
        bool
            True if framework has been edited, otherwise False
        """
        if self.df is None:
            return False
        return not self.df.equals(self.df_original)

    def export(self):
        """Get the current framework as a pandas DataFrame under self.df"""

        response = self.client.session.get(f"/af/source/{self.identifier}/export")
        df = self._decode_csv(response)
        self.df = df
        self._df_original = df.copy()

    def _csv_data(self):
        if self.df is not None:
            return self.df.to_csv(index=False).encode("utf-8")
        else:
            return None

    def get_root_asset(self):
        """Get root asset instance associated with the asset framework"""
        return self.client.asset.from_path(self.name)

    def save(self):
        """Create a new asset framework with the current configuration"""

        # Create via csv upload
        if self.df is not None:
            response = self.client.session.post(
                self.endpoint,
                params=self._json(),
                data=self._csv_data(),
            )

        # Create via asset tree builder
        else:
            response = self.client.session.post(
                "/af/builder",
                json=self._json(),
            )

        self._post_updates(response)

    def update(self):
        """Updates asset framework with the current configuration"""
        if self.edited:
            data = self._csv_data()
        else:
            data = None

        response = self.client.session.put(
            self.link,
            params=self._json(),
            data=data,
        )

        self._put_updates(response)

    def get_errors(self):
        """Get the errors from last upload

        Returns
        -------
        pandas.DataFrame
            DataFrame of the csv of errors
        """
        nc = DownloadCenter(client=self.client, location="af")
        response = nc.download(link=f"/source/{self.identifier}/history/{self.sync.identifier}/error")
        return self._decode_csv(response)

    @staticmethod
    def _decode_csv(response):
        try:
            return pd.read_csv(io.StringIO(response.content.decode("utf-8")))

        # Empty file
        except pd.errors.EmptyDataError:
            return pd.DataFrame(
                columns=[
                    "id",
                    "path",
                    "name",
                    "description",
                    "type",
                    "template",
                    "tag",
                    "source",
                ]
            )

    def _json(self):
        return {"name": self.name, "published": self.published}

    def __repr__(self):
        return f"<< AssetFramework | {self.name} >>"

    def __str__(self):
        return self.name


class AssetFrameworkFactory(FactoryBase):
    """Implements methods for asset framework retrieval and construction

    ``client.asset.framework`` returns a AssetFrameworkFactory instance
     """
    tm_class = AssetFramework

    def __call__(self, name, published=False, df=None):
        """
        Creates a new csv asset framework that we can then post to the appliance

        The complete asset framework can be provided in a DataFrame, or the asset framework can be constructed
        step-by-step using the asset tree builder. In the latter case, start by not providing a dataframe, and simply
        creating the root asset via the `post` method. This root asset can then be provided as the parent when creating
        child assets or attributes.


        Parameters
        ----------
        name : str
            Asset framework name. This will become the name of the root asset.
        published : bool, default False
            Whether the framework is published to the users
        df : pd.DataFrame, optional
            Framework csv structure. If a csv is provided, the .post method will create the full framework at once. If
            no csv is provided, only a single root asset will be created using the asset tree builder.

        Returns
        -------
        AssetFramework
            New asset framework instance. Can be uploaded to the appliance by using the :func:`~AssetFramework.post`
            method.
        """
        return self.tm_class(
            client=self.client,
            name=name,
            identifier=None,
            ordering=None,
            published=published,
            af_type="CSV",
            df=df,
        )

    @property
    def sync(self):
        """Interface to factory for retrieving asset framework sync statuses

        Returns
        -------
        AssetFrameworkSyncFactory
            Factory for retrieving asset framework sync statuses
        """
        return AssetFrameworkSyncFactory(client=self.client)

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        AssetFramework
        """
        return self.tm_class(
            client=self.client,
            name=data["name"],
            identifier=data["identifier"],
            ordering=data.get("ordering"),  # Experimental sources without ordering can occur
            published=data["published"],
            af_type=data.get("type"),  # corrupted asset structures without type can occur
            df=None,
        )

    def all(self):
        """Retrieve all asset frameworks

        Returns
        -------
        list[AssetFramework]
            List of all asset frameworks the user has access to in TrendMiner
        """
        params = {"size": MAX_GET_SIZE}
        content = self.client.session.paginated(keys=["content"]).get(self._endpoint, params=params)
        return [self._from_json(data) for data in content]

    def from_identifier(self, ref):
        """Retrieve an asset framework from its identifier

        Parameters
        ----------
        ref : str
            Asset framework UUID

        Returns
        -------
        AssetFramework
        """
        link = posixpath.join(self._endpoint, ref)
        response = self.client.session.get(link)
        return self._from_json(response.json())

    def from_name(self, ref):
        """Get an asset framework by its name

        This requires loading all asset frameworks and then selecting the correct one, making it an expensive function
        to call often.

        Parameters
        ----------
        ref : str
            Complete name of the framework to retrieve. Correct case is not required.

        Returns
        -------
        AssetFramework
            The asset framework with the given name
        """
        return ip.object_match_nocase(self.all(), attribute="name", value=ref)

    @property
    def _get_methods(self):
        return self.from_identifier, self.from_name

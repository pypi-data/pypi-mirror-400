import abc

from trendminer_interface.base import LazyAttribute, ByFactory
from trendminer_interface.work import WorkOrganizerObjectBase, WorkOrganizerObjectFactoryBase
from trendminer_interface.fingerprint.entry import FingerprintEntryMultiFactory
from trendminer_interface.fingerprint.layer import FingerprintLayerFactory, FingerprintLayer
from trendminer_interface.tag import Tag
from trendminer_interface.folder import FolderFactory
from trendminer_interface.user import UserFactory

from .hull import FingerprintHull


class FingerprintClient(abc.ABC):
    """Client for fingerprint factory"""

    @property
    def fingerprint(self):
        """Factory for instantiating and retrieving fingerprints"""
        return FingerprintFactory(client=self)


class Fingerprint(WorkOrganizerObjectBase):
    """TrendMiner fingerprint

    Attributes
    ----------
    identifier_complex : str
        Identifier to the Fingerprint data (as opposed to the work organizer object)
    data_type : str
        Fingerprint data type. Seemingly always `LAYER_BASED`.
    entries : list of Tag or Attribute
        Entries assigned to the Fingerprint
    """

    content_type = "FINGERPRINT"
    entries = ByFactory(FingerprintEntryMultiFactory, "_list")

    def __init__(
            self,
            client,
            name,
            description,
            identifier,
            parent,
            owner,
            last_modified,
            version,
            entries,
            layers,
            identifier_complex,
            data_type,

    ):
        super().__init__(client=client, identifier=identifier, name=name, description=description, parent=parent,
                         owner=owner, last_modified=last_modified, version=version)
        self.identifier_complex = identifier_complex
        self.layers = layers
        self.data_type = data_type
        self.entries = entries

    @property
    def layers(self):
        """List of layers belonging to the Fingerprint

        Returns
        -------
            layers : list of FingerprintLayer
        """
        return self._layers

    @layers.setter
    def layers(self, layers):
        if not isinstance(layers, LazyAttribute):
            layers = FingerprintLayerFactory(client=self.client)._list(layers)
            if not any([layer.base for layer in layers]):
                layers[0].base = True
        self._layers = layers

    @property
    def tags(self):
        """List of all tags in the fingerprint

        Retrieves a list of all directly embedded tags and all tags belonging to embedded attributes

        Returns
        -------
        list of Tag
        """
        return [entry  if isinstance(entry, Tag) else entry.tag for entry in self.entries]

    def get_hulls(self):
        """Get Hulls from the saved fingerprint

        Note that the hulls are retrieved directly from TrendMiner using the `identifier_complex` attribute. The
        Fingerprint thus needs to be saved/updated in TrendMiner before we can retrieve the (correct) hulls.

        Returns
        -------
        list of FingerPrintHull
        """
        if self.identifier is None:
            raise ValueError("The fingerprint needs to be saved before hulls can be retrieved")

        r = self.client.session.get(f"/fingerprints/fingerprints/{self.identifier_complex}/result")

        return [
            FingerprintHull._from_json(
                client=self.client,
                data=data,
            )
            for data in r.json()["hulls"]
        ]

    def _full_instance(self):
        return FingerprintFactory(client=self.client).from_identifier(self.identifier)

    def _json_data(self):
        return {
            "identifier": self.identifier_complex,
            "layers": [layer._json() for layer in self.layers],
            "type": self.data_type,
            "dataReferences": [entry._json_fingerprint() for entry in self.entries],
        }

    def _post_updates(self, response):
        super()._put_updates(response)
        self.identifier_complex = response.json()["data"]["identifier"]

    def _put_updates(self, response):
        super()._put_updates(response)
        self.identifier_complex = response.json()["data"]["identifier"]


class FingerprintFactory(WorkOrganizerObjectFactoryBase):
    """Factory for creating and retrieving fingerprints"""
    tm_class = Fingerprint

    def __call__(
            self,
            entries,
            layers,
            name="New Fingerprint",
            description="",
            parent=None,
    ):
        """Instantiate a new Fingerprint instance

        Parameters
        ----------
        entries : list of Tag or Attribute
            Numeric tags or attributes to use in the fingerprint
        layers : list of FingerprintLayer or Interval
            Layers of equal length from which to construct the fingerprint
        name : str, default 'New Fingerprint'
            Work organizer name
        description : str, optional
            Work organizer description
        parent : Folder, optional
            Work organizer folder

        Returns
        -------
        Fingerprint
            New fingerprint object

        Notes
        -----
        The user needs to provide layers of equal length, otherwise an error will occur. If the desired input intervals
        are not of equal length (e.g., when coming from search results), the user needs to process them. A typical
        approach would be to truncate all layers to the length of the shortest layer.
        """
        return self.tm_class(
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
            identifier_complex=None,
            data_type="LAYER_BASED",
        )

    def _json_data(self, data):
        return {
            "entries": [
                FingerprintEntryMultiFactory(client=self.client)._from_json_fingerprint(entry)
                for entry in data["data"]["dataReferences"]
            ],
            "layers": [
                FingerprintLayerFactory(client=self.client)._from_json(layer)
                for layer in data["data"]["layers"]
            ],
            "identifier_complex": data["data"]["identifier"],
            "data_type": data["data"]["type"],
        }

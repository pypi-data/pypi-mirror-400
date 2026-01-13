import abc

from trendminer_interface.user import UserFactory
from trendminer_interface.base import AsTimestamp, EditableBase, LazyLoadingMixin, ByFactory

from .access import WorkOrganizerAccessRuleFactory


class WorkOrganizerObjectBase(EditableBase, LazyLoadingMixin, abc.ABC):
    """Superclass for objects that can be stored in the work organizer

    Attributes
    ----------
    name : str
        Object name
    description: str
        Object description
    owner : User
        The user that owns the object
    last_modified : pandas.Timestamp
        The date at which the object was last modified
    version : int, optional
        Saved version number of the object. Incremented automatically by TrendMiner.
    """
    endpoint = "/work/saveditem/"
    content_type = None
    last_modified = AsTimestamp()
    owner = ByFactory(UserFactory)

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
    ):
        EditableBase.__init__(self=self, client=client, identifier=identifier)

        self.name = name
        self.description = description
        self.parent = parent
        self.owner = owner
        self.last_modified = last_modified
        self.version = version

    @property
    def parent(self):
        """The folder in which the object is saved

        Returns
        -------
        parent : Folder
        """
        return self._parent

    @parent.setter
    def parent(self, parent):
        from trendminer_interface.folder import FolderFactory
        self._parent = FolderFactory(client=self.client)._get(parent)

    def move(self, folder):
        """Move the work organizer object to a new folder

        Parameters
        ----------
        folder : Folder
            The folder to which to move the item. None can be used to move the object to the root folder

        Returns
        -------
        None
        """
        from trendminer_interface.folder import FolderFactory
        folder = FolderFactory(client=self.client)._get(folder)

        params = {"destination": folder.identifier}

        self.client.session.put(f"/work/saveditem/{self.identifier}/move", params=params)
        self.version += 1  # Version is automatically incremented on the server upon move (but not returned by PUT)

        # Update the parent parameter after the move
        self._parent = folder

    def _post_updates(self, response):
        super()._post_updates(response)

        self.last_modified = response.json()["lastModifiedDate"]

        from trendminer_interface.folder import FolderFactory
        self._parent = FolderFactory(client=self.client)._from_json_identifier_only(response.json()["parentId"])

        self.owner = UserFactory(client=self.client)._from_json_work(response.json()["ownerUserDetails"])

        self.version = response.json()["version"]

    def _put_updates(self, response):
        super()._put_updates(response)

        self.last_modified = response.json()["lastModifiedDate"]

        from trendminer_interface.folder import FolderFactory
        self._parent = FolderFactory(client=self.client)._from_json_identifier_only(response.json()["parentId"])

        self.owner = UserFactory(client=self.client)._from_json_work(response.json()["ownerUserDetails"])

        self.version = response.json()["version"]

    @property
    def access(self):
        """Interface to factory for managing shared access to object

        Returns
        -------
        WorkOrganizerAccessRuleFactory
        """
        return WorkOrganizerAccessRuleFactory(parent=self)

    @abc.abstractmethod
    def _json_data(self, data):
        pass

    def _json(self):
        # This method is overwritten in the Folder class, which is a special case

        # We must be able to handle the case where parent is None, which implies the current user's home folder. We
        # should not attempt to replace the None with the actual home folder identifier, as this would often lead to
        # an additional API call and might trigger infinite recursion when the user's home folder is empty (cfr.
        # FolderFactory.get_home).
        parent = self.parent.identifier if self.parent is not None else None

        return {
            "identifier": self.identifier,
            "name": self.name,
            "description": self.description,
            "type": self.content_type,
            "folder": False,
            "parentId": parent,
            "data": self._json_data(),
            "version": self.version,
        }

    def __repr__(self):
        return f"<< {type(self).__name__} | {self._repr_lazy('name')} >>"

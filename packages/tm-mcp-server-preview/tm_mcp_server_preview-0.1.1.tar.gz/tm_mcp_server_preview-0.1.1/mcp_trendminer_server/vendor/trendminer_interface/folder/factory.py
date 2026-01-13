import re
import cachetools

from trendminer_interface.base import FactoryBase, kwargs_to_class, LazyAttribute
from trendminer_interface.work import WorkOrganizerObjectFactoryBase
from trendminer_interface.constants import  MAX_FOLDER_CACHE
from trendminer_interface.exceptions import ResourceNotFound
from trendminer_interface.user import UserFactory, User

from .folder import Folder


class FolderFactory(WorkOrganizerObjectFactoryBase):
    """Factory for creating and retrieving folders"""
    tm_class = Folder

    def __call__(self, name, parent=None):
        """Instantiate a new work organizer folder

        Attributes
        ----------
        name : str
            Folder name
        parent : Folder, optional
            Parent folder. Defaults to the current user's home folder

        Returns
        -------
        Folder
            New folder instance
        """
        return self.tm_class(
            client=self.client,
            identifier=None,
            name=name,
            parent=self._get(parent),
            owner=None,
            last_modified=None,
            version=None,
        )

    def _json_data(self, data):
        return {}

    @property
    def _type_filter_parameters(self):
        # Folder filtering works differently than other work organizer items
        return {
            "foldersOnly": True,
        }

    def get_home(self, user=None):
        """Get the home folder of the current user or a specified user

        Parameters
        ----------
        user : User, optional
            The user for whom to get the home folder. If None, gets the home folder of the authenticated user. Accessing
            another user's home folder requires system administrator privileges.
        """

        self_user = UserFactory(client=self.client).self
        user = UserFactory(client=self.client)._get(user)

        # If user is not specified, we need to get the home folder of authenticated user
        user = user if user is not None else self_user

        # If the authenticated user is not an admin, they can only retrieve their own work organizer, and the only way
        # to do that is to browse the work organizer and return the identifier of an item there.
        if ("tm_system_admin" not in self_user.roles) and (user.identifier == self_user.identifier):
            params = {"size": 1}
            response = self.client.session.get("/work/saveditem/browse", params=params)
            content = response.json()["_embedded"]["content"]

            # If the work organizer of the user is empty, we have a problem. The only way to retrieve the home
            # folder identifier is then to first create a temporary item in it. Note that giving a new folder parent
            # None does not try to load the home folder again (which would lead to infinite recursion).
            if len(content) == 0:
                temporary_folder = self.__call__(
                    name=".__temporary_folder_for_home_folder_retrieval__",
                    parent=None,
                )
                temporary_folder.save()
                home_folder = temporary_folder.parent
                temporary_folder.delete()
                return home_folder

            # When there is an item in the home folder, we can simply read the parentId of that item
            else:
                home_folder_id = content[0]["parentId"]
                return self._from_json_identifier_only(home_folder_id)

        # Admin users can retrieve any user's home folder directly. If the user is not an admin, but is attempting
        # to retrieve the work organizer of another user, this will fail with an authorization error.
        params={"homeFolderByUserId": user.identifier}
        response = self.client.session.get(
            "/work/saveditem/browse",
            params=params,
        )
        content = response.json()["_embedded"]["content"]
        assert len(content) == 1, "Expected exactly one home folder for the specified user"
        return self._from_json_work_organizer(content[0])

    @property
    def _home_dummy(self):
        """Dummy home folder that avoids an API call

        This dummy folder can be used in cases where a folder identifier of None would imply the home folder. It avoids
        having to load the actual home folder identifier, which can be costly.
        """
        return self.tm_class(
            client=self.client,
            identifier=None,
            name=".__home_folder_placeholder__",
            parent=None,
            owner=None,
            last_modified=None,
            version=None,
        )

    def from_path(self, ref, create_new=False, user=None):
        """Retrieve or create a folder on a given path

        Parameters
        ----------
        ref : str
            Folder path
        create_new : bool, default False
            Whether a new folder needs to be created at the given path if no folder is found there. Creates intermediate
            folders on the path too.
        user : User, optional
            The user for whom to get the home folder. If None, gets the home folder of the authenticated user. Browsing
            another user's home folder requires system administrator privileges.

        Returns
        -------
        Folder
            Folder on the given path
        """
        # Split in parts
        path = re.sub("^/", "", ref)
        parts = path.split("/")

        # Start at root folder
        if user is None:
            current_folder = self._home_dummy
        else:
            current_folder = self.get_home(user=user)


        # Iterate folders
        for part in parts:
            try:
                current_folder = current_folder.get_child_from_name(part, folders_only=True)
            except ResourceNotFound as e:
                if create_new:
                    new_folder = self.client.folder(name=part, parent=current_folder)
                    new_folder.save()
                    current_folder = new_folder
                else:
                    raise e

        return current_folder

    @cachetools.cached(cache=cachetools.LRUCache(maxsize=MAX_FOLDER_CACHE), key=FactoryBase._cache_key_ref)
    def from_identifier(self, ref):
        """Retrieve folder from its identifier

        Parameters
        ----------
        ref : str
            Folder UUID

        Returns
        -------
        Folder
        """
        return super().from_identifier(ref)

    @property
    def _get_methods(self):
        return self.from_identifier, self.from_path

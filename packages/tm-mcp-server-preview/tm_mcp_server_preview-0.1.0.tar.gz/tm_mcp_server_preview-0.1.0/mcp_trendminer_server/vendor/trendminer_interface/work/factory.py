import abc
import re
import posixpath

from trendminer_interface.user import UserFactory
from trendminer_interface.base import AuthenticatableBase, FactoryBase, kwargs_to_class, MultiFactoryBase, to_subfactory
from trendminer_interface import _input as ip


class WorkOrganizerFactoryBase(AuthenticatableBase, abc.ABC):
    """General base class for getting objects from the work organizer

    Inherited by base factory for getting work organizer objects for one specific type, and multifactory for getting
    objects that are in a provided selection of types.
    """

    @property
    @abc.abstractmethod
    def _included(self):
        """Property returning what classes need to be included in folder browsing

        Writing this to a property so that it can be overwritten for MultiFactory instances which can return work
        organizer objects of multiple types.
        """
        pass

    def from_identifier(self, ref):
        """Get instance from UUID

        Parameters
        ----------
        ref : str
            UUID string of the work organizer item

        Returns
        -------
        WorkOrganizerObjectBase
        """
        url = posixpath.join("/work/saveditem/", ref)
        response = self.client.session.get(url)
        return self._from_json(response.json())

    def from_path(self, ref, user=None):
        """Retrieve object by its full path in the work organizer structure

        Parameters
        ----------
        ref : str
            Path string, e.g. my_folder/my_subfolder/my_object
        user : User, optional
            The user for whom to get the home folder. If None, gets the home folder of the authenticated user. Browsing
            another user's home folder requires system administrator privileges.

        Returns
        -------
        Any
        """
        # Split in parts
        path = re.sub("^/", "", ref)
        parts = path.split("/")

        # Start at root folder
        from trendminer_interface.folder import FolderFactory
        if user is None:
            current_folder = FolderFactory(client=self.client)._home_dummy
        else:
            current_folder = FolderFactory(client=self.client).get_home(user=user)

        # Iterate folders
        for part in parts[0:-1]:
            current_folder = current_folder.get_child_from_name(part, folders_only=True)

        return current_folder.get_child_from_name(parts[-1], included=self._included)

    @kwargs_to_class
    def _from_json_identifier_only(self, data):
        return {"identifier": data}

    @abc.abstractmethod
    def _from_json(self):
        pass

    @abc.abstractmethod
    def _from_json_work_organizer(self):
        pass

    @property
    def _type_filter_parameters(self):
        # Separated to a property which can be overwritten by Folder, which has a different filter mechanism
        return {
            "includeTypes": [content_class.content_type for content_class in self._included],
        }

    def search(self, ref, all_users=False):
        """Search work organizer items of this type

        Parameters
        ----------
        ref : str
            Name or description search condition. The '*' can be used as a wildcard
        all_users: bool, default False
            Whether to search items from all users (True) or only from the authenticated user (False). Searching through
            items from all users requires system administrator privileges.

        Returns
        -------
        list
            Work organizer items of the given type matching the search query
        """
        params = {
            "query": ref,
            "includeData": False,
            **self._type_filter_parameters,
        }

        # The system folder needs to be assigned if we want to search through items for all users.
        # Searching for items of a specific user is currently not supported by the TrendMiner API.
        if all_users:
            params.update({"parent": "00000000-0000-0000-0000-000000000000"})

        content = self.client.session.paginated(keys=["_embedded", "content"]).get(
            url="work/saveditem/search",
            params=params
        )

        return [self._from_json_work_organizer(data) for data in content]

    def from_name(self, ref, all_users=False):
        """Retrieve work organizer item by its name

        If there are multiple items with the given name (of the same type), an error is thrown

        Parameters
        ----------
        ref : str
            work organizer name
        all_users: bool, default False
            Whether to search items from all users (True) or only from the authenticated user (False). Searching through
            items from all users requires system administrator privileges.

        Returns
        -------
        Any
            Item with matching name
        """
        partial_matches = self.search(ref=ref, all_users=all_users)
        return ip.object_match_nocase(partial_matches, attribute="name", value=ref)

    def all(self, all_users=False):
        """Retrieve all work organizer objects of this type

        Parameters
        ----------
        all_users: bool, default False
            Whether to search items from all users (True) or only from the authenticated user (False). Searching through
            items from all users requires system administrator privileges.

        Returns
        -------
        list
            Work organizer items of the given type
        """
        return self.search(ref="*", all_users=all_users)


class WorkOrganizerObjectFactoryBase(WorkOrganizerFactoryBase, FactoryBase, abc.ABC):
    """Base class for getting work organizer items of a specific type"""

    @property
    def _included(self):
        return [self.tm_class]

    def _json_work(self, data):
        """Work organizer data"""
        from trendminer_interface.folder import FolderFactory
        return {
            "identifier": data["identifier"],
            "name": data["name"],
            "description": data.get("description"),
            "parent": (
                FolderFactory(client=self.client)._from_json_identifier_only(data["parentId"])
                if "parentId" in data else None
            ),
            "last_modified": data["lastModifiedDate"],
            "owner": UserFactory(client=self.client)._from_json_work(data["ownerUserDetails"]),
            "version": data["version"],
        }

    @kwargs_to_class
    def _from_json_work_organizer(self, data):
        """Generate instances from browsing the work organizer"""
        return self._json_work(data)

    @abc.abstractmethod
    def _json_data(self):
        pass

    @kwargs_to_class
    def _from_json(self, data):
        """Generate fully enriched instance"""
        return {
            **self._json_work(data),
            **self._json_data(data),
        }

    @property
    def _get_methods(self):
        return self.from_identifier, self.from_path, self.from_name


class WorkOrganizerObjectMultiFactoryBase(MultiFactoryBase, WorkOrganizerFactoryBase, abc.ABC):
    """Base MultiFactory class for getting work organizer objects of one of a number of types"""

    @property
    def _included(self):
        return [factory.tm_class for factory in self.factories.values()]

    @to_subfactory
    def _from_json(self, data):
        """Full response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        Any
        """
        return data.get("type", "FOLDER")  # Folders do not return type field

    @to_subfactory
    def _from_json_work_organizer(self, data):
        """Limited response json from work organizer browsing"""
        return data.get("type", "FOLDER")

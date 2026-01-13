import cachetools
import posixpath
import pandas as pd

from trendminer_interface import _input as ip
from trendminer_interface.base import FactoryBase, kwargs_to_class, LazyLoadingMixin, AsTimestamp
from trendminer_interface.constants import MAX_GET_SIZE, MAX_USER_CACHE

from .base import UserBase
from .group import UserGroupFactory


class User(UserBase, LazyLoadingMixin):
    """A TrendMiner user or client user

    Attributes
    ----------
    name : str
        TrendMiner username. The username of client users is `service-account-{client id}`.
    first_name : str
        Assigned first name
    last_name : str
        Assigned last name
    roles : list of str
        Roles assigned to the User
            - default-roles-trendminer: regular user rights. Always present.
            - tm_admin: application administrator
            - tm_system_admin: ConfigHub access
            - tm_shared_space_user: Special purpose shared access user. Cannot be combined with any admin roles.
    mail : str
        User email
    created : datetime
        User creation time

    Notes
    -----
    A special Everyone-user exists which is used to give permissions to all users.
    """
    _subject_type = "USER"
    _beneficiary_type = "USER"
    endpoint = f"/auth/realms/trendminer/local/users/"
    created = AsTimestamp()

    def __init__(
        self,
        client,
        identifier,
        name,
        roles,
        mail,
        first_name,
        last_name,
        created,
    ):
        UserBase.__init__(self, client=client, identifier=identifier, name=name)
        self.first_name = first_name
        self.last_name = last_name
        self.roles = roles
        self.mail = mail
        self.created = created

    def _full_instance(self):
        if "identifier" in self.lazy:
            return UserFactory(client=self.client).from_name(ref=self.name)
        else:
            return UserFactory(client=self.client).from_identifier(ref=self.identifier)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<< User | {self._repr_lazy('name')} >>"


class UserFactory(FactoryBase):
    tm_class = User

    def __init__(self, client):
        super().__init__(client)

    @property
    def self(self):
        """Get the currently authenticated user

        Returns
        -------
        self : User
            The currently authenticated user
        """
        data = self.client.session.token_decoded
        return self.tm_class(
            client=self.client,
            identifier=data["sub"],
            name=data["preferred_username"],
            roles=data["roles"],
            mail=data.get("email"),
            first_name=data.get("given_name"),
            last_name=data.get("family_name"),
            created=pd.Timestamp(data["createdDate"], tz="UTC", unit="ms").astimezone(self.client.tz),
        )

    def from_identifier(self, ref):
        """Retrieve a user from their identifier

        Parameters
        ----------
        ref : str
            User UUID

        Returns
        -------
        User
            User with the given identifier
        """
        link = posixpath.join(self._endpoint, ref)
        response = self.client.session.get(link)
        return self._from_json(response.json())

    @cachetools.cached(cache=cachetools.LRUCache(maxsize=MAX_USER_CACHE), key=FactoryBase._cache_key_ref)
    def from_name(self, ref):
        """Retrieve a user from their name

        Parameters
        ----------
        ref : name
            User username

        Returns
        -------
        User
            User with the given username
        """

        params = {"username": ref}

        response = self.client.session.get(self.tm_class.endpoint, params=params)
        content = response.json()["_embedded"]["content"]

        # Since the call only returns exact username matches, only a single object should be returned. Nonetheless, we
        # robustly select the exact match in case multiple results are returned.
        return ip.object_match_nocase([self._from_json(data=data) for data in content], attribute="name", value=ref)

    def search(self, ref):
        """Retrieve a user by any of their properties

        Searches by username, first name, last name, and email

        Parameters
        ----------
        ref : str
            Partial match for username, first name, last name or email

        Returns
        -------
        list of User
            Users with a property matching the given search string

        Notes
        -----
        There is no endpoint for searching users by a specific property (e.g. username)

        Client users cannot be retrieved by this method. They can be retrieved by their exact name
        (`service-account-{client id}`) using the `.from_name` method.

        Searching for a first or last name with a string that includes spaces does not work.
        """
        params={
            "search": ref,
            "size": MAX_GET_SIZE
        }

        content = self.client.session.paginated(keys=["_embedded", "content"]).get(
            self.tm_class.endpoint,
            params=params
        )

        return [self._from_json(data=data) for data in content]

    @property
    def group(self):
        """Factory for retrieval of user groups

        Returns
        -------
        UserGroupFactory
        """
        return UserGroupFactory(client=self.client)

    @kwargs_to_class
    def _from_json(self, data):
        return {
            "first_name": data.get("firstName"),  # client user has no firstName/lastName
            "last_name": data.get("lastName"),
            "identifier": data["userId"],
            "name": data["username"],
            "roles": data["roles"],
            "mail": data.get("email"),
            "created": data.get("createdDate"),
        }

    @kwargs_to_class
    def _from_json_context(self, data):
        return {
            "first_name": data.get("firstName"),  # client user has no firstName/lastName
            "last_name": data.get("lastName"),
            "identifier": data["identifier"],
            "name": data["username"],
        }

    @kwargs_to_class
    def _from_json_work(self, data):
        """Work organizer ownership user representation

        Overwritten in UserMultiFactory

        Also used for user representation in ContextHub filters (but different from the rest of ContextHub)
        """
        return {
            "identifier": data["userId"],
            "name": data.get("userName"),  # System folder owner is deleted user without username
            "first_name": data.get("firstName"),  # client user has no firstName/lastName
            "last_name": data.get("lastName"),
        }

    @kwargs_to_class
    def _from_json_asset_access(self, data):
        """Asset access user representation

        Overwritten in UserMultiFactory
        """
        return {
            "identifier": data["userDetailsResource"]["userId"],
            "name": data["userDetailsResource"]["userName"],
            "first_name": data["userDetailsResource"].get("firstName"),
            "last_name": data["userDetailsResource"].get("lastName"),
        }

    @kwargs_to_class
    def _from_json_name_only(self, data):
        """Create lazy instance from only the name"""
        return {"name": data}

    @kwargs_to_class
    def _from_json_identifier_only(self, data):
        """Create lazy instance from only the identifier"""
        return {"identifier": data}

    @property
    def _get_methods(self):
        return self.from_name,

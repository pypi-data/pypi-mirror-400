from trendminer_interface import _input as ip
from trendminer_interface.base import FactoryBase
from .base import UserBase


class UserGroup(UserBase):
    _beneficiary_type = "GROUP"
    _subject_type = "EVERYONE"  # assets cannot be shared with groups other than 'everyone'

    def __repr__(self):
        return f"<< {self.__class__.__name__} | {self.name} >>"


class UserGroupFactory(FactoryBase):
    tm_class = UserGroup

    def __init__(self, client):
        super().__init__(client)

    def from_identifier(self, ref) -> UserGroup:
        """Get UserGroup by identifier

        Parameters
        ----------
        ref : str
            Identifier of the UserGroup to retrieve

        Returns
        -------
        UserGroup
            The requested UserGroup
        """
        response = self.client.session.get(
            f"/auth/realms/trendminer/groups/{ref}"
        )
        return self._from_json_work(response.json())

    def search(self, name: str) -> list[UserGroup]:
        """Search for UserGroups by name

        Parameters
        ----------
        name : str
            Name or part of the name of the UserGroups to search for

        Returns
        -------
        list of UserGroup
            List of UserGroups matching the search criteria
        """
        response = self.client.session.paginated(
            keys=["_embedded", "content"], total=False).get(
            "/auth/realms/trendminer/groups/search",
            params={"query": name, "size": 1000}
        )
        return [self._from_json_search(data) for data in response]

    def from_name(self, ref: str) -> UserGroup:
        """Get UserGroup by name

        Parameters
        ----------
        ref : str
            Name of the UserGroup to retrieve

        Returns
        -------
        UserGroup
            The UserGroup with the given name
        """
        return ip.object_match_nocase(self.search(name=ref), attribute="name", value=ref)

    def _from_json_work(self, data: dict) -> UserGroup:
        return self.tm_class(
            client=self.client,
            identifier=data["identifier"],
            name=data["name"]
        )

    def _from_json_search(self, data: dict) -> UserGroup:
        return self.tm_class(
            client=self.client,
            identifier=data["id"],
            name=data["name"]
        )

    def _from_json_asset_access(self, data: dict) -> UserGroup:
        # Asset access can only be provided for the 'Everyone' group
        assert data["subjectType"] == "EVERYONE"  # sanity check
        return self.everyone


    @property
    def everyone(self) -> UserGroup:
        """Group representing all TrendMiner users

        This group is always present. It has a fixed identifier and name.

        Returns
        -------
        everyone : UserGroup
            Group representing all TrendMiner users, with:
            - identifier: "99999999-9999-9999-9999-999999999999"
            - name: "*"

        Notes
        -----
        - This group is not retrievable from its identifier or name.
        """
        return self.tm_class(
            client=self.client,
            identifier="99999999-9999-9999-9999-999999999999",
            name="*"
        )

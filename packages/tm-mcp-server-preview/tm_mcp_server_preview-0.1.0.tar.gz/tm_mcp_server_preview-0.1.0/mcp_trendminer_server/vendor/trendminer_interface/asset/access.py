import abc
from trendminer_interface.base import EditableBase, RetrievableBase, FactoryBase, ByFactory, HasOptions
from trendminer_interface.user import UserMultiFactory, UserGroup, UserGroupFactory


class AssetAccessRuleBase(RetrievableBase, abc.ABC):
    """Access rule giving a user certain permissions to a certain Asset

    Attributes
    ----------
    parent : Asset or Attribute
        The object to which the access rule relates
    user : User or UserGroup
        The user to which the access rule relates
    permission : str
        The permission granted to the user. "ASSET_READ_CONTEXT_ITEM", "ASSET_BROWSE", or "ASSET_NO_PERMISSIONS".
    """
    user = ByFactory(UserMultiFactory)
    permission = HasOptions({
        "ASSET_BROWSE": "ASSET_BROWSE",
        "ASSET_READ_CONTEXT_ITEM": "ASSET_READ_CONTEXT_ITEM",
        "ASSET_NO_PERMISSIONS": "ASSET_NO_PERMISSIONS",
        "browse": "ASSET_BROWSE",
        "read": "ASSET_READ_CONTEXT_ITEM",
        "none": "ASSET_NO_PERMISSIONS",
    })

    def __init__(self, client, identifier, parent, user, permission):
        super().__init__(client=client, identifier=identifier)
        self.parent = parent
        self.user = user
        self.permission = permission

    @property
    def endpoint(self):
        return f"/af/asset/{self.parent.path_hex}/accessrule"

    def _json(self):

        # Backend actually expects a list
        permissions = [self.permission]

        # Asset browsing permission follows from reading context item
        if self.permission == "ASSET_READ_CONTEXT_ITEM":
            permissions.append("ASSET_BROWSE")

        return {
            "identifier": self.identifier,
            "permissions": permissions,
            "subjectType": self.user._subject_type,
            "subjectId": self.user.identifier,
        }

    def __repr__(self):
        return f"<< {self.__class__.__name__} | {self.user.name} - {self.permission} >>"


class InheritedAssetAccessRule(AssetAccessRuleBase):
    # Inherited access rule is read-only
    pass


class AssetAccessRule(AssetAccessRuleBase, EditableBase):
    # Direct access rule has save/update/delete capabilities
    pass


class AssetAccessRuleFactoryBase(FactoryBase):
    """Base factory for Asset and Attribute access rights"""
    tm_class = AssetAccessRule

    def __init__(self, parent):
        super().__init__(client=parent.client)
        self._parent = parent

    @property
    @abc.abstractmethod
    def _endpoint(self):
        pass

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        AccessRule
        """

        # Get user or user group
        user = UserMultiFactory(client=self.client)._from_json_asset_access(data)

        # Select highest permission from list
        for permission in ["ASSET_READ_CONTEXT_ITEM", "ASSET_BROWSE", "ASSET_NO_PERMISSIONS"]:
            if permission in data["permissions"]:
                break
        else:
            raise ValueError(f"Unknown permissions found in access rule data: {data['permissions']}")

        return self.tm_class(
            client=self.client,
            identifier=data["identifier"],
            parent=self._parent,
            user=user,
            permission=permission,
        )

    def all(self):
        """Retrieve all access rules for the object

        Returns
        -------
        list of AccessRule
        """
        response = self.client.session.get(self._endpoint)
        return [self._from_json(data) for data in response.json()]


class InheritedAssetAccessRuleFactory(AssetAccessRuleFactoryBase):
    """Factory for retrieving inherited access rules for an Asset or Attribute"""
    @property
    def _endpoint(self):
        return f"/af/asset/{self._parent.path_hex}/accessrule/inherited"


class AssetAccessRuleFactory(AssetAccessRuleFactoryBase):
    """Factory for managing user access to a certain Asset or Attribute"""

    @property
    def _endpoint(self):
        return f"/af/asset/{self._parent.path_hex}/accessrule"

    def add(self, user, permission):
        """Adds given permissions to the object for the given user

        Parameters
        ----------
        user : User or UserGroup
            The user who is granted the permissions, or the 'Everyone' group which grants permissions to all
        permission : str
            "ASSET_READ_CONTEXT_ITEM", "ASSET_BROWSE", or "ASSET_NO_PERMISSIONS"
        """
        user = UserMultiFactory(client=self.client)._get(user)

        # Check if a provided group is indeed 'Everyone' to avoid treating any group as 'Everyone'
        if isinstance(user, UserGroup) and not UserGroupFactory(client=self.client).everyone.identifier == user.identifier:
            raise ValueError("Access rules can only be assigned to individual users or the 'Everyone' user group.")

        rule = self.tm_class(
            client=self.client,
            identifier=None,
            parent=self._parent,
            user=user,
            permission=permission,
        )
        rule.save()

    def remove(self, user):
        """Remove rules involving specific users on the object

        Parameters
        ----------
        user : User or UserGroup
            Users for which all access rules need to be removed

        Notes
        -----
        If no rules exist for the given user, nothing happens.
        """

        user = UserMultiFactory(client=self.client)._get(user)

        existing_rules = self.all()
        matching_rules = [rule for rule in existing_rules if rule.user.identifier == user.identifier]
        for rule in matching_rules:
            rule.delete()

    def clear(self):
        """Clear all existing access rules on the object"""
        for rule in self.all():
            rule.delete()

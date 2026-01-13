from trendminer_interface.base import SerializableBase, ByFactory, HasOptions, FactoryBase
from trendminer_interface.user import UserMultiFactory


class WorkOrganizerAccessRule(SerializableBase):
    """Access rule giving a user permissions to a work organizer object

    Attributes
    ----------
    parent : Any
        The object to which the access rule relates
    user : User or UserGroup
        The user to which the access rule relates
    permission : str
        The permissions granted to the user. One of "READ", "WRITE", "OWNER".
    """
    user = ByFactory(UserMultiFactory)
    permission = HasOptions(["READ", "WRITE", "OWNER"])

    def __init__(self, client, parent, user, permission):
        super().__init__(client=client)
        self.parent = parent
        self.user = user
        self.permission = permission

    def _json(self):
        return {
            "beneficiaryId": self.user.identifier,
            "beneficiaryType": self.user._beneficiary_type,
            "permission": self.permission,
        }

    def __repr__(self):
        return f"<< {self.__class__.__name__} | {self.user.name} - {self.permission} >>"


class WorkOrganizerAccessRuleFactory(FactoryBase):
    """Factory for managing user access to a certain object"""
    tm_class = WorkOrganizerAccessRule

    def __init__(self, parent):
        super().__init__(client=parent.client)
        self._parent = parent

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        WorkOrganizerAccessRule
        """
        user = UserMultiFactory(client=self.client)._from_json_work(data["beneficiaryDetails"])

        return self.tm_class(
            client=self.client,
            parent=self._parent,
            user=user,
            permission=data["permission"],
        )

    def all(self):
        """Retrieve all access rules for the object

        Returns
        -------
        list of WorkOrganizerAccessRule
        """

        rule_data_list = self.client.session.paginated(keys=["_embedded", "content"]).get(
            url = f"/work/saveditem/{self._parent.identifier}/share",
        )
        return [self._from_json(data) for data in rule_data_list]

    def add(self, user, permission):
        """Adds given permissions to the object for the given user

        Parameters
        ----------
        user : User or UserGroup
            The user who is granted the permissions
        permission : str
            The permissions granted to the user. "READ" or "WRITE".
        """
        new_rule = self.tm_class(
            client=self.client,
            parent=self._parent,
            user=user,
            permission=permission,
        )

        existing_rules = self.all()
        existing_rules = [rule for rule in existing_rules if rule.permission != "OWNER"]  # ignore owner rule

        # TODO: check if existing rule exists for the given user, and update to the highest permission rather than letting it lead to 500 server error
        all_rules = existing_rules + [new_rule]

        self.client.session.put(
            url=f"/work/saveditem/{self._parent.identifier}/share",
            json=[rule._json() for rule in all_rules],
        )

    def remove(self, user):
        """Remove access to the work organizer object for a given user

        Parameters
        ----------
        user : User or UserGroup
            Users for which all access rules need to be removed

        Notes
        -----
        - If the given user currently does not have access, nothing happens.
        - The owner rule cannot be removed.
        """

        user = UserMultiFactory(client=self.client)._get(user)
        existing_rules = self.all()
        existing_rules = [rule for rule in existing_rules if rule.permission != "OWNER"]  # ignore owner rule

        remaining_rules = [rule for rule in existing_rules if rule.user.identifier != user.identifier]

        if len(remaining_rules) < len(existing_rules):
            self.client.session.put(
                url=f"/work/saveditem/{self._parent.identifier}/share",
                json=[rule._json() for rule in remaining_rules],
            )

    def clear(self):
        """Clear all existing access rules on the object"""
        self.client.session.put(
            url=f"/work/saveditem/{self._parent.identifier}/share",
            json=[],
        )

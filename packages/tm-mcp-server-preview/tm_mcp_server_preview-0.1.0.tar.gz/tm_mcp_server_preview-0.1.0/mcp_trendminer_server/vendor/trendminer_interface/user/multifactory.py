from trendminer_interface.base import MultiFactoryBase, to_subfactory
from .user import UserFactory
from .group import UserGroupFactory


class UserMultiFactory(MultiFactoryBase):
    """Factory for retrieving users, including the special 'everyone' user

    The UserMultiFactory is only intended to differentiate between regular and 'Everyone' users.
    """

    factories = {
        factory.tm_class._subject_type: factory
        for factory in [UserFactory, UserGroupFactory]
    }

    @to_subfactory
    def _from_json_asset_access(self, data):
        return data["subjectType"]

    @to_subfactory
    def _from_json_work(self, data):
        beneficiary_to_key = {
            factory.tm_class._beneficiary_type: key
            for key, factory in self.factories.items()
        }
        return beneficiary_to_key[data["beneficiaryType"]]

    @property
    def _get_methods(self):
        return UserFactory(client=self.client)._get_methods

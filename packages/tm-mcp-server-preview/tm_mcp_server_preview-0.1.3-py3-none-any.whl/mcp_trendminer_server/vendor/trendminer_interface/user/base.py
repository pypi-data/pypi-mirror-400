import abc
from trendminer_interface.base import RetrievableBase


class UserBase(RetrievableBase, abc.ABC):
    """Base class for users and user groups

    Attributes
    ----------
    name : str
        Name of the user
    """
    _beneficiary_type = None  # for work organizer sharing
    _subject_type = None  # for asset access rules

    def __init__(self, client, identifier, name):
        super().__init__(client=client, identifier=identifier)
        self.name = name

    def _json(self):
        return self.identifier

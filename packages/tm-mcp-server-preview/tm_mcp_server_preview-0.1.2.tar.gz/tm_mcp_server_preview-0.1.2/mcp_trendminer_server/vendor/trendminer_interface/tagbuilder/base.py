import abc
from trendminer_interface.work import WorkOrganizerObjectBase
from trendminer_interface.tag import TagFactory


class TagBuilderTagBase(WorkOrganizerObjectBase, abc.ABC):
    """Base class for tag builder tags"""

    @property
    def tag(self):
        """The tag made by the formula

        Returns
        -------
        Tag
        """
        return TagFactory(client=self.client).from_name(self.name)

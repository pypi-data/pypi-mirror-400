import abc

from trendminer_interface.tag import TagFactory
from trendminer_interface.base import SerializableBase, ByFactory


class ReferencingTagBase(SerializableBase, abc.ABC):
    """Superclass for search-related objects referencing to a tag

    Attributes
    ----------
    tag : Tag
        Reference tag
    """
    tag = ByFactory(TagFactory)

    def __init__(self, client, tag):
        super().__init__(client=client)
        self.tag = tag

    def _json(self):
        return {
            "reference": {
                "id": self.tag.identifier,
                "shift": int(self.tag.shift.total_seconds()),
                "name": self.tag.name,
                "interpolationType": self.tag._interpolation_payload_str_lower,
            }
        }

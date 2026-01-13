from trendminer_interface.base import (SerializableBase, ByFactory, TrendHubEntryMixin, TrendHubEntryFactoryBase,
                                       kwargs_to_class)
from .data_reference_factory import DataReferenceMultiFactory
from trendminer_interface.tag import Tag


class TrendHubEntryGroup(SerializableBase, TrendHubEntryMixin):
    """A grouping of two or more tags and/or attributes in TrendHub

    Grouped tags and attributes are displayed together, on the same scale

    Attributes
    ----------
    entries : list
        List of Tag and Attribute instances in the group.
    name : str
        Name of the group. Displayed in TrendHub.
    """
    entries = ByFactory(DataReferenceMultiFactory, "_list")

    def __init__(self, client, entries, name, scale=None, color=None):
        SerializableBase.__init__(self, client=client)
        TrendHubEntryMixin.__init__(self, scale=scale, color=color)
        self.entries = entries
        self.name = name

    @property
    def tags(self):
        """Get all underlying tags.

        For attribute entries, the underlying tag is given, while tag entries are simply returned as is

        Returns
        -------
        list of Tag
        """
        return [entry if isinstance(entry, Tag) else entry.tag for entry in self.entries]

    def _json_trendhub(self):
        return {
            "group": {
                "dataReferences": [entry._json_trendhub()["dataReference"] for entry in self.entries],
                "name": self.name,
                "options": {
                    "color": self.color,
                    "scale": self._json_scale(),
                },
            },
            "type": "GROUP",
        }

    def _json(self):
        raise NotImplementedError("No default json method")

    def __repr__(self):
        return f"<< GROUP | {self.name} >>"


class TrendHubEntryGroupFactory(TrendHubEntryFactoryBase):
    """Implements methods for TrendHub group retrieval and creation"""
    tm_class = TrendHubEntryGroup

    def __call__(self, entries, name="New Group", scale=None):
        """
        Create a new TrendHub group of tags and attributes

        Parameters
        ----------
        entries : list
            Tags and/or attributes
        name : str, default "New Group"
            Name of the group, as displayed in TrendHub.
        scale : list of float, optional
            [min, max] scale on the chart. Autoscaled when no value is provided.

        Returns
        -------
        TrendHubEntryGroup
        """
        return self.tm_class(
            client=self.client,
            entries=entries,
            name=name,
            scale=scale,
            color=None,
        )

    def _json_to_kwargs_trendhub(self, data):
        return {
            **super()._json_to_kwargs_options(data["options"]),
            "name": data["name"],
            "entries": [
                DataReferenceMultiFactory(client=self.client)._from_json_trendhub_group(entry)
                for entry in data["dataReferences"]
            ]
        }

    @kwargs_to_class
    def _from_json_trendhub(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        TrendHubEntryGroup
        """
        return self._json_to_kwargs_trendhub(data["group"])

    @property
    def _get_methods(self):
        return ()

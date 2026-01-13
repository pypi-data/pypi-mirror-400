from trendminer_interface.base import MultiFactoryBase, to_subfactory
from trendminer_interface.tag import TagFactory
from trendminer_interface.asset import AttributeFactory


class FingerprintEntryMultiFactory(MultiFactoryBase):
    """MuliFactory for returning tag or attribute reference in Fingerprint hull json"""

    factories = {
        "TIME_SERIES": TagFactory,
        "ATTRIBUTE": AttributeFactory,
    }

    @to_subfactory
    def _from_json_fingerprint(self, data):
        return data["type"]

    def from_tag(self, ref):
        """Get tag from a reference

        Parameters
        ----------
        ref : Any
            Tag reference

        Returns
        -------
        Tag
        """
        return TagFactory(client=self.client)._get(ref)

    def from_attribute(self, ref):
        """Get attribute from a reference

        Parameters
        ----------
        ref : Any
            Attribute reference

        Returns
        -------
        Attribute
        """
        return AttributeFactory(client=self.client)._get(ref)

    @property
    def _get_methods(self):
        return self.from_tag, self.from_attribute

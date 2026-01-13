from trendminer_interface.base import (ByFactory, kwargs_to_class, TimeSeriesMixin, TimeSeriesFactoryBase,
                                       default_trendhub_attributes)
from trendminer_interface.tag import TagFactory

from .base import AssetFrameworkNodeBase, AssetFrameworkNodeFactoryBase, LazyAttribute


class Attribute(AssetFrameworkNodeBase, TimeSeriesMixin):
    """Attributes are the end nodes of an asset framework, linking to a tag

    Attributes can be included in a TrendHub view directly.

    Attributes
    ----------
    tag : Tag
        The tag underlying the Attribute
    """
    component_type = "ATTRIBUTE"
    tag = ByFactory(TagFactory)

    def __init__(
            self,
            client,
            name,
            description,
            identifier,
            parent,
            source,
            template,
            identifier_template,
            identifier_external,
            path_hex,
            tag,
            color,
            scale,
            shift,
            visible,
    ):
        AssetFrameworkNodeBase.__init__(
            self=self,
            client=client,
            name=name,
            description=description,
            identifier=identifier,
            parent=parent,
            source=source,
            template=template,
            identifier_template=identifier_template,
            identifier_external=identifier_external,
            path_hex=path_hex,
        )

        TimeSeriesMixin.__init__(
            self=self,
            color=color,
            scale=scale,
            shift=shift,
            visible=visible,
        )

        self.tag = tag

    @property
    def _interpolation_payload_str(self):
        """Underlying tag interpolation type

        Returns
        -------
        str
            "LINEAR" or "STEPPED"
        """
        return self.tag._interpolation_payload_str

    def _json_trendhub(self):
        return {
            "dataReference": {
                "options": self._json_options(),
                "description": self.description,
                "id": self.identifier,
                "name": self.name,
                "path": self.path_hex,
                "type": self.component_type,
            },
            "type": "DATA_REFERENCE"
        }

    def _json(self):
        return {
            "name": self.name,
            "description": self.description,
            "parentPath": self.parent.path_hex,
            "tag": self.tag.name,
        }

    def _json_fingerprint(self):
        return {
            "identifier": self.identifier,
            "type": "ATTRIBUTE",
            "properties": {
                "interpolationType": self._interpolation_payload_str,
                "path": self.path_hex,
                "shift": int(self.shift.total_seconds()),
                "visible": self.visible,
            },
        }

    def _full_instance(self):
        return AttributeFactory(client=self.client).from_identifier(self.identifier)


class AttributeFactory(TimeSeriesFactoryBase, AssetFrameworkNodeFactoryBase):
    """Factory for retrieving attributes"""
    tm_class = Attribute

    def __call__(self, name, parent, tag, description=None):
        """Instantiate a new Attribute

        Instantiated attributes can be created on the appliance by an application administrator using the `post` method.

        Parameters
        ----------
        name : str
            Name of the attribute
        parent : Asset
            Parent asset under which the attribute will be placed as a child
        tag : Tag
            The tag referenced by the attribute
        description : str, optional
            Attribute description

        Returns
        -------
        Attribute
            Newly instantiated attribute
        """
        return self.tm_class(
            client=self.client,
            name=name,
            identifier=None,
            parent=parent,
            source=parent.source,
            tag=tag,
            description=description,
            identifier_external=None,
            identifier_template=None,
            path_hex=None,
            template=None,
            **default_trendhub_attributes,
        )

    def _tag_from_json(self, data):
        """Attribute tag can be deleted. In that case no time series definition is present in the response"""
        if "timeSeriesDefinition" in data:
            return TagFactory(client=self.client)._from_json(data["timeSeriesDefinition"])
        else:
            return None

    def _json_to_kwargs_browse(self, data):
        return {
            **super()._json_to_kwargs_browse(data),
            **default_trendhub_attributes,
        }

    def _json_to_kwargs(self, data):
        # A direct call to the identifier of an attribute returns the tag information. By default, this is not the case
        # when the data is retrieved by browsing (this is available as an option, but greatly reduces speed when there
        # are many attributes under an asset).
        return {
            **self._json_to_kwargs_browse(data),
            "tag": self._tag_from_json(data),
        }

    def _json_to_kwargs_trendhub(self, data):
        return {
            **super()._json_to_kwargs_trendhub(data),
            "path_hex": data["path"],
        }

    @kwargs_to_class
    def _from_json_fingerprint(self, data):
        return {
            "identifier": data["identifier"],
            "path_hex": data["properties"]["path"],
            "color": None,
            "scale": None,
            "shift": data["properties"]["shift"],
            "visible": data["properties"]["visible"],
        }

    @kwargs_to_class
    def _from_json_context_item(self, data):
        return {
            **self._json_to_kwargs_context_item(data),
            **default_trendhub_attributes,
        }

    @kwargs_to_class
    def _from_json_current_value_tile(self, data):
        return {
            "identifier": data["componentIdentifier"],
            "path_hex": data["path"],
            **default_trendhub_attributes
        }

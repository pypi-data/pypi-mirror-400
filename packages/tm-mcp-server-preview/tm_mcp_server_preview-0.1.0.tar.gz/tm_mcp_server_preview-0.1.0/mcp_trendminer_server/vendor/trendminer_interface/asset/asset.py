import posixpath

import trendminer_interface._input as ip

from trendminer_interface.constants import MAX_GET_SIZE
from trendminer_interface.base import kwargs_to_class

from .base import AssetFrameworkNodeBase, AssetFrameworkNodeFactoryBase
from .framework import AssetFrameworkFactory


class Asset(AssetFrameworkNodeBase):
    """Asset framework Asset instance

     An asset is a node in the asset framework that can be a parent to attributes or other assets
    """
    component_type = "ASSET"

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
            path_hex
    ):
        super().__init__(
            client=client,
            name=name,
            description=description,
            identifier=identifier,
            parent=parent,
            source=source,
            template=template,
            identifier_template=identifier_template,
            identifier_external=identifier_external,
            path_hex=path_hex
        )

    def _full_instance(self):
        """Account for assets with only the path known"""
        if "identifier" not in self.lazy:
            return AssetFactory(client=self.client).from_identifier(self.identifier)
        else:
            assert "path_hex" not in self.lazy
            return AssetFactory(client=self.client).from_path_hex(self.path_hex)

    def get_children(self):
        """Direct children of the asset in the asset framework.

        Children can be attributes other assets.

        Returns
        -------
        List[Union[Asset, Attribute]]
            Direct children of the current asset, which can be assets or attributes.
        """
        from .node_multifactory import NodeMultiFactory
        params = {
            "size": MAX_GET_SIZE,
            "parentPath": self.path_hex,
            "resolveTimeSeriesData": False,  # whether to retrieve associated tag metadata, big cost when True
        }
        response = self.client.session.get(
            url=posixpath.join(self.endpoint, "browse"),
            params=params
        )

        return [NodeMultiFactory(client=self.client)._from_json_browse(child) for child in response.json()["content"]]

    def get_child_from_name(self, ref):
        """Get child Asset or Attribute from its name

        Parameters
        ----------
        ref : str
            Name of the child Asset/Attribute (not case-sensitive)

        Returns
        --------
        Asset or Attribute
            Child Asset or Attribute with the corresponding name
        """
        return ip.object_match_nocase(self.get_children(), attribute="name", value=ref)

    def get_child_from_template(self, ref):
        """Get child Asset or Attribute from its template

        Parameters
        ----------
        ref : str
            Template name of the child Asset/Attribute (not case-sensitive)

        Returns
        --------
        Asset or Attribute
            Child Asset or Attribute with the corresponding template
        """
        return ip.object_match_nocase(self.get_children(), attribute="template", value=ref)

    def _json(self):
        return {
            "name": self.name,
            "description": self.description,
            "parentPath": self.parent.path_hex,
        }


class AssetFactory(AssetFrameworkNodeFactoryBase):
    """Factory for retrieving assets"""
    tm_class = Asset

    def __call__(self, name, parent, description=None):
        """Instantiate a new Asset

        Instantiated assets can be created on the appliance by an application administrator using the `post` method.

        Parameters
        ----------
        name : str
            Name of the asset
        parent : Asset
            Parent Asset under which the asset will be placed as a child
        description : str, optional
            Asset description

        Returns
        -------
        Asset
            Newly instantiated asset

        Notes
        -----
        The creation of a root asset (i.e., an asset without a parent) happens indirectly through the creation of an
        asset framework:
        >>> af = client.asset.framework(...)
        >>> af.save()
        >>> asset = af.get_root_asset()

        The new root asset can then be used as a parent for child assets:
        >>> child_asset = client.asset(name="child", parent=asset)
        >>> child_asset.save()
        """

        return self.tm_class(
            client=self.client,
            identifier=None,
            name=name,
            description=description,
            parent=parent,
            source=parent.source,
            template=None,
            identifier_template=None,
            identifier_external=None,
            path_hex=None,
        )

    @kwargs_to_class
    def _from_json_path_hex_only(self, data):
        return {"path_hex": data}

    def _json_to_kwargs_browse(self, data):
        if "ASSET_NO_PERMISSIONS" in data["permissions"]:
            return {
                "name": data["name"],
                "identifier": data["identifier"],
            }
        else:
            return super()._json_to_kwargs_browse(data)

    def _json_to_kwargs(self, data):
        # For assets, the data extracted from the direct call is the same as for browsing
        return self._json_to_kwargs_browse(data)

    @kwargs_to_class
    def _from_json_context_item(self, data):
        return self._json_to_kwargs_context_item(data)

    @property
    def framework(self):
        """Interface to factory for retrieving and creating asset frameworks

        Returns
        -------
        AssetFrameworkFactory
            Factory for retrieving retrieving and creating asset frameworks
        """
        return AssetFrameworkFactory(client=self.client)

    def roots(self):
        """All root assets

        Returns
        -------
        list of Asset
        """
        params = {
            "size": MAX_GET_SIZE,
            "parentPath": None,  # No parent for root assets
        }

        response = self.client.session.get(
            url=posixpath.join(AssetFrameworkNodeBase.endpoint, "browse"),
            params=params
        )

        return [AssetFactory(client=self.client)._from_json_browse(asset) for asset in response.json()["content"]]

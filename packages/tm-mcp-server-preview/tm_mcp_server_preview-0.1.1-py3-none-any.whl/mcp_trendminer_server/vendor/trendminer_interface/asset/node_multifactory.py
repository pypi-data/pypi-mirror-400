import posixpath

import trendminer_interface._input as ip

from trendminer_interface.base import  MultiFactoryBase, to_subfactory
from trendminer_interface.exceptions import AmbiguousResource, ResourceNotFound

from .asset import AssetFactory
from .attribute import AttributeFactory
from .base import AssetFrameworkNodeBase


class NodeMultiFactory(MultiFactoryBase):
    """Implements methods for Asset and Attribute retrieval

    ``client.asset`` returns an AssetFactory instance
     """
    factories = {
        "ASSET": AssetFactory,
        "ATTRIBUTE": AttributeFactory,
    }

    @to_subfactory
    def _from_json(self, data):
        if "type" in data:
            return data["type"]
        elif "ASSET_NO_PERMISSIONS" in data["permissions"]:
            return "ASSET"  # only assets can have no permissions
        else:  # pragma: no cover
            raise ValueError

    @to_subfactory
    def _from_json_browse(self, data):
        if "type" in data:
            return data["type"]
        elif "ASSET_NO_PERMISSIONS" in data["permissions"]:
            return "ASSET"  # only assets can have no permissions
        else:  # pragma: no cover
            raise ValueError

    def from_identifier(self, ref):
        response = self.client.session.get(posixpath.join(AssetFrameworkNodeBase.endpoint, ref))
        return self._from_json(response.json())

    # TODO: duplicates code from base.NodeFactoryBase; can be removed when eliminating ComponentFactory MultiFactory
    def from_path_hex(self, ref):
        """Returns instance (Asset or Attribute) from path with hex values

        Whether an Asset or an Attribute is returned depend on from which factory class the method is called. The same
        logic is executed in both cases, but a type check is performed at the end to avoid unexpected returns.

        Used for internal retrieval of Assets or Attributes. The difference with the `from_path` method is that the
        hexagonal path string serves as a direct identifier to the asset or attribute, and that we thus not have to
        run through the path.

        Parameters
        ----------
        ref : ref
            Hexagonal path as string, e.g. "0000025e.0000025f.00000260"

        Returns
        -------
        Asset or Attribute
            The asset or attribute at the given path
        """
        params = {"path": ref}
        response = self.client.session.get(AssetFrameworkNodeBase.endpoint, params=params)
        content = response.json()["content"]

        # For some reason the returned content is a list. There should never be more than one item returned since the
        # path should be unique, but let's check anyway.
        if len(content) > 1:  # pragma: no cover
            raise AmbiguousResource(ref)
        if len(content) == 0:  # pragma: no cover
            raise ResourceNotFound(ref)
        return self._from_json(content[0])

    # TODO: duplicates code from base.NodeFactoryBase; can be removed when eliminating ComponentFactory MultiFactory
    def from_path(self, ref):
        """Returns instance (Asset or Attribute) from human-readable path

        Whether an Asset or an Attribute is returned depend on from which factory class the method is called. The same
        logic is executed in both cases, but a type check is performed at the end to avoid unexpected returns.

        Parameters
        ----------
        ref : str
            Human readable path as text, e.g. "my_asset/my_subasset/my_attribute"

        Returns
        -------
        Asset or Attribute
            The asset or attribute at the given path
        """

        # Get root asset first
        node_name_list = [name for name in ref.split("/") if name != ""]
        node = ip.object_match_nocase(
            AssetFactory(client=self.client).roots(),
            attribute="name",
            value=node_name_list[0],
        )

        # Iterate over the rest of the path (if any)
        for node_name in node_name_list[1:]:
            node = node.get_child_from_name(node_name)

        # Return Asset or Attribute
        return node

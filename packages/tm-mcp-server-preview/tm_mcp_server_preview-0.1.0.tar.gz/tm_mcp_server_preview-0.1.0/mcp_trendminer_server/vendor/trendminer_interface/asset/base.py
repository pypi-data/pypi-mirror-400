import abc
import posixpath

import trendminer_interface._input as ip

from trendminer_interface.constants import MAX_GET_SIZE
from trendminer_interface.exceptions import ResourceNotFound, AmbiguousResource
from trendminer_interface.base import (EditableBase, LazyLoadingMixin, LazyAttribute, ByFactory, FactoryBase,
                                       kwargs_to_class, ComponentMixin, ComponentFactoryMixin)

from .access import AssetAccessRuleFactory, InheritedAssetAccessRuleFactory

from .framework import AssetFrameworkFactory


class AssetFrameworkNodeBase(EditableBase, ComponentMixin, LazyLoadingMixin, abc.ABC):
    """Abstract base class is the basis for both Assets and Attributes

    Attributes
    ----------
    name : str
        Instance name. The names of assets and attributes make up the path.
    description : str
        Instance description
    parent : Asset, optional
        Parent asset. Parent asset is None for root assets
    source : AssetFramework
        The asset framework this instance is under.
    template : str, optional
        The asset/attribute template when defined
    identifier_template : str, optional
        Identifier for the template. For a CSV asset structure, `identifier_template` is equal to `template`, which is a
        simple string of the template name. For other sources, it is the reference within the external source (for PI AF
        it is a UUID).
    identifier_external : str
        Identifier of the node in the external source. For a CSV asset framework, this is equal to the path of the node
        within the structure. For other sources, it is whatever the reference is within the external source. For
        example, for PI AF it is a UUID.
    path_hex : str
        path as a string of hexadecimal identifiers used for internal referencing
    """
    endpoint = "/af/asset/"
    component_type = abc.abstractmethod(lambda: None)
    source = ByFactory(AssetFrameworkFactory)

    # pylint: disable=too-many-arguments
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
    ):

        EditableBase.__init__(self, client=client, identifier=identifier)

        self.name = name
        self.description = description
        self.source = source
        self.parent = parent
        self.template = template
        self.identifier_template = identifier_template
        self.identifier_external = identifier_external
        self.path_hex = path_hex

        self._path = None

    def save(self):
        response = self.client.session.post(
            posixpath.join("/af/builder/", self.source.identifier, "node"),
            params={"force": False},  # TODO: to overwrite soft-deleted path we need force=True
            json=self._json(),
        )
        self._post_updates(response)

    def update(self):
        response = self.client.session.put(
            posixpath.join("/af/builder/", self.source.identifier, "node", self.identifier),
            json=self._json()
        )
        self._put_updates(response)

    def delete(self):
        response = self.client.session.delete(
            posixpath.join("/af/builder/", self.source.identifier, "node", self.identifier),
        )
        self._delete_updates(response)

    def _post_updates(self, response):
        super()._post_updates(response)
        self.identifier_external = LazyAttribute()
        self.identifier_template = LazyAttribute()
        self.path_hex = LazyAttribute()
        self.template = LazyAttribute()

    def _delete_updates(self, response):
        super()._delete_updates(response)
        self.identifier_external = None
        self.path_hex = None

    @property
    def path(self):
        """Human-readable path in the asset framework

        Returns
        -------
        str
            Human-readable path, e.g. "my_parent/this_node"
        """
        if self.source.af_type == "CSV":
            return f"{self.source.name}{self.identifier_external}"
        else:  # pragma: no cover
            names = [self.name]
            parent = self.parent
            while True:
                names.insert(0, parent.name)
                parent = parent.parent
                if parent is None:
                    break
            return "/".join(names)

    @property
    def access(self):
        """Interface to retrieving and setting access rights on the current node

        Returns
        -------
        AssetAccessRuleFactory
            Interface to retrieving and setting access rights on the current node
        """
        return AssetAccessRuleFactory(parent=self)

    @property
    def access_inherited(self):
        """Interface to retrieving access rights inherited from a parent asset

        Returns
        -------
        InheritedAssetAccessRuleFactory
            Interface to retrieving access rights inherited from a parent asset
        """
        return InheritedAssetAccessRuleFactory(parent=self)

    def _json_component(self):
        """Payload for Asset/Attribute as a context item component"""
        return {
            "type": self.component_type,
            "reference": self.identifier,
        }

    def __repr__(self):
        return f"<< {self.__class__.__name__} | {self._repr_lazy('name')} >>"

    def __str__(self):
        return self.name


class AssetFrameworkNodeFactoryBase(FactoryBase, ComponentFactoryMixin, abc.ABC):
    """Abstract base class for AssetFactory and AttributeFactory"""
    tm_class = AssetFrameworkNodeBase

    @kwargs_to_class
    def _from_json(self, data):
        return self._json_to_kwargs(data)

    @kwargs_to_class
    def _from_json_browse(self, data):
        return self._json_to_kwargs_browse(data)

    def _json_to_kwargs_browse(self, data):
        """kwargs from json obtained from browsing the asset framework"""

        if data.get("deleted", False) is True:
            source = None
            path_hex = None
            parent = None
        else:
            source = AssetFrameworkFactory(client=self.client)._from_json(data["source"])
            path_hex = data["paths"][0]
            parent_path = path_hex.rpartition(".")[0]
            if parent_path:
                from .asset import AssetFactory
                parent = AssetFactory(client=self.client)._from_json_path_hex_only(parent_path)
            else:
                parent = None

        return {
            "name": data["name"],
            "description": data.get("description"),
            "identifier": data["identifier"],
            "source": source,
            "template": data.get("template"),  # absent when there is no associated template
            "identifier_template": data.get("templateId"),  # absent when there is no associated template
            "identifier_external": data.get("externalId"),  # absent for CSV root assets
            "path_hex": path_hex,
            "parent": parent,
        }

    @abc.abstractmethod
    def _json_to_kwargs(self, data):
        """kwargs from json obtained from a direct call to the identifier"""
        pass

    def _json_to_kwargs_context_item(self, data):
        return {
            "name": data["name"],
            "description": data.get("description", ""),
            "identifier": data["reference"],
        }

    def from_identifier(self, ref):
        response = self.client.session.get(posixpath.join(self.tm_class.endpoint, ref))
        return self._from_json(response.json())

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
        from .asset import AssetFactory

        # Get root asset first
        node_name_list = [name for name in ref.split("/") if name != ""]
        node = ip.object_match_nocase(
            AssetFactory(client=self.client).roots(),
            attribute="name",
            value=node_name_list[0],
        )

        # Iterate over the rest of the path (if any)
        for node_name in node_name_list[1:]:
            new_node = node.get_child_from_name(node_name)
            new_node.parent = node  # Manually update parent with lazy attributes to parent with loaded attributes
            node = new_node

        # Type check and return the final node
        if not isinstance(node, self.tm_class):
            raise ResourceNotFound(f"Resource at '{ref}' is not of the type {self.tm_class.__name__}")

        return node

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

    def search(self, name=None, description=None, template=None, frameworks=None):
        """Search Attributes and Assets

        Whether Assets or an Attributes are returned depend on from which factory class the method is called.

        Parameters
        ---------
        name : str, optional
            Name search condition
        description : str, optional
            Description search condition
        template : str, optional
            Template search condition
        frameworks : list of AssetFramework, optional
            Asset frameworks to search in. Searches all frameworks by default.

        Returns
        -------
        list of Asset or list of Attribute
            List of assets or attributes matching the search conditions
        """
        payload = {"size": MAX_GET_SIZE}
        filters = [f"type=='{self.tm_class.component_type}'"]  # filter on asset/attribute
        if name is not None:
            filters.append(f"name=='{name}'")
        if description is not None:
            filters.append(f"description=='{description}'")
        if template is not None:
            filters.append(f"template=='{template}'")
        if frameworks is not None:
            frameworks = AssetFrameworkFactory(client=self.client)._list(frameworks)
            framework_ids = [af.identifier for af in frameworks]
            framework_ids_str = "('" + "','".join(framework_ids) + "')"
            filters.append(f"source.identifier=in={framework_ids_str}")

        if filters:
            payload.update({"query": ";".join(filters)})

        paginator = self.client.session.paginated(keys=["content"], json_params=True)
        content = paginator.post(
            url=posixpath.join(self.tm_class.endpoint,"search"),
            json=payload,
        )

        return [self._from_json(data) for data in content]

    @property
    def _get_methods(self):
        return (
            self.from_identifier,
            self.from_path_hex,
            self.from_path
        )

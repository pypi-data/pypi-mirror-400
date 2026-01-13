import trendminer_interface._input as ip

from trendminer_interface.base import LazyLoadingMixin, EditableBase, ByFactory, kwargs_to_class, ColorPicker, HasOptions
from trendminer_interface.constants import CONTEXT_ICON_OPTIONS, MAX_GET_SIZE

from .configuration_factory_base import ContextConfigurationFactoryMixin
from .workflow import ContextWorkflowFactory
from .field import ContextFieldFactory


class ContextType(EditableBase, LazyLoadingMixin):
    """Context item type

    Attributes
    ----------
    key : str
        Context type unique key. Context types do not have uuids
    name : str
        Context type name visible to the user. Does not need to be unique.
    workflow : ContextWorkflow
        The workflow associated with the context type
    fields : list of ContextField
        The context fields associated with the context type
    icon : str
        Icon associated with the context type: "alert--circle", "arrows--round", "bucket", "circle-success",
        "clipboard", "cracked", "file--check", "flame", "flask", "flow--line", "information", "person", "ruler",
        "snowflake", "spoon", "trending--down", "warning", "waterdrops", "waves", "wheelbarrow", or "wrench".
    color : str
        Context type color as a string (e.g. "#F0A3FF")
    approvals_enabled : bool
        Whether context items of this type can be approved
    audit_trail_enabled : bool
        Whether context item edit history will be saved as metadata to the item
    """
    endpoint = "context/type/"
    workflow = ByFactory(ContextWorkflowFactory)
    fields = ByFactory(ContextFieldFactory, "_list")
    color = ColorPicker()
    icon = HasOptions(CONTEXT_ICON_OPTIONS)

    def __init__(self, client, key, name, workflow, fields, icon, color, approvals_enabled, audit_trail_enabled):
        EditableBase.__init__(self, client=client, identifier=key)

        self.key = key
        self.name = name
        self.workflow = workflow
        self.fields = fields
        self.icon = icon
        self.color = color
        self.approvals_enabled = approvals_enabled
        self.audit_trail_enabled = audit_trail_enabled

    def _full_instance(self):
        return ContextTypeFactory(client=self.client).from_key(self.key)

    def _json(self):
        payload = {
            "identifier": self.key,
            "name": self.name,
            "fields": [field._json() for field in self.fields],
            "icon": self.icon,
            "color": self.color[1:],  # context type color does not contain the initial '#'
            "approvalsEnabled": self.approvals_enabled,
            "auditTrailEnabled": self.audit_trail_enabled,
        }

        if self.workflow is not None:
            payload.update({"workflow": self.workflow._json()})

        return payload

    def __str__(self):
        return self.key

    def __repr__(self):
        return f"<< {self.__class__.__name__} | {self._repr_lazy('key')} >>"


class ContextTypeFactory(ContextConfigurationFactoryMixin):
    """Factory for creating and retrieving context types"""
    tm_class = ContextType

    def __call__(self, key, name, workflow=None, fields=None, icon="information", color=None, approvals_enabled=False,
                 audit_trail_enabled=False):
        """Create new context type

        Parameters
        ----------
        key : str
            Context type unique key. Context types do not have uuids
        name : str
            Context type name visible to the user. Does not need to be unique.
        workflow : ContextWorkflow or str, optional
            The workflow associated with the context type
        fields : list of ContextField or list of str
            The context fields associated with the context type
        color : str, optional
            The context type color (e.g. "#F0A3FF"). If no value is entered, a random value is assigned.
        icon : str, default "information"
            Icon associated with the context type: "alert--circle", "arrows--round", "bucket", "circle-success",
            "clipboard", "cracked", "file--check", "flame", "flask", "flow--line", "information", "person", "ruler",
            "snowflake", "spoon", "trending--down", "warning", "waterdrops", "waves", "wheelbarrow", or "wrench".
        approvals_enabled : bool, default False
            Whether context items of this type can be approved
        audit_trail_enabled : bool, default False
            Whether context item edit history will be saved as metadata to the item
        """
        return self.tm_class(
            client=self.client,
            key=key,
            name=name,
            workflow=workflow,
            fields=fields,
            icon=icon,
            color=color,
            approvals_enabled=approvals_enabled,
            audit_trail_enabled=audit_trail_enabled,
        )

    def from_key(self, ref):
        """Retrieve context type from its unique key

        Parameters
        ----------
        ref : str
            The context item unique key

        Returns
        -------
        ContextType
            The corresponding context type
        """
        return self.from_identifier(ref)

    def from_name(self, ref):
        """Retrieve context type from its name

        Parameters
        ----------
        ref : str
            The context type name

        Returns
        -------
        ContextType
            The corresponding context type
        """
        return ip.object_match_nocase(self.search(name=ref), attribute="name", value=ref)

    def search(self, key=None, name=None):
        """Search context types

        Parameters
        ----------
        key : str
            Context type key search query
        name : str
            Context type name search query

        Returns
        -------
        list of ContextType
            Context types matching the search conditions
        """
        params = {"size": MAX_GET_SIZE}

        filters = []
        if key is not None:
            filters.append(f"identifier=='{key}'")
        if name is not None:
            filters.append(f"name=='{name}'")

        if filters:
            params.update({"query": ";".join(filters)})

        content = self.client.session.paginated(keys=["content"]).get("/context/type/search", params=params)

        return [self._from_json(data) for data in content]

    def _json_to_kwargs_base(self, data):
        return {
            "key": data["identifier"],
            "name": data["name"],
            "color": "#"+data["color"],  # context type color value does not contain the '#'
            "icon": data["icon"],
            "approvals_enabled": data["approvalsEnabled"],
            "audit_trail_enabled": data["auditTrailEnabled"],
        }

    @kwargs_to_class
    def _from_json(self, data):

        workflow = data.get("workflow")
        if workflow:
            workflow=ContextWorkflowFactory(client=self.client)._from_json(workflow)

        return {
            **self._json_to_kwargs_base(data),
            "workflow": workflow,
            "fields": [
                ContextFieldFactory(client=self.client)._from_json(field)
                for field in data["fields"]
            ],
        }

    @kwargs_to_class
    def _from_json_context_filter(self, data):
        return self._json_to_kwargs_base(data)

    @property
    def _get_methods(self):
        return self.from_key, self.from_name

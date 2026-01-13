from trendminer_interface import _input as ip
from trendminer_interface.base import EditableBase, HasOptions
from trendminer_interface.constants import CONTEXT_FIELD_OPTIONS, MAX_GET_SIZE

from .configuration_factory_base import ContextConfigurationFactoryMixin


class ContextField(EditableBase):
    """Context field structure

    A ContextField instance gives the structure of a context field, it does not represent a single field+value on a
    context item. Context item field values are given as a dict by `ContextItem.fields`, where the key in the dict must
    match the key of the corresponding ContextField instance.

    Attributes
    ----------
    name : str
        Name that is visible to the users in the appliance
    key : str
        Key that is used as the main identifier of the field. Needs to be unique.
    field_type : {"ENUMERATION", "STRING", "NUMERIC"}
        Context field type. Determines what type of values the field can take.
    placeholder : str
        Field placeholder that is displayed to the user if the field is blank. This is NOT a default value, it is a
        visual aid to the user.
    """
    endpoint = "context/fields/"
    field_type = HasOptions(CONTEXT_FIELD_OPTIONS)

    def __init__(self, client, identifier, field_type, name, key, placeholder, options):
        super().__init__(client, identifier=identifier)
        self.name = name
        self.key = key
        self.field_type = field_type
        self.placeholder = placeholder
        self.options = options

    @property
    def options(self):
        """Get field options. Returns None if field is not of type ENUMERATION

        Returns
        -------
        options : list of str, optional
            Options for enumeration fields
        """
        return self._options

    @options.setter
    def options(self, options):
        options = options or []
        if not (self.field_type == "ENUMERATION") and options != []:
            raise ValueError(
                f"Context field of type {self.field_type} does not take options"
            )
        self._options = [str(i) for i in options]

    def _json(self):
        """post/put request payload for saving context field"""
        payload = {
            "identifier": self.identifier,
            "propertyKey": self.key,
            "name": self.name,
            "type": self.field_type,
            "placeholder": self.placeholder,
        }
        if self.field_type == "ENUMERATION":
            payload.update({"options": self.options})
        return payload

    def __str__(self):
        return self.key

    def __repr__(self):
        return f"<< ContextField | {self.key} >>"


class ContextFieldFactory(ContextConfigurationFactoryMixin):
    """Factory for creating and retrieving context fields"""
    tm_class = ContextField

    def __call__(self, key, name, field_type="STRING", placeholder="", options=None):
        """Create new context field

        Parameters
        ----------
        key : str
            Context field unique key
        name : str
            Context field name
        field_type : str, default "STRING"
            "STRING", "ENUMERATION" or "NUMERIC"
        placeholder : str
            Placeholder displayed in empty field (NOT a default value)
        options : list of str, optional
            List of options for enumeration type field
        """
        return self.tm_class(client=self.client,
                             identifier=None,
                             field_type=field_type,
                             name=name,
                             key=key,
                             placeholder=placeholder,
                             options=options,
                             )

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        ContextField
        """
        return self.tm_class(
            client=self.client,
            identifier=data["identifier"],
            field_type=data["type"],
            name=data["name"],
            key=data["propertyKey"],
            placeholder=data.get("placeholder"),
            options=data.get("options"),
        )

    def search(self, key=None, name=None):
        """Search context fields

        Parameters
        ----------
        key : str, optional
           Field key search condition. Can use the '*' symbol as wildcard.
        name : str, optional
            Field name search condition. Can use the '*' symbol as wildcard.

        Returns
        -------
        list of ContextField
            Context fields matching the search conditions
        """
        params = {"size": MAX_GET_SIZE}

        filters = []
        if key is not None:
            filters.append(f"propertyKey=='{key}'")
        if name is not None:
            filters.append(f"name=='{name}'")

        if filters:
            params.update({"query": ";".join(filters)})

        content = self.client.session.paginated(keys=["content"]).get(self._endpoint + "search", params=params)

        return [self._from_json(data) for data in content]

    def from_key(self, ref):
        """Retrieve context field by its unique key

        Parameters
        ----------
        ref : str
            Context field key
        """
        return ip.object_match_nocase(self.search(key=ref), attribute="key", value=ref)

    def from_name(self, ref):
        """Retrieve context field by its name

        Parameters
        ----------
        ref : str
            Context field name

        Returns
        -------
        ContextField
            Context field with the given name
        """
        return ip.object_match_nocase(self.search(name=ref), attribute="name", value=ref)

    @property
    def _get_methods(self):
        return self.from_identifier, self.from_key, self.from_name

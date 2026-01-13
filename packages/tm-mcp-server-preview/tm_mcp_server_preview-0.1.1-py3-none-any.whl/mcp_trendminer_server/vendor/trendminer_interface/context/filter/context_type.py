from trendminer_interface.base import ByFactory, FactoryBase
from trendminer_interface.context.filter.base.filter import ContextFilterBase
from trendminer_interface.context.type import ContextTypeFactory


class TypeFilter(ContextFilterBase):
    """Filter on context types

    Attributes
    ----------
    context_types : list
        List of (reference to) ContextType
    """
    filter_type = "TYPE_FILTER"
    context_types = ByFactory(ContextTypeFactory, "_list")

    def __init__(self, client, context_types):
        super().__init__(client=client)
        self.context_types = context_types

    def _json(self):
        return {
            **super()._json(),
            "types": [context_type.key for context_type in self.context_types]
        }


class TypeFilterFactory(FactoryBase):
    """Factory for creating context type filters"""
    tm_class = TypeFilter

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        TypeFilter
        """
        return self.tm_class(
            client=self.client,
            context_types=[
                ContextTypeFactory(client=self.client)._from_json_context_filter(context_type)
                for context_type in data["typeResources"]
                ],
        )

    def __call__(self, context_types):
        """Create new context type filter

        Parameters
        ----------
        context_types : list
            Context types on which to filter
        """
        return self.tm_class(client=self.client, context_types=context_types)

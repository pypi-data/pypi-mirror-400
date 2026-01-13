import abc


class ComponentMixin(abc.ABC):
    """Mixin class with placeholders for ContextHub components"""
    component_type = abc.abstractmethod(lambda: None)

    @abc.abstractmethod
    def _json_component(self):
        """Payload as a context item component"""
        pass


class ComponentFactoryMixin(abc.ABC):
    """Mixin class with placeholders for component factory classes"""

    @abc.abstractmethod
    def _from_json_context_item(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        Any
        """
        pass

from trendminer_interface.base import ByFactory
from trendminer_interface.component_factory import ComponentMultiFactory
from trendminer_interface.context import ContextTypeFactory
from .base import MonitorNotificationBase


class ContextItemMonitorNotification(MonitorNotificationBase):
    """Context item monitor notification

    Attributes
    ----------
    context_type : ContextType, optional
        The context item type
    component : Tag or Attribute or Asset, optional
        The component the item will be attached to
    description : str, optional
        The context item description
    fields : dict, optional
        The context item fields
    keywords : list of str, optional
        The keywords attached to the context item
    """

    context_type = ByFactory(ContextTypeFactory)
    component = ByFactory(ComponentMultiFactory)

    def __init__(self, monitor, enabled, enabled_at, context_type, component, description, fields, keywords):
        super().__init__(monitor, enabled, enabled_at)
        self.context_type = context_type
        self.component = component
        self.description = description
        self.fields = fields
        self.keywords = keywords

    @classmethod
    def _from_json(cls, monitor, data):
        """Response json to instance

        Attributes
        ----------
        monitor : Monitor
            monitor on which the notification is configured
        data : dict
            response json

        Returns
        -------
        ContextItemMonitorNotification
        """
        return cls(
            monitor=monitor,
            enabled=data["enabled"],
            enabled_at=data["enabledAt"],
            context_type=data["type"],
            component=data["componentReference"],
            fields=data["fields"],
            keywords=data["keywords"],
            description=data.get("description"),
        )

    def _json(self):
        # TODO: should generate lazy attributes
        return {
            **super()._json(),
            "componentReference": self.component.identifier if self.component else None,
            "componentType": self.component.component_type if self.component else None,
            "description": self.description,
            "fields": self.fields,
            "keywords": self.keywords,
            "type": self.context_type.key if self.context_type else None,
        }

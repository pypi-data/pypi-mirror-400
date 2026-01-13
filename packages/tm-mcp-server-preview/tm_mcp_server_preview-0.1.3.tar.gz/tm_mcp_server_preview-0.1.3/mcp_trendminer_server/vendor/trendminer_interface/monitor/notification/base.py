import abc
from trendminer_interface.base import SerializableBase, AsTimestamp


class MonitorNotificationBase(SerializableBase, abc.ABC):
    """Base class for monitor notifications

    Attributes
    ----------
    enabled : bool
        Whether the notification is enabled
    enabled_at : datetime
        What time the notification was enabled
    """
    enabled_at = AsTimestamp()

    def __init__(self, monitor, enabled, enabled_at):
        super().__init__(client=monitor.client)
        self.enabled = enabled
        self.enabled_at = enabled_at

    def _json(self):
        return {
            "enabled": self.enabled,
        }


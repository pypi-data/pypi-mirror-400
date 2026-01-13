from .base import MonitorNotificationBase


class WebhookMonitorNotification(MonitorNotificationBase):
    def __init__(self, monitor, enabled, enabled_at, url):
        super().__init__(monitor, enabled, enabled_at)
        self.url = url

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
        WebhookMonitorNotification
        """
        return cls(
            monitor=monitor,
            enabled=data["enabled"],
            enabled_at=data.get("enabledAt"),
            url=data["url"],
        )

    def _json(self):
        return {
            **super()._json(),
            "url": self.url,
        }
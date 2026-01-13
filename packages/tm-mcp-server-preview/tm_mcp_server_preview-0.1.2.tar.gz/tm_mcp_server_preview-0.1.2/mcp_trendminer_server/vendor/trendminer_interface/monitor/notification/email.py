from .base import MonitorNotificationBase


class EmailMonitorNotification(MonitorNotificationBase):
    """Monitor email notfication"""

    def __init__(self,
                 monitor,
                 enabled,
                 enabled_at,
                 subject,
                 message,
                 to,
                 ):
        super().__init__(monitor=monitor, enabled=enabled, enabled_at=enabled_at)
        self.subject = subject
        self.message = message
        self.to = to

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
        EmailMonitorNotification
        """
        return cls(
            monitor=monitor,
            enabled=data["enabled"],
            enabled_at=data["enabledAt"],
            subject=data["subject"],
            message=data["message"],
            to=data["to"],
        )

    def _json(self):
        return {
            **super()._json(),
            "subject": self.subject,
            "message": self.message,
            "to": self.to,
        }
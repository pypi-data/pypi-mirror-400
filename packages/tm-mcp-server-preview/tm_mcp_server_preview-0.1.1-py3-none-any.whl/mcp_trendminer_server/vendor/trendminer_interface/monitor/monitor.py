import posixpath
import pandas as pd

from trendminer_interface.base import FactoryBase, kwargs_to_class, RetrievableBase
from trendminer_interface.base import LazyLoadingMixin, LazyAttribute, AsTimestamp
from trendminer_interface import _input as ip
from trendminer_interface.search import SearchMultiFactory, search_type_to_content_type

from .notification import WebhookMonitorNotification, EmailMonitorNotification, ContextItemMonitorNotification


class Monitor(RetrievableBase, LazyLoadingMixin):
    """Search-based monitor"""
    endpoint = '/hps/api/monitoring/'

    created = AsTimestamp()
    last_modified = AsTimestamp()

    def __init__(
            self,
            client,
            identifier,
            enabled,
            created,
            last_modified,
            search,
            state,
            monitor_dependency,  # is this monitor a trigger for another monitor (fingerprint deviation)
            webhook,
            email,
            context,
    ):
        RetrievableBase.__init__(self=self, client=client, identifier=identifier)

        self.enabled = enabled
        self.search = search
        self.created = created
        self.last_modified = last_modified
        self.state = state
        self.monitor_dependency = monitor_dependency
        self.webhook = webhook
        self.email = email
        self.context = context

    @property
    def identifier(self):
        """Monitor identifier

        Not a UUID, just simple sequential numbering. Converted to string for compatibility.

        Returns
        -------
        identifier : str
        """
        return self._identifier

    @identifier.setter
    def identifier(self, identifier):
        if identifier not in [None, LazyAttribute]:
            identifier = str(identifier)
        self._identifier = identifier

    @property
    def name(self):
        """Monitor name

        Identical to the name of the underlying search

        Returns
        -------
        name : str
            Monitor name
        """
        return self.search.name

    def update(self):
        """Update existing search with the current configuration"""

        # Update the item
        # TODO: no _put_updates? Better to do them but to leave them blank
        response = self.client.session.put(self.link, json=self._json())

        # Reset content containing last updated info
        self.last_modified = LazyAttribute()
        self.webhook = LazyAttribute()
        self.email = LazyAttribute()
        self.context = LazyAttribute()

        # Separate request required to enable/disable monitor
        if self.enabled:
            self.client.session.post(f"/hps/api/monitoring/status/{self.identifier}")
        else:
            self.client.session.delete(f"/hps/api/monitoring/status/{self.identifier}")

    def _full_instance(self):
        if "search" not in self.lazy:
            return MonitorFactory(client=self.client).from_search(self.search)
        else:
            return MonitorFactory(client=self.client).from_identifier(self.identifier)

    def _json(self):
        return {
            "contextItemNotification": self.context._json(),
            "created": self.created.isoformat(timespec="milliseconds"),
            "emailNotification": self.email._json(),
            "enabled": self.enabled,
            "id": int(self.identifier),
            "isMonitoringPatternDependency": self.monitor_dependency,
            "lastUpdatedDate": pd.Timestamp.utcnow().isoformat(timespec="milliseconds"),  # TODO: probably does not make sense to set 'last updated' manually
            "name": self.name,
            "searchId": self.search.identifier_complex,
            "state": self.state,
            "type": self.search.search_type,
            "username": self.search.owner.name,
            "webhookNotification": self.webhook._json(),
            # "tags" also given from UX put request, but is filled automatically when not provided
        }

    def __repr__(self):
        return f"<< {self.__class__.__name__} | {self._repr_lazy('identifier')} >>"


class MonitorFactory(FactoryBase):
    """Factory for retrieving monitors"""
    tm_class = Monitor

    def _json_to_kwargs_base(self, data):
        return {
            "identifier": data["id"],
            "enabled": data["enabled"],
            "created": data["created"],
            "last_modified": data["lastUpdatedDate"],
            "state": data["state"],
        }

    def _json_to_kwargs_notifications(self, data):
        return {
            "webhook": WebhookMonitorNotification._from_json(
                monitor=self,
                data=data.get("webhookNotification", {"enabled": False, "url": ""})
            ),
            "email": EmailMonitorNotification._from_json(
                monitor=self,
                data=data["emailNotification"]
            ),
            "context": ContextItemMonitorNotification._from_json(
                monitor=self, data=data["contextItemNotification"]
            ),
        }

    @kwargs_to_class
    def _from_json_full(self, data):
        """Getting data from search ID gives full overview"""
        return {
            **self._json_to_kwargs_base(data),
            **self._json_to_kwargs_notifications(data),
            "search": SearchMultiFactory(client=self.client)._from_json_monitor(data),
            "monitor_dependency": data["isMonitoringPatternDependency"],
        }

    @kwargs_to_class
    def _from_json_all(self, data):
        """from structure when requesting overview of all monitors"""
        return {
            **self._json_to_kwargs_base(data),
            "search": SearchMultiFactory(client=self.client)._from_json_monitor_all(data),
        }

    @kwargs_to_class
    def _from_json(self, data):
        """from structure when getting monitor directly from identifier"""
        return {
            **self._json_to_kwargs_base(data),
            **self._json_to_kwargs_notifications(data),
            "search": SearchMultiFactory(client=self.client)._from_json_monitor_nameless(data),
        }

    @kwargs_to_class
    def _from_json_identifier_only(self, data):
        """create instance from only the identifier"""
        return {"identifier": data}

    def from_search(self, search):
        """Retrieve monitor from a search

        Attributes
        ----------
        search : Any
            Any (reference to an) existing search
        """
        if search.identifier_complex is None:
            raise ValueError("Search is expected to have `identifier_complex` attribute set")
        response = self.client.session.get(f"hps/api/monitoring/bySearchId/{search.identifier_complex}")
        monitor = self._from_json_full(response.json())

        # Update lazy attributes of the original search with info coming from the monitor
        # Required when a search needs to be loaded only from its identifier_external
        search._update(monitor.search)

        # Set the monitor search to the (updated) input search
        monitor.search = search

        return monitor

    def overview(self, since):
        """Number of triggers for the active monitors

        Parameters
        ----------
        since : pandas.Timestamp
            The start date from when to count the number of triggers (up to the current date)

        Returns
        -------
        dict of (Any: int)
            Search objects as keys, number of hits as values
        """
        since = pd.Timestamp(since)
        if not since.tz:
            since = since.tz_localize(self.client.tz)
        params = {
            "since": since.isoformat(timespec="milliseconds")
        }
        response = self.client.session.get("/hps/api/monitoring/overview", params=params)
        active_monitors = self.all(active_only=True)
        return {
            ip.object_match_nocase(active_monitors, "identifier", str(entry["id"])): entry["numberOfResults"]
            for entry in response.json()["overview"]
        }

    def from_identifier(self, ref):
        """Retrieve monitor from identifier

        Parameters
        ----------
        ref : str or int
            Monitor identifier

        Returns
        -------
        Monitor
        """
        ref = str(ref)

        link = posixpath.join(self._endpoint, ref)
        response = self.client.session.get(link)

        return self._from_json(response.json())

    def all(self, active_only=True):
        """Retrieve all monitors

        Parameters
        ----------
        active_only : bool, default True
            Whether only the currently active monitors need to be retrieved, otherwise a monitor is retrieved for every
            search that is implemented in the SDK.
        """
        params = {
            "filterOnlyActiveMonitors": active_only,
            "doNotRetrieveTags": True,
        }
        response = self.client.session.get(self.tm_class.endpoint, params=params)
        return [
            self._from_json_all(data) for data in response.json()
            # TODO: better way to implement -> prone to generate issues that are hard to debug. Dummy placeholder?
            # only load monitors for search types we support
            if search_type_to_content_type.get(data["type"]) in SearchMultiFactory.factories
        ]

    def from_name(self, ref):
        """Retrieve monitor from its name

        Returns
        -------
        Monitor
        """
        return ip.object_match_nocase(self.all(active_only=False), "name", ref)

    @property
    def _get_methods(self):
        return self.from_search, self.from_identifier, self.from_name

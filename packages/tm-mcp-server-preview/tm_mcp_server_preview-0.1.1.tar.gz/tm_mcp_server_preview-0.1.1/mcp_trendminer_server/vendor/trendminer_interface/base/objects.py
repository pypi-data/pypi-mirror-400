import abc
from copy import deepcopy

import posixpath


class AuthenticatableBase(abc.ABC):
    """Instances which store authentication to the TrendMiner server

    Parameters
    ----------
    client: TrendMinerClient
        Client providing link to the appliance
    """
    def __init__(self, client):
        self.client = client

    def __repr__(self):
        return f"<< {self.__class__.__name__} >>"


class SerializableBase(AuthenticatableBase, abc.ABC):
    """Instances which are json-serializable on the TrendMiner server

    Attributes
    ----------
    client : TrendMinerClient
        Client authenticated to send requests to the appliance
    """

    def __init__(self, client):
        super().__init__(client)

    @abc.abstractmethod
    def _json(self):
        """JSON representation of the instance used to create and update objects on the appliance

        Returns
        -------
        dict
            Instance JSON representation
        """
        pass

    def copy(self, attributes=None):
        """Creates deepcopy of the instance, optionally replacing some attributes in the copied instance

        Parameters
        ----------
        attributes: dict, optional
            Instance attributes and what to replace them with in the copy as key-value pairs in a dict

        Returns
        -------
        Any
            Deepcopy of the instance, potentially with some attributes changed.
        """
        attributes = attributes or {}
        copy = deepcopy(self)
        copy.client = self.client  # client needs to be explicitly assigned, since client.session does not copy over
        for key, value in attributes.items():
            setattr(copy, key, value)
        return copy


class RetrievableBase(SerializableBase, abc.ABC):
    """TrendMiner instances which can be retrieved by a get request

    Attributes
    ----------
        identifier: str, optional
            Unique reference on the appliance
    """
    endpoint = None  # TODO: remove this concept

    def __init__(self, client, identifier):
        super().__init__(client=client)
        self.identifier = identifier

    # TODO: should be private
    @property
    def link(self):
        """Link to existing object"""
        return posixpath.join(self.endpoint, self.identifier)

    def __hash__(self):
        return hash((self.__class__, self.identifier))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.identifier == other.identifier


class EditableBase(RetrievableBase, abc.ABC):
    """Instances which can be saved to the TrendMiner server"""

    def __init__(self, client, identifier):
        super().__init__(client=client, identifier=identifier)

    def _put_updates(self, response):
        """Update some instance attributes from a put response"""
        pass

    def _post_updates(self, response):
        """Update instance attributes from a post response"""
        self.identifier = response.json()["identifier"]

    def _delete_updates(self, response):
        """Update instance attributes form a delete response"""
        self.identifier = None

    def save(self):
        """Creates this instance on the TrendMiner appliance"""
        self.identifier = None  # reset identifier to avoid overwriting  # TODO: move pre-config to another method
        response = self.client.session.post(self.endpoint, json=self._json())
        self._post_updates(response)

    def update(self):
        """Updates the appliance object to match this instance"""
        response = self.client.session.put(self.link, json=self._json())
        self._put_updates(response)

    def delete(self):
        """Remove this instance from the appliance"""
        self.client.session.delete(self.link)

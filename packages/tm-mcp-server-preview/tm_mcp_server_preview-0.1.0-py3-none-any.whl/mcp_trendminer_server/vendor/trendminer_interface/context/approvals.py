import posixpath
import pandas as pd

import trendminer_interface._input as ip

from trendminer_interface.base import FactoryBase, AuthenticatableBase, AsTimestamp
from trendminer_interface.constants import MAX_GET_SIZE
from trendminer_interface.user import UserFactory
from trendminer_interface.download_center import DownloadCenter


class Approval(AuthenticatableBase):
    """Context item approval

    Attributes
    ----------
    parent : pandas.Series
        Parent context item
    identifier : str
        Attachment identifier
    created : pandas.Timestamp
        Attachment creation time
    created_by : User
        Creator of the attachment
    """

    created = AsTimestamp()

    def __init__(
            self,
            parent,
            identifier,
            created,
            created_by,
    ):
        client = parent["type"].client
        super().__init__(client=client)
        self.parent = parent
        self.identifier=identifier
        self.created = created
        self.created_by = created_by

    @property
    def endpoint(self):
        """Context item attachment base endpoint depends on its parent context item"""
        return f"/context/data/{self.parent['identifier']}/approval/"

    def __repr__(self):
        return f"<< {self.__class__.__name__} | {self.created_by.name} >>"


class ApprovalFactory(FactoryBase):
    tm_class = Approval

    def __init__(self, parent: pd.Series):
        client = parent["type"].client
        super().__init__(client=client)
        self.parent = parent

    @property
    def _endpoint(self):
        return f"/context/data/{self.parent['identifier']}/approval"

    def _from_json(self, data):
        return self.tm_class(
            parent=self.parent,
            identifier=data["identifier"],
            created=data["createdDate"],
            created_by=UserFactory(client=self.client)._from_json_context(data["userDetails"]),
    )

    def all(self):
        """Retrieve all approvals of the parent ContextItem

        Returns
        -------
        list[Approval]
            List of all approvals on the parent ContextItem
        """

        response = self.client.session.get(self._endpoint)

        return [self._from_json(data) for data in response.json()]

    def add(self):
        """Add your own approval to the context item"""
        self.client.session.post(self._endpoint)

    def delete(self):
        """Delete your own approval of this context item"""
        self.client.session.delete(self._endpoint)

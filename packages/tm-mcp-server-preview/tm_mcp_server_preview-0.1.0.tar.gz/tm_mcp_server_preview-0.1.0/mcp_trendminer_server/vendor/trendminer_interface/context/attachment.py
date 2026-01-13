import posixpath
import pandas as pd

import trendminer_interface._input as ip

from trendminer_interface.base import FactoryBase, EditableBase, AsTimestamp
from trendminer_interface.constants import MAX_GET_SIZE
from trendminer_interface.user import UserFactory
from trendminer_interface.download_center import DownloadCenter


class Attachment(EditableBase):
    """Context item attachment

    Attributes
    ----------
    parent : pandas.Series
        Parent context item
    identifier : str
        Attachment identifier
    name : str
        Attachment name (does not include file extension)
    content_type : str
        Attachment content type (e.g. 'image/jpeg')
    extension : str
        Attachment file extension
    created : pandas.Timestamp
        Attachment creation time
    created_by : User
        Creator of the attachment
    modified : pandas.Timestamp
        Attachment last modified time
    modified_by : User
        Last updater of the context item
    """

    def _json(self):
        return {
            "identifier": self.identifier,
            "name": self.name,
            "extension": self.extension,
            "content_type": self.content_type,
        }

    created = AsTimestamp()
    modified = AsTimestamp()

    def __init__(
            self,
            parent,
            identifier,
            name,
            content_type,
            extension,
            created,
            created_by,
            modified,
            modified_by,
    ):
        client = parent["type"].client
        super().__init__(client=client, identifier=identifier)
        self.parent = parent
        self.name = name
        self.content_type = content_type,
        self.created = created
        self.created_by = created_by
        self.modified = modified
        self.modified_by = modified_by
        self.extension = extension

    @property
    def filename(self):
        """Attachment filename

        Returns
        -------
        str
        """
        return f"{self.name}.{self.extension}"

    @property
    def endpoint(self):
        """Context item attachment base endpoint depends on its parent context item"""
        return f"/context/data/{self.parent['identifier']}/attachments/"

    def download(self):
        """Download the context item attachment

        Returns
        -------
            bytes: attachment content
        """
        dc = DownloadCenter(client=self.client, location="context")
        response = dc.download(link=f"data/{self.parent['identifier']}/attachments/{self.identifier}/download")
        return response.content


class AttachmentFactory(FactoryBase):
    tm_class = Attachment

    def __init__(self, parent: pd.Series):
        client = parent["type"].client
        super().__init__(client=client)
        self.parent = parent

    @property
    def _endpoint(self):
        return f"/context/data/{self.parent['identifier']}/attachments"

    def _from_json(self, data):
        return self.tm_class(
            parent=self.parent,
            identifier=data["identifier"],
            name=data["name"],
            content_type=data["type"],
            extension=data["extension"],
            created=data["createdDate"],
            created_by=UserFactory(client=self.client)._from_json_identifier_only(data["createdBy"]),
            modified=data["lastModifiedDate"],
            modified_by=UserFactory(client=self.client)._from_json_identifier_only(data["lastModifiedBy"]),
    )

    def all(self):
        """Retrieve all attachments of the parent ContextItem

        Returns
        -------
        list[Attachment]
            List of all attachments on the parent ContextItem
        """
        params = {"size": MAX_GET_SIZE}
        content = self.client.session.paginated(keys=["content"]).get(self._endpoint, params=params)
        return [self._from_json(data) for data in content]

    def from_identifier(self, ref):
        """Retrieve an attachment from its identifier

        Parameters
        ----------
        ref : str
            Attachment UUID

        Returns
        -------
        Attachment
        """
        link = posixpath.join(self._endpoint, ref)
        response = self.client.session.get(link)
        return self._from_json(response.json())

    def from_name(self, ref):
        """Retrieve context item attachment by its name

        Parameters
        ----------
        ref : str
            Attachment name including extension
        """
        return ip.object_match_nocase(self.all(), attribute="filename", value=ref)

    def add(self, filename, content):
        """Add a new attachment to the context item

        Parameters
        ----------
        filename : str
            Filename including extension
        content : str
            File content as a string
        """
        name, extension = filename.split(".")
        self.client.session.post(
            url=self._endpoint,
            params={"name": name, "extension": extension, "type": "image/jpg"},
            headers={"Content-Type": "application/octet-stream"},
            data=content,
        )

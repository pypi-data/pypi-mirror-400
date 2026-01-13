from trendminer_interface.base import AuthenticatableBase, LazyAttribute
from trendminer_interface.tag import TagFactory
import trendminer_interface._input as ip

from .structure import structure_csv


class TagIOFactory(AuthenticatableBase):
    """Factory for managing tag file export/import"""
    endpoint = "ds/imported/timeseries/"

    @staticmethod
    def structure(tag_data_dict):
        """Puts tags in correct format to upload as csv

        Parameters
        ----------
        tag_data_dict : dict[Tag, pandas.Series]
            Tags and their data to be uploaded to the appliance via the csv import endpoint. The data pandas.Series data
            instance should have a DatetimeIndex. If a timezone-unaware index is given by the user, it is assumed to be
            in the client timezone.

        Returns
        -------
        pandas.DataFrame
            DataFrame with correct structure for import. Call `.to_csv` with `index_label=False` to save as csv file.
        """
        return structure_csv(tag_data_dict=tag_data_dict)

    def all(self):
        """Retrieve all csv-imported tags

        Returns
        -------
        tags : list[Tag]
            All csv-imported tags
        """
        content = self.client.session.paginated(keys=["content"]).get("/ds/imported/timeseries")
        return [
            TagFactory(client=self.client)._from_json_imported(data)
            for data in content
        ]

    def from_name(self, ref):
        """Retrieve a csv-imported tag from its name

        Parameters
        ----------
        ref : str
            Name of the imported tag

        Returns
        ------
        tag : Tag
            Imported tag with the given name
        """
        return ip.object_match_nocase(self.all(), attribute="name", value=ref)

    def save(self, tag_data_dict, index=True):
        """Uploads new csv tags or overwrites user's existing tags

        Parameters
        ----------
        tag_data_dict : dict[Tag, pandas.Series]
            Tags and their data to be uploaded to the appliance via the csv import endpoint. The data pandas.Series data
            instance should have a DatetimeIndex. If a timezone-unaware index is given by the user, it is assumed to be
            in the client timezone.
        index : bool, default True
            Whether to send an index request to the tags after uploading. Indexing them makes them ready for use in
            the appliance.

        Notes
        -----
        Valid tag data pandas.Series instances can be obtained by a call to Tag.get_data.
        """

        df = structure_csv(tag_data_dict=tag_data_dict)
        file = df.to_csv(index_label=False)
        files = {"file": ("tagdata.csv", file)}
        self.client.session.post(self.endpoint, files=files)

        # Update input tag data
        for tag in tag_data_dict:
            server_tag = TagFactory(client=self.client).from_name(tag.name)
            tag.identifier = server_tag.identifier
            tag.datasource = server_tag.datasource
            if not tag.numeric:
                tag.states = LazyAttribute()

        # Index tags if requested
        if index:
            for tag in tag_data_dict:
                tag.index()

    def delete(self, tags):
        """Remove imported tags

        Tagnames of removed tags can never be used again. To preserve names, it is better to overwrite them with a new
        call to the `post`.

        Parameters
        ----------
        tags : list of Tag or Any
            Imported tags (or references to these tags) that need to be removed.
        """
        tags = TagFactory(client=self.client)._list(tags)

        # Need to load all imported tags and match by name to get correct identifier
        content = self.client.session.paginated(keys=["content"]).get(self.endpoint)
        for tag in tags:
            match = ip.dict_match_nocase(items=content, key="name", value=tag.name)
            self.client.session.delete(f"{self.endpoint}/{match['identifier']}")

    def delete_all(self):
        """Remove all imported tags"""
        self.client.session.delete(self.endpoint)
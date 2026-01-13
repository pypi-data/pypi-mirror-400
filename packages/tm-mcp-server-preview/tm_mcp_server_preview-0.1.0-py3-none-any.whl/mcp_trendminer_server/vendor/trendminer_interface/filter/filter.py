from trendminer_interface.base import kwargs_to_class
from trendminer_interface.work import WorkOrganizerObjectBase, WorkOrganizerObjectFactoryBase

from .properties import FilterPropertiesMultiFactory, SearchFilterProperties, ManualFilterProperties


class Filter(WorkOrganizerObjectBase):
    """Filter object

    Attributes
    ----------
    identifier_complex : str
        additional UUID used for filters and searches; "complexId" in the backend
    properties : SearchFilterProperties or ManualFilterProperties
        Properties of the filter. Currently, a filter can be derived from a search, or crated manually from a list of
        input intervals
    """
    content_type = "FILTER"

    def __init__(
            self,
            client,
            identifier,
            name,
            description,
            parent,
            owner,
            last_modified,
            version,
            identifier_complex,
            properties,
    ):
        super().__init__(client=client, identifier=identifier, name=name, description=description, parent=parent,
                         owner=owner, last_modified=last_modified, version=version)

        self.identifier_complex = identifier_complex
        self.properties = properties

    def _post_updates(self, response):
        super()._post_updates(response)
        self.identifier_complex = response.json()["complexId"]

    def _put_updates(self, response):
        super()._put_updates(response)
        self.identifier_complex = response.json()["complexId"]

    def _json_data(self):
        return {
            **self.properties._json(),
        }

    def _full_instance(self):
        return FilterFactory(client=self.client).from_identifier(ref=self.identifier)


class FilterFactory(WorkOrganizerObjectFactoryBase):
    """Factory for instantiating and retrieving filters"""
    tm_class = Filter

    def _json_data(self, data):
        return {
            "identifier_complex": data["complexId"],
            "properties": FilterPropertiesMultiFactory(client=self.client)._from_json(data["data"]),
        }

    def from_search(self, search, filter_results, name, description="", parent=None):
        """Instantiate a new filter from a saved search

        Parameters
        ----------
        search : Any
            Saved search
        filter_results : bool
            When True, search results are filtered out. Otherwise, everything that is not a search result will be
            filtered out.
        name : str
            Filter name
        description : str, default ""
            Filter description
        parent : Folder or str
            The (reference to the) folder in which the filter will be saved
        """
        return self.tm_class(
            client=self.client,
            identifier=None,
            name=name,
            description=description,
            parent=parent,
            owner=None,
            last_modified=None,
            version=None,
            identifier_complex=None,
            properties=SearchFilterProperties(
                client=self.client,
                search=search,
                filter_results=filter_results,
            ),
        )

    def from_intervals(self, intervals, name, description="", parent=None):
        """Instantiate a new filter from a list of intervals

        Parameters
        ----------
        intervals : list of Interval
            Intervals which need to be filtered out
        name : str
            Filter name
        description : str, default ""
            Filter description
        parent : Folder or str
            The (reference to the) folder in which the filter will be saved
        """
        return self.tm_class(
            client=self.client,
            identifier=None,
            name=name,
            description=description,
            parent=parent,
            owner=None,
            last_modified=None,
            version=None,
            identifier_complex=None,
            properties=ManualFilterProperties(
                client=self.client,
                intervals=intervals,
            ),
        )

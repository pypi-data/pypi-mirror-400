from trendminer_interface.base import kwargs_to_class
from trendminer_interface.work import WorkOrganizerObjectBase, WorkOrganizerObjectFactoryBase, WorkOrganizerObjectMultiFactoryBase
from trendminer_interface.constants import WORK_ORGANIZER_CONTENT_OPTIONS
from trendminer_interface.folder import FolderFactory
from trendminer_interface.context.view import ContextHubViewFactory
from trendminer_interface.trendhub.view import TrendHubViewFactory
from trendminer_interface.search import ValueBasedSearchFactory, SimilaritySearchFactory
from trendminer_interface.tagbuilder import FormulaFactory, AggregationFactory
from trendminer_interface.dashhub import DashboardFactory
from trendminer_interface.filter import FilterFactory
from trendminer_interface.fingerprint import FingerprintFactory


class WorkOrganizerPlaceholder(WorkOrganizerObjectBase):
    """Placeholder for work organizer objects which have not yet been implemented in the SDK

    These item can be managed and deleted in the work organizer, but they cannot otherwise be interacted with. Their
    data is simply dumped as a dict in the `data` parameter.

    Attributes
    ----------
    data : dict
        Dump of the object json data
    content_type : str
        Work organizer item type
    """
    def __init__(self,
                 client,
                 identifier,
                 name,
                 description,
                 parent,
                 owner,
                 last_modified,
                 version,
                 data,
                 content_type,
                 ):
        super().__init__(client=client, identifier=identifier, name=name, description=description, parent=parent,
                         owner=owner, last_modified=last_modified, version=version)
        self.data = data
        self.content_type = content_type

    def _json_data(self):
        return self.data

    def _full_instance(self):
        raise NotImplementedError

    def __repr__(self):
        return f"<< {self.content_type} (not implemented) | {self.name} >>"


class WorkOrganizerPlaceholderFactory(WorkOrganizerObjectFactoryBase):
    """Factory for retrieving work organizer placeholder objects"""
    tm_class = WorkOrganizerPlaceholder

    def _json_data(self, data):
        """Full enriched payload"""
        return {
            "content_type": data["type"],
            "data": data["data"],
        }

    @kwargs_to_class
    def _from_json_work_organizer(self, data):
        """Need to add placeholder arguments not present in work organizer"""
        return {
            **super()._from_json_work_organizer.__wrapped__(self, data),
            "content_type": data["type"],
        }


implemented_factories = {
    factory.tm_class.content_type: factory
    for factory in [
        ContextHubViewFactory,
        TrendHubViewFactory,
        FolderFactory,
        ValueBasedSearchFactory,
        FormulaFactory,
        AggregationFactory,
        DashboardFactory,
        SimilaritySearchFactory,
        FilterFactory,
        FingerprintFactory,
    ]
}

unimplemented_factories = {
    content_type: WorkOrganizerPlaceholderFactory
    for content_type in WORK_ORGANIZER_CONTENT_OPTIONS
    if content_type not in implemented_factories
}


class FolderContentMultiFactory(WorkOrganizerObjectMultiFactoryBase):
    """Factory for retrieving any type of work organizer item"""
    factories = {
        **unimplemented_factories,
        **implemented_factories,
    }

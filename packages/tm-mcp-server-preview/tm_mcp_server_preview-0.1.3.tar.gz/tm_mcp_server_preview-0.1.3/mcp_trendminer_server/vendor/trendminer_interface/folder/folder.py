from trendminer_interface import _input as ip
from trendminer_interface.base import HasOptions
from trendminer_interface.constants import FOLDER_BROWSE_SIZE, WORK_ORGANIZER_CONTENT_OPTIONS
from trendminer_interface.work import WorkOrganizerObjectBase


class Folder(WorkOrganizerObjectBase):
    """Work organizer folder"""
    content_type = "FOLDER"

    def __init__(
            self,
            client,
            identifier,
            name,
            parent,
            owner,
            last_modified,
            version,
            description=None,
    ):
        # Folders do not have descriptions. It is accepted in the constructor for compatibility, but ignored.
        super().__init__(
            client=client,
            identifier=identifier,
            name=name,
            description=None,
            parent=parent,
            owner=owner,
            last_modified=last_modified,
            version=version,
        )

    def _json_data(self):
        return

    def _json(self):
        # We must be able to handle the case where parent is None, which implies the current user's home folder. We
        # should not attempt to replace the None with the actual home folder identifier, as this would often lead to
        # an additional API call and might trigger infinite recursion when the user's home folder is empty (cfr.
        # FolderFactory.get_home).
        parent = self.parent.identifier if self.parent is not None else None
        return {
            "id": self.identifier,
            "name": self.name,
            "folder": True,
            "parentId": parent,
            "version": self.version,
        }

    # TODO: implement uniform strategy for cacheing and clearing the cache
    def _clear_cache(self):
        """Clear the folder getting cache every time the folder structure is changed"""
        self.client.folder.from_identifier.cache_clear()

    def _put_updates(self, response):
        super()._put_updates(response)
        self._clear_cache()

    def _post_updates(self, response):
        super()._post_updates(response)
        self._clear_cache()

    def _delete_updates(self, response):
        super()._delete_updates(response)
        self._clear_cache()

    def _full_instance(self):
        from .factory import FolderFactory
        return FolderFactory(client=self.client).from_identifier(self.identifier)

    def get_children(self, included=None, excluded=None, folders_only=False):
        """Get the items in the current folder

        Parameters
        ----------
        included : list of str, optional
            Included work organizer item types. Options are: "VIEW", "FINGERPRINT", "CONTEXT_LOGBOOK_VIEW", "DASHBOARD",
            "FORMULA", "AGGREGATION", "VALUE_BASED_SEARCH", "DIGITAL_STEP_SEARCH", "SIMILARITY_SEARCH", "AREA_SEARCH",
            "CROSS_ASSET_VALUE_BASED_SEARCH", "TREND_HUB_2_VIEW", "FILTER", "MACHINE_LEARNING", "PREDICTIVE",
            "LEGACY_FINGERPRINT"
        excluded : list of str, optional
            Excluded work organizer item types. Options are: "VIEW", "FINGERPRINT", "CONTEXT_LOGBOOK_VIEW", "DASHBOARD",
            "FORMULA", "AGGREGATION", "VALUE_BASED_SEARCH", "DIGITAL_STEP_SEARCH", "SIMILARITY_SEARCH", "AREA_SEARCH",
            "CROSS_ASSET_VALUE_BASED_SEARCH", "TREND_HUB_2_VIEW", "FILTER", "MACHINE_LEARNING", "PREDICTIVE",
            "LEGACY_FINGERPRINT"
        folders_only : bool, default False
            Whether to only search for subfolders. Ignores `included` and èxcluded`

        Notes
        -----
        In the backend, monitors are included in the work organizer for technical reasons. However, in the user
        interface they are always filtered out. When `excluded` is kept at `None`, monitors are therefore also filter
        out. An empty list needs to provided explicitly to include monitors (`excluded=[]`).
        """
        if excluded is None:
            excluded = []
        included = [t if isinstance(t, str) else t.content_type for t in ip.any_list(included)]
        excluded = [t if isinstance(t, str) else t.content_type for t in ip.any_list(excluded)]
        included = [ip.correct_value(t, WORK_ORGANIZER_CONTENT_OPTIONS) for t in included]
        excluded = [ip.correct_value(t, WORK_ORGANIZER_CONTENT_OPTIONS) for t in excluded]

        params = {
            "size": FOLDER_BROWSE_SIZE,
            "foldersOnly": folders_only,
            "parent": self.identifier,
        }

        if included:
            params.update({"includeTypes": included})
        elif excluded:
            params.update({"excludeTypes": excluded})

        response = self.client.session.get("/work/saveditem/browse", params=params)

        try:
            content = response.json()["_embedded"]["content"]
        except KeyError:
            content = []

        from .content_factory import FolderContentMultiFactory
        return [
            FolderContentMultiFactory(client=self.client)._from_json_work_organizer(data) for data in content
        ]

    def get_child_from_name(self, ref, included=None, excluded=None, folders_only=False):
        """Get a single object from a folder by its name

        Parameters
        ----------
        ref : str
            Name of the child work organizer object saved in the folder
        included : list of str, optional
            Included work organizer item types. Options are: "VIEW", "FINGERPRINT", "CONTEXT_LOGBOOK_VIEW", "DASHBOARD",
            "FORMULA", "AGGREGATION", "VALUE_BASED_SEARCH", "DIGITAL_STEP_SEARCH", "SIMILARITY_SEARCH", "AREA_SEARCH",
            "CROSS_ASSET_VALUE_BASED_SEARCH", "TREND_HUB_2_VIEW", "FILTER", "MACHINE_LEARNING", "PREDICTIVE",
            "LEGACY_FINGERPRINT", "MONITOR"
        excluded : list of str, optional
            Excluded work organizer item types. Options are: "VIEW", "FINGERPRINT", "CONTEXT_LOGBOOK_VIEW", "DASHBOARD",
            "FORMULA", "AGGREGATION", "VALUE_BASED_SEARCH", "DIGITAL_STEP_SEARCH", "SIMILARITY_SEARCH", "AREA_SEARCH",
            "CROSS_ASSET_VALUE_BASED_SEARCH", "TREND_HUB_2_VIEW", "FILTER", "MACHINE_LEARNING", "PREDICTIVE",
            "LEGACY_FINGERPRINT", "MONITOR"
        folders_only : bool, default False
            Whether to only search for subfolders. Ignores `included` and èxcluded`

        Notes
        -----
        In the backend, monitors are included in the work organizer for technical reasons. However, in the user
        interface they are always filtered out. When `excluded` is kept at `None`, monitors are therefore also filter
        out. An empty list needs to provided explicitly to include monitors (`excluded=[]`).

        """
        content = self.get_children(included=included, excluded=excluded, folders_only=folders_only)
        return ip.object_match_nocase(content, attribute="name", value=ref)

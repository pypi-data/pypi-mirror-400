import posixpath
import pandas as pd
import numpy as np

from trendminer_interface.base import ByFactory, HasOptions, kwargs_to_class
from trendminer_interface.work import WorkOrganizerObjectBase, WorkOrganizerObjectFactoryBase
from trendminer_interface.user import UserFactory
from trendminer_interface.component_factory import ComponentMultiFactory
from trendminer_interface.constants import MAX_CONTEXT_ITEM_GET_SIZE, CONTEXT_VIEW_OPTIONS

from .view_configuration import grid_settings_dummy, scatter_settings_dummy, gantt_settings_dummy
from .filter import ContextFilterMultiFactory
from .type import ContextTypeFactory


class ContextHubView(WorkOrganizerObjectBase):
    """ContextHub view that can retrieve context items matching its associated context filters

    Attributes
    ----------
    filters : list
        Context filters associated with the view. These will determine the context items that are retrieved.
    view_type : str
        Visual representation of the view in the appliance: "gantt" or "grid"
    grid_settings : dict
        Configuration of the columns of the table view in json format. Not intended to be edited via the sdk.
    gantt_settings : dict
        Configuration of the gantt chart view in json format. Not intended to be edited via the sdk.
    scatter_settings : dict
        Settings for the sorting of context items in the table view, in json format. Not intended to be edited via the
        sdk.
    """
    content_type = "CONTEXT_LOGBOOK_VIEW"
    filters = ByFactory(ContextFilterMultiFactory, "_list")
    view_type = HasOptions(CONTEXT_VIEW_OPTIONS)

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
        filters,
        view_type,
        grid_settings,
        gantt_settings,
        scatter_settings,
    ):

        WorkOrganizerObjectBase.__init__(self, client=client, identifier=identifier, name=name, description=description,
                                         parent=parent, owner=owner, last_modified=last_modified, version=version)

        self.view_type = view_type
        self.grid_settings = grid_settings
        self.gantt_settings = gantt_settings
        self.scatter_settings = scatter_settings
        self.filters = filters

    def _full_instance(self):
        return ContextHubViewFactory(client=self.client).from_identifier(self.identifier)

    def _json_search(self):
        return {
            "filters": [filter._json() for filter in self.filters],
            "sortProperties": ["startEventDate"],
            "sortDirection": "asc",
            "fetchSize": MAX_CONTEXT_ITEM_GET_SIZE,
        }

    def _json_delete(self):
        return {
            **self._json_search(),
            "createdBefore": pd.Timestamp.now(tz=self.client.tz).isoformat(timespec="milliseconds")
        }

    def _json_data(self):
        return {
            "gridSettings": self.grid_settings,
            "ganttSettings": self.gantt_settings,
            "scatterSettings": self.scatter_settings,
            "viewType": self.view_type,
            **self._json_search(),
        }

    def get_items(self):
        """Retrieve all context items matching the view filters

        Returns
        -------
        items : pandas.DataFrame

            Index:
            The index will be pandas.IntervalIndex, with `index.left` and `index.right` timestamps of the context item
            start and end events, respectively. If a context item only has a single timestamp (i.e., when its type does
            not have an associated context workflow), `index.left` and `index.right` will be identical. For open context
            item, `index.right` will be the current time.

            Metadata columns:
            - **key** (str): short key
            - **identifier** (str): uuid
            - **identifier_external** (str): optional identifier by which the item is linked to an external system
            - **description** (str): optional description
            - **type** (object, ContextType): context item type
            - **component** (object, Tag or Asset or Attribute): component the item is linked to
            - **created_by** (object, User): user that created the item
            - **created** (datetime64[ns, client timezone]): creation date
            - **last_modified**: (datetime64[ns, client timezone]): last modified date

            Field columns:
            There will be a column for every unique field. Values will be float or str. The column name will be the
            unique field key (not the field name!) If the field is not present on some of the items, the corresponding
            values will be nan. Note that for context items that were created by monitors, the following metadata fields
            will be present (but hidden in the TrendMiner UI):
            - tm_monitor_id (str): `Monitor.identifier` short ID
            - tm_search_id (str): `SearchBase.identifier` UUID
            - tm_search_type (str): 'valuebased', 'similarity', ...

            Keyword columns:
            There will be a boolean column for every unique keyword, with a value of True when the keyword is present on
            an item. If the keyword is not present the corresponding value will be False.

            Event columns:
            All context item events besides of the start and end events will be added as datetime64[ns, client timezone]
            columns, with the event name as the column name.

        Notes
        -----
        Context items linked to multiple components are not supported. Only the first component will be returned.

        Duplicate column names can occur when a certain event state occurs more than once, or when there is an overlap
        between field keys, keywords, state names and/or metadata column names. It is advised to avoid this situation as
        this will complicate processing of the resulting DataFrame.
        """

        params = {
            "useTimeSeriesIdentifier": True
        }

        content = self.client.session.continuation(keys=["content"]).post(
            url="/context/v2/item/search",
            json=self._json_search(),
            params=params,
        )

        pd.set_option('future.no_silent_downcasting', True)

        current_time = pd.Timestamp.now(tz="UTC")

        base_type_dict = {
            "key": "str",
            "identifier": "str",
            "description": "str",
            "component": "object",
            "type": "object",
            "created_by": "object",
            "created": f"datetime64[ns, {self.client.tz}]",
            "last_modified": f"datetime64[ns, {self.client.tz}]",
        }

        if not content:
            return (
                pd.DataFrame(
                    index=pd.IntervalIndex(
                        data=[],
                        dtype=f"interval[datetime64[ns, {self.client.tz}], both]",
                        closed="both",
                    ),
                    columns=list(base_type_dict.keys()),
                )
                .astype(base_type_dict)
            )

        # Metadata
        # TODO: specific array type for context type, user, components
        df_base = (
            pd.DataFrame([
                {
                    "left": c["startEventDate"],
                    "right": c.get("endEventDate", current_time),
                    "key": c["shortKey"],
                    "identifier": c["identifier"],
                    "identifier_external": c.get("externalId"),
                    "description": c.get("description"),
                    "type": ContextTypeFactory(client=self.client)._from_json(c["type"]),
                    "component": (
                        ComponentMultiFactory(client=self.client)._from_json_context_item(c["components"][0])
                        if c["components"] else None
                    ),
                    "created_by": (
                        UserFactory(client=self.client)._from_json_context(c["userDetails"])
                        if "userDetails" in c else None
                    ),
                    "created": c["createdDate"],
                    "last_modified": c["lastModifiedDate"],
                }
                for c in content
            ])
            .assign(
                left=lambda df: pd.to_datetime(df["left"], format="mixed").dt.tz_convert(self.client.tz),
                right=lambda df: pd.to_datetime(df["right"], format="mixed").dt.tz_convert(self.client.tz),
                created=lambda df: pd.to_datetime(df["created"], format="mixed").dt.tz_convert(self.client.tz),
                last_modified=lambda df: pd.to_datetime(df["last_modified"], format="mixed").dt.tz_convert(self.client.tz)
            )
            .pipe(lambda df: df.set_index(
                pd.IntervalIndex.from_arrays(
                    left=df.pop("left"),
                    right=df.pop("right"),
                    closed="both",
                    name=self.name
                )
            ))
            .astype(base_type_dict)
            .sort_index()
        )

        df_keywords = (
            pd.DataFrame(
                index=df_base.index,
                data=[{keyword: True for keyword in c["keywords"]} for c in content],
                dtype="boolean",
            )
            .fillna(False)
        )

        # Fields
        field_conversion_functions = {
            "STRING": lambda x: x.astype("string"), # Important not to use 'str', which silently converts np.nan to 'nan'
            "ENUMERATION": lambda x: x.astype("string"),
            "NUMERIC": lambda x: pd.to_numeric(x, errors="coerce"),  # string value can occur in numeric field from syncs
        }

        df_fields = pd.DataFrame(
            index=df_base.index,
            data=[c["fields"] for c in content],
        )

        # Coerce field values into their correct types, and make sure all indexed fields are present
        # TODO: pandas `unique` method should work for context type, user, component, field
        unique_types = df_base["type"][~df_base["type"].map(lambda x: x.identifier).duplicated()].to_list()
        unique_field_dict = {field.key: field for context_type in unique_types for field in context_type.fields}

        for field_key, field in unique_field_dict.items():
            if field_key in df_fields:
                # convert existing field
                df_fields[field_key] = field_conversion_functions[field.field_type](df_fields[field_key])
            else:
                # Fill column with nan/NA values, depending on the datatype
                if field.field_type == "NUMERIC":
                    df_fields[field_key] = np.nan
                elif field.field_type in ["STRING", "ENUMERATION"]:
                    df_fields[field_key] = pd.NA
                    df_fields[field_key] = df_fields[field_key].astype("string")  # TODO: cleaner implementation
                else:
                    raise ValueError(field.field_type)

        # Events
        event_data = []
        renamed_columns = {}
        for c in content:
            d = {}
            for event in c["events"][1:-1]: # ignore start and end state, this info is in the IntervalIndex
                original_state = event["state"]
                state = original_state

                # Handle duplicate states by temporarily renaming them
                i = 0
                while state in d:
                    i+=1
                    state = f"{original_state}_unduplicated_{i}"
                d[state] = event["occurred"]
                renamed_columns.update({state: original_state})
            event_data.append(d)

        df_events = (
            pd.DataFrame(index=df_base.index, data=event_data)
            .apply(pd.to_datetime, errors="coerce")
            .apply(lambda ser: ser.dt.tz_convert(self.client.tz))
        )
        df_events.columns = df_events.columns.map(renamed_columns)  # Return duplicate states to their original name

        df = pd.concat([df_base, df_events, df_keywords, df_fields], axis=1)

        return df

    def delete_items(self):
        """Delete all context items matching the view filters"""
        self.client.session.delete("/context/item/batch/filters", json=self._json_delete())


class ContextHubViewFactory(WorkOrganizerObjectFactoryBase):
    """Factory for creating and retrieving ContextHub views"""
    tm_class = ContextHubView

    def __call__(
            self,
            filters,
            name="New View",
            description="",
            parent=None,
            view_type="grid",
    ):
        """Create a new ContextHub view

        Parameters
        ----------
        filters : list
            Context filters for the view
        name : str, default "New View"
            View name
        description : str, optional
            View description
        parent : Folder or str, optional
            Folder to which the view needs to be saved
        view_type : str
            Visual representation of the view in the appliance: "gantt" or "grid"
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
            filters=filters,
            view_type=view_type,
            grid_settings=grid_settings_dummy,
            scatter_settings=scatter_settings_dummy,
            gantt_settings=gantt_settings_dummy,
        )

    def from_identifier(self, ref):
        link = posixpath.join('/context/view', ref, "enriched")
        response = self.client.session.get(link)
        return self._from_json(response.json())

    def _json_data(self, data):
        return {
            "filters": [
                ContextFilterMultiFactory(client=self.client)._from_json(cfilter)
                for cfilter in data["data"]["filters"]
            ],
            "view_type": data["data"]["viewType"],
            "grid_settings": data["data"]["gridSettings"],
            "scatter_settings": data["data"]["scatterSettings"],
            "gantt_settings": data["data"]["ganttSettings"],
        }

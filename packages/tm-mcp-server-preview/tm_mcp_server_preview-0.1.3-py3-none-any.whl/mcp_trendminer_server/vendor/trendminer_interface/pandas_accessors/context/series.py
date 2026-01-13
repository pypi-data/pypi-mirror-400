import pandas as pd
from trendminer_interface.context import ContextItemFactory
from trendminer_interface.constants import MAX_GET_SIZE
from trendminer_interface.context import AttachmentFactory, ApprovalFactory


@pd.api.extensions.register_series_accessor("context")
class ContextItemSeriesAccessor:
    """Custom accessor for a pandas Series object representing a context item

    The convention that a context item is represented by a `pandas.Series` follows from the representation of a
    collection of context items (e.g. coming from a ContextHub view) as a `pandas.DataFrame`. It is assumed that users
    often want to do manipulations on those context items in parallel, for which the DataFrame format works well.

    This accessor is applicable to any Series object of valid structure. The minimal requirements are:
    - The `name` attribute should be a `pandas.Interval` based on timezone-aware timestamps
    - A 'type' value containing a ContextType object
    - A 'component' value containing a Tag, Asset or Attribute object

    Furthermore, there are additional values which have a specific meaning. The full structure is given below.

        Metadata values:
        - **key** (str): short key
        - **identifier** (str): uuid
        - **identifier_external** (str): optional identifier by which the item is linked to an external system
        - **description** (str): optional description
        - **type** (object, ContextType): context item type
        - **component** (object, Tag or Asset or Attribute): component the item is linked to
        - **created_by** (object, User): user that created the item
        - **created** (datetime64[ns, client timezone]): creation date
        - **last_modified**: (datetime64[ns, client timezone]): last modified date

        Field values:
        There will be a value for every unique field. Values will be float or str. The index name will be the
        unique field key (not the field name!) If the field is not present on some of the items, the corresponding
        values will be nan. Note that for context items that were created by monitors, the following metadata fields
        will be present (but hidden in the TrendMiner UI):
        - tm_monitor_id (str): `Monitor.identifier` short ID
        - tm_search_id (str): `SearchBase.identifier` UUID
        - tm_search_type (str): 'valuebased', 'similarity', ...

        Keyword values:
        There will be a boolean value for every unique keyword, with a value of True when the keyword is present on
        an item. If the keyword is not present the corresponding value will be False.

        Event values:
        All context item events besides of the start and end events will be added as pandas.Timestamp values, with the
        event name as the index key.

    The idea of this accessor is to provide users with an interface for edits and (bulk) updates to context items.

    Notes
    -----
    Methods return a modified DataFrames, they do not edit in place.

    Since the context item dataframe has an IntervalIndex, it can use the `interval` accessor for interval-based
    calculations and utilities.

    Duplicate index keys can occur when a certain event state occurs more than once, or when there is an overlap
    between field keys, keywords, state names and/or metadata keys. It is advised to avoid this situation as
    this will complicate processing of the resulting Series object.
    """

    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):

        if not isinstance(obj.name, pd.Interval):
            raise AttributeError("Context items are expected to have pandas.IntervalIndex index")

        if "type" not in obj.index:
            raise AttributeError("Context items should have a `type` column")

        if "component" not in obj.index:
            raise AttributeError("Context items should have a `component` column")

    @property
    def client(self):
        """Client object associated with the Series

        Returns
        -------
        TrendMinerClient
        """
        return self._obj["type"].client

    def _to_json(self) -> dict:
        """Get json payload representation of the context item

        Returns
        -------
        payload : dict
        """

        # Keywords are all columns where the value is a `True` boolean.
        keywords = self._obj[self._obj.apply(lambda value: value is True)].index.to_list()
        keywords = [kw.lower() for kw in keywords]

        # Events are all columns of the datetime type which are not `created` or `last_modified`
        if self._obj["type"].workflow is None:
            events = [{"occurred": self._obj.name.left.isoformat(timespec="milliseconds")}]
        else:
            additional_event_ser = (
                self._obj[self._obj.apply(isinstance, args=(pd.Timestamp,))]
                .drop(["last_modified", "created"], errors="ignore")
            )

            additional_events = [
                {
                    "occurred": value.isoformat(timespec="milliseconds"),
                    "state": key
                }
                for key, value in additional_event_ser.items()
            ]

            start_event = {
                "occurred": self._obj.name.left.isoformat(timespec="milliseconds"),
                "state": self._obj["type"].workflow.states[0],
            }

            end_event = {
                "occurred": self._obj.name.right.isoformat(timespec="milliseconds"),
                "state": self._obj["type"].workflow.states[-1],
            }

            events = [start_event] + additional_events + [end_event]

        # Fields are str or numeric values which are not booleans
        fields = (
            self._obj[self._obj.apply(isinstance, args=((str, float, int),)) & ~self._obj.apply(isinstance, args=(bool,))]
            .dropna()  # nan values are seen as floats
            .drop(
                ["key", "identifier", "identifier_external", "description", "type", "component",
                 # drop all default fields
                 "created_by", "created", "last_modified"] + keywords,  # Booleans are seen as int -> ignore keywords
                errors="ignore"  # dropped too many fields to be on the safe side (e.g. a user changed the type)
            )
            .pipe(lambda ser: ser[ser != ""])  # empty string values give errors
            .to_dict()
        )

        # Set description
        description = self._obj.get("description", "")
        description = description if pd.notna(description) else ""

        payload = {
            "identifier": self._obj.get("identifier"),
            "description": description,
            "keywords": keywords,
            "type": self._obj["type"]._json(),
            "components": [self._obj["component"]._json_component()],
            "fields": fields,
            "events": events,
        }

        return payload

    def save(self) -> pd.Series:
        """Save as a new context item in TrendMiner

        Returns the saved context item with additional metadata (identifiers, creator, created timestamp, ...)

        Returns
        -------
        item : pandas.Series
            The saved context item
        """
        response = self.client.session.post("/context/item", json=self._to_json())
        item = ContextItemFactory(client=self.client)._from_json(response.json())
        return item

    def update(self) -> pd.Series:
        """Update the server context item based on the current data in the Series

        Returns
        -------
        item : pd.Series
            The updated context item

        Notes
        -----
        When the original context items was open-ended (i.e., lacking an end state and having the current time at the
        moment of loading the item as the `index.right` value), it will be automatically closed when updating.
        """
        identifier = self._obj["identifier"]
        response = self.client.session.put(f"/context/item/{identifier}", json=self._to_json())
        item = ContextItemFactory(client=self.client)._from_json(response.json())
        return item

    def delete(self) -> None:
        """Delete the context item"""
        identifier = self._obj["identifier"]
        self.client.session.delete(f"/context/item/{identifier}")

    def get_history(self) -> list:
        """Get context item history

        Returns
        -------
        history : dict
            Context item history in raw json format
        """
        identifier = self._obj["identifier"]
        params = {"size": MAX_GET_SIZE, "sort": "desc"}
        response = self.client.session.get(f"context/history/{identifier}", params=params)
        return response.json()["content"]

    @property
    def approvals(self):
        """Context item approval factory

        Returns
        -------
        ApprovalFactory
        """
        return ApprovalFactory(parent=self._obj)

    @property
    def attachments(self):
        """Context item attachment factory

        Returns
        -------
        AttachmentFactory
        """
        return AttachmentFactory(parent=self._obj)

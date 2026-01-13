import pandas as pd
from trendminer_interface.constants import MAX_CONTEXT_ITEM_POST_SIZE


@pd.api.extensions.register_dataframe_accessor("context")
class ContextItemDataFrameAccessor:
    """Custom accessor for DataFrames of context items

    This accessor is applicable to any DataFrame of valid structure. The minimal requirements are:
    - IntervalIndex based on timezone-aware timestamps
    - A 'type' column containing a ContextType objects
    - A 'component' column with Tag/Asset/Attribute objects

    Furthermore, there are additional column names which have a specific meaning. The full structure is given below.

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

    The idea of this accessor is to provide users with an interface for edits and (bulk) manipulation, creation and
    updating of context items, for which a DataFrame is a great format.

    Notes
    -----
    Methods return a modified DataFrames, they do not edit in place.

    Since the context item dataframe has an IntervalIndex, it can use the `interval` accessor for interval-based
    calculations and utilities.

    Duplicate column names can occur when a certain event state occurs more than once, or when there is an overlap
    between field keys, keywords, state names and/or metadata column names. It is advised to avoid this situation as
    this will complicate processing of the resulting DataFrame.
    """

    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):

        if not isinstance(obj.index.dtype, pd.IntervalDtype):
            raise AttributeError("Context items are expected to have pandas.IntervalIndex index")

        if "type" not in obj.columns:
            raise AttributeError("Context items should have a `type` column")

        if "component" not in obj.columns:
            raise AttributeError("Context items should have a `component` column")

    @staticmethod
    def _validate_identifiers(obj):
        if obj["identifier"].isnull().any():
            raise AttributeError("All context items need a valid identifier to be updated")

    @property
    def client(self):
        """Client object associated with the DataFrame

        Only a single client per DataFrame is supported

        Returns
        -------
        TrendMinerClient
        """

        # Return client from first context type
        return self._obj.iloc[0].context.client

    def save(self):
        """Create multiple new context items to the appliance in a single request

        Creating multiple items at once in one (large) POST request is much more efficient than creating items
        individually in a loop.

        Returns
        -------
        None

        Notes
        -----
        Updating context items via this method does not return anything, nor are any properties (e.g. identifier, key,
        last_modified, ...) updated in place. Context items need to be retrieved from the server via a ContextHubView
        search (`get_items` method) to get their metadata.
        """

        if self._obj.empty:
            return

        payload = self._obj.apply(lambda item: item.context._to_json(), axis=1).to_list()

        for i in range(0, len(payload), MAX_CONTEXT_ITEM_POST_SIZE):
            self.client.session.post("/context/item/batch", json=payload[i:i+MAX_CONTEXT_ITEM_POST_SIZE])

    def update(self):
        """Update the server context items based on the current data in the DataFrame

        Returns
        -------
        None

        Notes
        -----
        A request needs to be sent for every individual context item in the DataFrame, making this method slow compared
        to creating new items (which can be performed in a single request).

        Updating context items via this method does not return anything, nor are any properties (e.g. last_modified)
        updated in place. Context items need to be retrieved from the server via a ContextHubView search (`get_items`
        method) to get their metadata.

        When the original context items were open-ended (i.e., lacking an end state and having the current time at the
        moment of loading the item as the `index.right` value), they will be automatically closed when updating.
        When loading items with the goal of updating them, you generally load only closed items by using a filter:
        `ContextHubView.get_items(filters=[client.context.filter.states(mode="CLOSED_ONLY"), ...], ... )`
        """

        if self._obj.empty:
            return

        # Validate the identifiers of all items up front to avoid failing somewhere halfway
        self._validate_identifiers(self._obj)

        for _, item in self._obj.iterrows():
            item.context.update()

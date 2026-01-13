import pandas as pd

import trendminer_interface._input as ip

from trendminer_interface.component_factory import ComponentMultiFactory
from trendminer_interface.base import FactoryBase
from trendminer_interface.user import UserFactory

from .type import ContextTypeFactory


class ContextItemFactory(FactoryBase):
    """Factory for creating and retrieving context items"""
    tm_class = pd.Series

    def __call__(self, context_type, component, events, description="", fields=None, keywords=None):
        """Instantiate a new pandas.Series instance representing a single context item

        Parameters
        ----------
        context_type : ContextType or str
            Type associated with the new context item
        component : Tag or Asset or Attribute
            Component to which the context item needs to be attached.
        events : pandas.Interval, pandas.Timestamp or dict[pandas.Timestamp, str]
            List of events corresponding to the context item. These can be ContextEvent or datetime. An interval can
            also be given as input, taking the interval start and end as the start and end events. Though the events
            need to be defined before context item creation on the appliance, this parameter can be left initially,
            allowing a context item 'template' to be initialized. This template can then be used to create many items
            (e.g. by filling in the `events` attribute in a loop).
        description : str, default ""
            Context item description
        fields : dict, optional
            Context item data fields.
        keywords : list, optional
            Keywords attached to the context item

        Returns
        -------
        item : pandas.Series
            Context item as structured Series object. Dedicated context item methods can be accessed through the
            `item.context` accessor.

        Notes
        -----
        It is not possible to create open-ended context items using the SDK
        """

        context_type = ContextTypeFactory(client=self.client)._get(context_type)
        component = ComponentMultiFactory(client=self.client)._get(component)

        # Initialize item with base data
        item = pd.Series(
            data={
                "description": description,
                "component": component,
                "type": context_type,
            },
        )

        if isinstance(events, pd.Interval):
            interval = events
            if (context_type.workflow is None) and (interval.length.total_seconds() != 0):
                raise ValueError(f"Interval length should be 0 as context type '{context_type}' does not have a workflow")

        elif isinstance(events, dict):
            if context_type.workflow is None:
                raise ValueError(f"Dict of events not a valid input as context type '{context_type}' does not have a "
                                 f"workflow. Use a single timestamp as input for the `events` parameter.")

            # Make sure keys are valid timestamps and case correct states
            events = {
                ip.to_local_timestamp(ts=ts, tz=self.client.tz): ip.correct_value(state, context_type.workflow.states)
                for ts, state in events.items()
            }

            start_state = context_type.workflow.states[0]
            starts = [ts for ts, state in events.items() if state == start_state]
            if len(starts) == 0:
                raise ValueError(f"Start state '{start_state}' should should be provided")

            end_state = context_type.workflow.states[-1]
            ends = [ts for ts, state in events.items() if state == end_state]
            if len(ends) == 0:
                raise ValueError(f"End state '{end_state}' should be provided")

            interval = pd.Interval(
                left=min(starts),
                right=max(ends),
                closed="both",
            )

            # Structure other events to add to the Series object
            other_events = {ts: state for ts, state in events.items() if ts not in [interval.left, interval.right]}
            ser_other_events = pd.Series(
                data=other_events.keys(),
                index=other_events.values(),
            )
            item = pd.concat([item, ser_other_events])

        else:
            events = ip.to_local_timestamp(ts=events, tz=self.client.tz)
            interval = pd.Interval(
                left=events,
                right=events,
                closed="both",
            )

        # Add keywords and fields
        keywords = keywords if keywords is not None else []
        ser_keywords = pd.Series(
            data=[True]*len(keywords),
            index=keywords,
        )
        ser_fields = pd.Series(
            data=fields,
        )
        item = pd.concat([item, ser_keywords, ser_fields])

        # Set the interval name for the series
        item.name = interval

        return item


    def from_identifier(self, ref):
        """Retrieve a single context item by its identifier

        Parameters
        ----------
        ref : str
            Context item UUID or shortKey

        Returns
        -------
        pandas.Series
        """
        response = self.client.session.get(f"/context/item/{ref}")
        return self._from_json(response.json())

    def _from_json(self, data):
        """Json to context item Series

        Parameters
        ----------
        data : dict
            response json

        Returns
        -------
        pandas.Series
        """

        interval = pd.Interval(
            left=pd.Timestamp(data["startEventDate"]).tz_convert(self.client.tz),
            right=pd.Timestamp(data.get("endEventDate", pd.Timestamp.now(tz=self.client.tz))).tz_convert(self.client.tz),
            closed="both",
        )

        # Metadata
        context_type = ContextTypeFactory(client=self.client)._from_json(data["type"])

        component = (
            ComponentMultiFactory(client=self.client)._from_json_context_item(data["components"][0])
            if data["components"] else None
        )

        created_by = (
            UserFactory(client=self.client)._from_json_context(data["userDetails"])
            if "userDetails" in data else None
        )

        metadata = {
            "key": data["shortKey"],
            "identifier": data["identifier"],
            "identifier_external": data.get("externalId"),
            "description": data.get("description"),
            "type": context_type,
            "component": component,
            "created_by": created_by,
            "created": pd.Timestamp(data["createdDate"]).tz_convert(self.client.tz),
            "last_modified": pd.Timestamp(data["lastModifiedDate"]).tz_convert(self.client.tz),
        }

        ser_base = pd.Series(name=interval, data=metadata)

        # Event data
        other_events = data["events"][1:-1]
        ser_events = pd.Series(
            name=interval,
            index=[event["state"] for event in other_events],
            data=[pd.Timestamp(event["occurred"], tz=self.client.tz) for event in other_events],
        )

        # Keyword data
        keyword_dict = {keyword: True for keyword in data["keywords"]}
        ser_keywords = pd.Series(name=interval, data=keyword_dict)

        # Field data
        ser_fields = pd.Series(name=interval,data=data["fields"])

        return pd.concat([ser_base, ser_events, ser_keywords, ser_fields])

    @property
    def _get_methods(self):
        return self.from_identifier,

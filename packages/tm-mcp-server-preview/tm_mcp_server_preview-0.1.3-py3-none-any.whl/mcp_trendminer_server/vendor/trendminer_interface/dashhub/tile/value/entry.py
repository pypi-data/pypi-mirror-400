from trendminer_interface.base import SerializableBase, FactoryBase
from trendminer_interface.tag import Tag
from trendminer_interface.component_factory import ComponentMultiFactory
from trendminer_interface.base import ByFactory
from .condition import CurrentValueConditionFactory


class CurrentValueEntry(SerializableBase):
    """Current value tile entry

    Attributes
    ----------
    component : Tag or Attribute
        Time-series component giving the current value
    color : str
        The default color if no condition is triggered
    conditions : list of CurrentValueCondition
        Conditions for the color of the tile
    """
    component = ByFactory(ComponentMultiFactory)
    conditions = ByFactory(CurrentValueConditionFactory, "_list")

    def __init__(self, client, component, color, conditions):
        SerializableBase.__init__(self, client=client)
        self.color = color  # Unconditioned color
        self.component = component
        self.conditions = conditions

    def _json(self):
        return {
            "componentIdentifier": self.component.identifier,
            "conditions": [
                              {
                                  "color": self.color,
                                  "values": [],
                              }
                          ] +
                          [
                              condition._json() for condition in self.conditions
                          ],
            "identifier": self.component.identifier,
            "path": None if isinstance(self.component, Tag) else self.component.path_hex,
            "type": self.component.component_type,
        }


class CurrentValueEntryFactory(FactoryBase):
    """Factory for instantiating and retrieving current value entries"""
    tm_class = CurrentValueEntry

    def __call__(self, component, color, conditions=None):
        """Instantiate a new current value tile entry

        Parameters
        ----------
        component : Tag or Attribute of str
            Time-series component giving the current value
        color : str
            The default tag color when no condition is triggered
        conditions : list of CurrentValueCondition or list of tuple, optional
            Conditional coloring criteria for the tile

        Returns
        -------
        CurrentValueEntry
        """
        return self.tm_class(
            client=self.client,
            component=component,
            color=color,
            conditions=conditions,
        )

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        CurrentValueEntry
        """
        return self.tm_class(
            client=self.client,
            component=ComponentMultiFactory(client=self.client)._from_json_current_value_tile(data),
            color=data["conditions"][0]["color"],  # unconditioned maps to entry color, not to a separate condition
            conditions=[
                CurrentValueConditionFactory(client=self.client)._from_json(condition)
                for condition in data["conditions"][1:]  # First condition is a blank for some reason
            ]
        )

from trendminer_interface import _input as ip
from trendminer_interface.base import SerializableBase, FactoryBase, HasOptions
from trendminer_interface.constants import VALUE_TILE_CONDITIONS


class CurrentValueCondition(SerializableBase):
    """Current value tile conditional formatting entity

    Defines a single condition and corresponding tag color

    Attributes
    ----------
    condition : str
        "GREATER_THAN", "GREATER_THAN_OR_EQUAL_TO", "LESS_THAN", "LESS_THAN_OR_EQUAL_TO", "EQUAL_TO",
        "NOT_EQUAL_TO", "BETWEEN", "NOT_BETWEEN", "CONTAINS" or "DOES_NOT_CONTAIN"
    color : str
        Tag color for the condition (e.g., "#FF0010")
    """
    conditions = HasOptions(VALUE_TILE_CONDITIONS)

    def __init__(self, client, color, condition, values):
        SerializableBase.__init__(self, client=client)
        self.color = color
        self.condition = condition
        self.values = values

    @property
    def values(self):
        """Condition value

        Length of the list is 1 or 2, depending on `condition`.

        Returns
        -------
        list
            values associated with the current value condition
        """
        return self._values

    @values.setter
    def values(self, values):
        self._values = ip.any_list(values)

    def _json(self):
        return {
            "color": self.color,
            "condition": self.condition,
            "values": [str(value) for value in self.values]
        }


class CurrentValueConditionFactory(FactoryBase):
    """Factory for instantiate and retrieving current value tile conditions"""
    tm_class = CurrentValueCondition

    def __call__(self, condition, values, color):
        """Instantiate new current value tile condition

        Parameters
        ----------
        condition : str
            "GREATER_THAN", "GREATER_THAN_OR_EQUAL_TO", "LESS_THAN", "LESS_THAN_OR_EQUAL_TO", "EQUAL_TO",
            "NOT_EQUAL_TO", "BETWEEN", "NOT_BETWEEN", "CONTAINS" or "DOES_NOT_CONTAIN". Also accepts numeric operators
            such as ">=".
        values : list
            List with 1 or 2 value entries, depending on the condition
        color : str
            Tag color for the condition (e.g., "#0075DC")

        Returns
        -------
        CurrentValueCondition
        """
        return self.tm_class(
            client=self.client,
            color=color,
            condition=condition,
            values=values
        )

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        CurrentValueCondition
        """
        return self.tm_class(
            client=self.client,
            color=data["color"],
            condition=data["condition"],
            values=data["values"],
        )

    def from_tuple(self, entry):
        """Instantiate new current value tile condition from tuple

        Parameters
        ----------
        entry : tuple
            (condition, values, color). Examples: (">", [1], "#0075DC"), ("BETWEEN", [1, 3], "#0075DC")
        """
        return self.tm_class(
            client=self.client,
            condition=entry[0],
            values=entry[1],
            color=entry[2],
        )

    @property
    def _get_methods(self):
        return self.from_tuple,

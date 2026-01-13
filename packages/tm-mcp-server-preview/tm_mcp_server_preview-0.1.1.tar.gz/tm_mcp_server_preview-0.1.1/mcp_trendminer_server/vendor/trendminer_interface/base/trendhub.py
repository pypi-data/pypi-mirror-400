import abc
import pandas as pd

from trendminer_interface.base import FactoryBase, ColorPicker, kwargs_to_class, AsTimedelta


class TrendHubEntryMixin(abc.ABC):
    """Mixin class for TrendHub objects: Tag, Attribute and EntryGroup

    These objects have a scale and a color. Even though EntryGroup has a color, it is not used and its individual
    members all have their own color.

    Attributes
    ----------
    color : str, optional
        The object color in TrendHub as a string (e.g. "#F0A3FF")
    scale : list, optional
        The scale as a [min, max] list. Blank (None) for autoscale.
    """
    color = ColorPicker()

    def __init__(self, color, scale):
        self.scale = scale
        self.color = color

    def _json_scale(self):
        if self.scale is None:
            return {"scaleType": "AUTO"}
        else:
            return {
                "min": self.scale[0],
                "max": self.scale[1],
                "scaleType": "MANUAL",
            }


class TrendHubEntryFactoryBase(FactoryBase, abc.ABC):
    """Base factory class for TrendHub object factories: TagFactory, AttributeFactory and EntryGroupFactory

    Implements shared logic on setting the scale attribute, as well as some abstract methods.
    """

    @abc.abstractmethod
    def _from_json_trendhub(self, data):
        """Get instance from TrendHub json data"""
        pass

    @abc.abstractmethod
    def _json_to_kwargs_trendhub(self, data):
        """Prepare keywords for instance creation from TrendHub json data"""
        pass

    def _json_to_kwargs_options(self, data):
        """Retrieve scale and color options from TrendHub json data"""
        data_scale = data["scale"]
        if data_scale["scaleType"].upper() == "AUTO":
            scale = None
        else:
            scale = [data_scale["min"], data_scale["max"]]

        return {
            "color": data["color"],
            "scale": scale,
        }


class TimeSeriesMixin(TrendHubEntryMixin, abc.ABC):
    """An object that can be shifted and hidden on a chart

    Parameters
    ----------
    shift: pandas.Timedelta, optional
        Object shift, impacts all data operations
    visible: bool, optional
        Whether object visible on the chart or hidden
    """

    shift = AsTimedelta()

    def __init__(self, color, scale, shift, visible):
        super().__init__(color=color, scale=scale)
        self.shift = shift
        self.visible = visible

    @property
    @abc.abstractmethod
    def _interpolation_payload_str(self):
        """Time series interpolation type as a string, used in calls

        Returns
        -------
        interpolation : str
            LINEAR or STEPPED
        """
        pass

    def _json_options(self):
        """TrendHub visualization options json"""
        return {
            "color": self.color,
            "interpolationType": self._interpolation_payload_str,
            "scale": self._json_scale(),
            "shift": int(self.shift.total_seconds()*1000),  # needs to be in ms
            "visible": self.visible
        }


class TimeSeriesFactoryBase(TrendHubEntryFactoryBase, abc.ABC):
    """Base factory class for time series object factories: TagFactory, AttributeFactory

    Implements shared logic for creating instances from TrendHub json data
    """

    @kwargs_to_class
    def _from_json_trendhub(self, data):
        """Create instance from data returned from TrendHub

        When retrieving the object directly (i.e., when it is not in a TrendHub group), the data is nested in
        'dataReference'.
        """
        return self._json_to_kwargs_trendhub(data["dataReference"])

    @kwargs_to_class
    def _from_json_trendhub_group(self, data):
        """Create instance from data returned from within a TrendHub group"""
        return self._json_to_kwargs_trendhub(data)

    def _json_to_kwargs_options(self, data):
        """Retrieve color, scale, shift and visibility from TrendHub json data"""
        return {
            **super()._json_to_kwargs_options(data),
            "shift": pd.Timedelta(milliseconds=data["shift"]),
            "visible": data["visible"],
        }

    def _json_to_kwargs_trendhub(self, data):
        """Partial keywords for instance creation from TrendHub json data"""
        return {
            **self._json_to_kwargs_options(data["options"]),  # For Tag/Attribute, options are nested in "options"
            "description": data.get("description"),
            "identifier": data["id"],
            "name": data["name"],
        }

    @abc.abstractmethod
    def _from_json_current_value_tile(self, data):
        """Retrieve instance from dashboard current value tile json"""
        pass

    @abc.abstractmethod
    def _from_json_context_item(self, data):
        """Retrieve instance from context item component json"""
        pass


# Default TrendHub configuration for Tag and Attributes. Not all endpoints return these attributes since they only
# matter in specific contexts. Therefore, it would be a mistake to assign a LazyAttribute instance to these attributes.
# Instead, when the info is not present, we must assume a 'normal' configuration. By assigning a default configuration
# rather than implementing a mechanism that would allow these options to be absent, the Tag or attribute can always be
# used in any which context (e.g. a TrendHub view).
default_trendhub_attributes = {
    "color": None,  # Will assign a color if no color info is present
    "scale": None,  # Assume autoscale
    "shift": pd.Timedelta(0),  # Assume there is no timeshift
    "visible": True,  # Assume the tag is visible
}

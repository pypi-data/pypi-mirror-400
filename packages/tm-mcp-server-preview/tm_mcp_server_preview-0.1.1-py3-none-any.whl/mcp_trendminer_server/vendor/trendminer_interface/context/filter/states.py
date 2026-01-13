from trendminer_interface import _input as ip
from trendminer_interface.base import HasOptions, FactoryBase
from trendminer_interface.constants import CONTEXT_FILTER_MODES_STATES
from trendminer_interface.context.filter.base import ContextFilterWithModeBase


class CurrentStateFilter(ContextFilterWithModeBase):
    """Filter on context item current state

    Attributes
    ----------
    mode : str, optional
        Filter for "OPEN_ONLY" or "CLOSED_ONLY" states. When using mode, any given states are ignored.
    """
    filter_type = "CURRENT_STATE_FILTER"
    mode = HasOptions(CONTEXT_FILTER_MODES_STATES)

    def __init__(self, client, states, mode):
        super().__init__(client=client, mode=mode)
        self.states = states

    @property
    def states(self):
        """Context item states

        Returns
        -------
        states : list of str
            Allowed context item states
        """
        return self._states

    @states.setter
    def states(self, states):
        self._states = ip.any_list(states)

    def _json(self):
        return {
            **super()._json(),
            "states": self.states,
        }


class CurrentStateFilterFactory(FactoryBase):
    """Factory for creating context item state filters"""
    tm_class = CurrentStateFilter

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        CurrentStateFilter
        """
        return self.tm_class(client=self.client, states=data.get("states"), mode=data.get("mode"))

    def __call__(self, states=None, mode=None):
        """Create new context item state filter

        Parameters
        ----------
        states : list of str, optional
            Allowed context item states
        mode : str, optional
            Filter for "OPEN_ONLY" or "CLOSED_ONLY" states. When using mode, any given states are ignored.
        """
        return self.tm_class(client=self.client, states=states, mode=mode)

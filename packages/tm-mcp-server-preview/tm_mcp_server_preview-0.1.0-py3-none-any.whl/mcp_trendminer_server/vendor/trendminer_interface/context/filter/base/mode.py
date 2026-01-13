import abc
from .filter import ContextFilterBase
from trendminer_interface.base import HasOptions
from trendminer_interface.constants import CONTEXT_FILTER_MODES_EMPTY


class ContextFilterWithModeBase(ContextFilterBase, abc.ABC):
    """Some context filters allow 'modes' to search for special conditions, rather than for an explicit value

    The default mode is to search for when a value is (not) empty

    Attributes
    ----------
    mode : str
        EMPTY or NON_EMPTY
    """
    mode = HasOptions(CONTEXT_FILTER_MODES_EMPTY)

    def __init__(self, client, mode):
        super().__init__(client=client)
        self.mode = mode

    def _json(self):
        return {
            **super()._json(),
            "mode": self.mode,
        }

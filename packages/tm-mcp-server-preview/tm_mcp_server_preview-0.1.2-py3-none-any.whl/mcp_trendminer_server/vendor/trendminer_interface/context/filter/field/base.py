import abc
from trendminer_interface.context.filter.base import ContextFilterWithModeBase
from trendminer_interface.context.field import ContextFieldFactory
from trendminer_interface.base import ByFactory


class ContextFieldFilterBase(ContextFilterWithModeBase, abc.ABC):
    """Superclass for filtering on a context field

    Attributes
    ----------
    field : ContextField
        The context field on which to filter
    """
    field = ByFactory(ContextFieldFactory)

    def __init__(self, client, field, mode):
        super().__init__(client=client, mode=mode)
        self.field = field

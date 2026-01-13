from trendminer_interface.base import MultiFactoryBase
from .numeric import NumericFieldFilterFactory
from .string import StringFieldFilterFactory
from .enumeration import EnumerationFieldFilterFactory
from ...field import ContextFieldFactory


class FieldFilterMultiFactory(MultiFactoryBase):
    """Factory for creating a field filter"""
    factories = {
        "NUMERIC": NumericFieldFilterFactory,
        "ENUMERATION": EnumerationFieldFilterFactory,
        "STRING": StringFieldFilterFactory,
    }

    def __call__(self, field, values=None, mode=None):
        """Create new context filter on a context field

        Parameters
        ----------
        field : Any
            A (reference to a) context field
        values : list, optional
            Values to filter on. List of string for enumeration or string fields, List of (entries convertible to)
            NumericQuery for numeric fields.
        mode : str, optional
            Search for special conditions, ignoring `values`. "EMPTY" or "NON_EMPTY"
        """
        field = ContextFieldFactory(client=self.client)._get(field)
        return self.factories[field.field_type](client=self.client)(field, values=values, mode=mode)

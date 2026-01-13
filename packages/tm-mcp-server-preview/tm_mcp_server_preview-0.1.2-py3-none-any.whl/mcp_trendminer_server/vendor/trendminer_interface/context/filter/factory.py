from trendminer_interface.base import MultiFactoryBase, to_subfactory

from .approval import ApprovalFilterFactory
from .context_type import TypeFilterFactory
from .created_by import CreatedByFilterFactory
from .components import ComponentFilterFactory
from .period import PeriodFilterFactory
from .interval import IntervalFilterFactory
from .keywords import KeywordFilterFactory
from .description import DescriptionFilterFactory
from .states import CurrentStateFilterFactory
from .field import (FieldFilterMultiFactory,
                    NumericFieldFilterFactory,
                    StringFieldFilterFactory,
                    EnumerationFieldFilterFactory)
from .property import PropertyFieldFilterFactory
from .created_date import CreatedDateFilterFactory
from .duration import DurationFilterFactory


filter_factory_dict = {factory.tm_class.filter_type: factory for factory in
                       [
                           ApprovalFilterFactory,
                           TypeFilterFactory,
                           CreatedByFilterFactory,
                           ComponentFilterFactory,
                           PeriodFilterFactory,
                           IntervalFilterFactory,
                           KeywordFilterFactory,
                           DescriptionFilterFactory,
                           CurrentStateFilterFactory,
                           NumericFieldFilterFactory,
                           StringFieldFilterFactory,
                           EnumerationFieldFilterFactory,
                           PropertyFieldFilterFactory,
                           CreatedDateFilterFactory,
                           DurationFilterFactory,
                       ]}


class ContextFilterMultiFactory(MultiFactoryBase):
    """Parent factory for context filters"""
    factories = filter_factory_dict

    @property
    def approval(self):
        """Approval filter factory

        Returns
        -------
        ApprovalFilterFactory
        """
        return ApprovalFilterFactory(client=self.client)

    @property
    def context_types(self):
        """Context type filter factory

        Returns
        -------
        TypeFilterFactory
        """
        return TypeFilterFactory(client=self.client)

    @property
    def users(self):
        """User filter factory

        Returns
        -------
        CreatedByFilterFactory
        """
        return CreatedByFilterFactory(client=self.client)

    @property
    def duration(self):
        """Duration filter factory

        Returns
        -------
        DurationFilterFactory
        """
        return DurationFilterFactory(client=self.client)

    @property
    def components(self):
        """Component filter factory

        Returns
        -------
        ComponentFilterFactory
        """
        return ComponentFilterFactory(client=self.client)

    @property
    def period(self):
        """Period filter factory

        A period is a live, moving timeframe, contrary to the static interval.

        Returns
        -------
        PeriodFilterFactory
        """
        return PeriodFilterFactory(client=self.client)

    @property
    def interval(self):
        """Interval filter factory

        An interval is a static timeframe, contrary to the moving period

        Returns
        -------
        IntervalFilterFactory
        """
        return IntervalFilterFactory(client=self.client)

    @property
    def keywords(self):
        """Keyword filter factory

        Returns
        -------
        KeywordFilterFactory
        """
        return KeywordFilterFactory(client=self.client)

    @property
    def description(self):
        """Description filter factory

        Returns
        -------
        DescriptionFilterFactory
        """
        return DescriptionFilterFactory(client=self.client)

    @property
    def states(self):
        """Current state filter factory

        Returns
        -------
        CurrentStateFilterFactory
        """
        return CurrentStateFilterFactory(client=self.client)

    @property
    def field(self):
        """Field filter factory

        Returns
        -------
        FieldFilterMultiFactory
        """
        return FieldFilterMultiFactory(client=self.client)

    @property
    def created_date(self):
        """Created date filter factory

        Returns
        -------
        CreatedByFilterFactory
        """
        return CreatedDateFilterFactory(client=self.client)

    @property
    def property(self):
        """Other property fitler factory

        Returns
        -------
        PropertyFieldFilterFactory
        """
        return PropertyFieldFilterFactory(client=self.client)

    @to_subfactory
    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        Any
        """
        return data["type"]

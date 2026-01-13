from trendminer_interface.context.filter.base.filter import ContextFilterBase
from trendminer_interface.base import FactoryBase


class ApprovalFilter(ContextFilterBase):
    """Context filter on item approval

    Attributes
    ----------
    approved : bool
        Item approval status
    """
    filter_type = "APPROVAL_FILTER"

    def __init__(self, client, approved: bool):
        super().__init__(client=client)
        self.approved = approved

    def _json(self):
        return {
            **super()._json(),
            "withApprovals": self.approved
        }


class ApprovalFilterFactory(FactoryBase):
    """Factory for creating context item approval filters"""
    tm_class = ApprovalFilter

    def _from_json(self, data):
        """Response json to instance

        Attributes
        ----------
        data : dict
            response json

        Returns
        -------
        ApprovalFilter
        """
        return self.tm_class(client=self.client, approved=data["withApprovals"])

    def __call__(self, approved: bool):
        """Create new context item approval filter

        Parameters
        ----------
        approved : bool
            Item approval status

        Returns
        -------
        ApprovalFilter
            Context item approval filter
        """
        return self.tm_class(client=self.client, approved=approved)

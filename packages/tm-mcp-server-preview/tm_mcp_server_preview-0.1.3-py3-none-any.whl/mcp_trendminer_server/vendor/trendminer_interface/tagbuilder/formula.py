import abc

from trendminer_interface.base import LazyAttribute, kwargs_to_class
from trendminer_interface.work import WorkOrganizerObjectFactoryBase
from trendminer_interface.tag import TagFactory

from .base import TagBuilderTagBase


class FormulaClient(abc.ABC):
    """Client for formula tag factory"""
    @property
    def formula(self):
        """Factory for instantiating and retrieving tag builder formulas"""
        return FormulaFactory(client=self)


class Formula(TagBuilderTagBase):
    """Tag builder formula tag

    Attributes
    ----------
    formula : str
        The formula definition as a string
    """
    content_type = "FORMULA"

    def __init__(
            self,
            client,
            formula,
            mapping,
            name,
            description,
            identifier,
            parent,
            owner,
            last_modified,
            version,
    ):
        super().__init__(client=client, identifier=identifier, name=name, description=description, parent=parent,
                         owner=owner, last_modified=last_modified, version=version)

        self.formula = formula
        self.mapping = mapping

    @property
    def mapping(self):
        """Variable to tag mapping

        Returns
        -------
        mapping : dict of str: Tag
            Dict mapping the variables in the formula definition to tags
        """
        return self._mapping

    @mapping.setter
    def mapping(self, mapping):
        if isinstance(mapping, LazyAttribute):
            self._mapping = mapping
        else:
            new_mapping = {}
            for key, value in mapping.items():
                new_mapping.update({key: TagFactory(client=self.client)._get(value)})
            self._mapping = new_mapping

    def _json_data(self):
        return {
            "formula": self.formula,
            "formulaVariableLinks": [
                {
                    "variable": k,
                    "timeSeriesDefinitionId": v.identifier,
                    "shift": int(v.shift.total_seconds()),
                    "interpolationType": v._interpolation_payload_str,
                    "timeSeriesName": v.name,
                }
                for k, v in self.mapping.items()
            ],
        }

    def _full_instance(self):
        return FormulaFactory(client=self.client).from_identifier(self.identifier)


class FormulaFactory(WorkOrganizerObjectFactoryBase):
    """Factory for creating and retrieving formula tags"""
    tm_class = Formula

    def __call__(
            self,
            formula,
            mapping,
            name,
            description="",
            parent=None,
    ):
        return self.tm_class(
            client=self.client,
            formula=formula,
            mapping=mapping,
            name=name,
            description=description,
            identifier=None,
            parent=parent,
            owner=None,
            last_modified=None,
            version=None,
        )

    def _json_data(self, data):
        """Full enriched payload"""
        mapping = {
            entry["variable"]: TagFactory(client=self.client)._from_json_formula(entry)
            for entry in data["data"]["formulaVariableLinks"]
        }

        return {
            "formula": data["data"]["formula"],
            "mapping": mapping,
        }

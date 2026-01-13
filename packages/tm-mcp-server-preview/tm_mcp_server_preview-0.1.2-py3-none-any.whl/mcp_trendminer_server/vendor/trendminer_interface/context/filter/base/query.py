import re
import abc
from trendminer_interface.base import SerializableBase, FactoryBase, HasOptions
from trendminer_interface.constants import CONTEXT_OPERATOR_MAPPING


inverted_mapping = {value: key for key, value in CONTEXT_OPERATOR_MAPPING.items()}
direct_mapping = {value: value for key, value in CONTEXT_OPERATOR_MAPPING.items()}

operator_options = {
    **CONTEXT_OPERATOR_MAPPING,
    **direct_mapping,
}


def interpret_query(query):
    """Extract parameter, operator and value from value-based-query-like input

    Attributes
    ----------
    query : str or dict or tuple
        query from which parameter, operator and value need to be extracted

    Returns
    -------
    parameter : Any
        The parameter extracted from the query
    operator : Any
        The operator extracted from the query
    value : Any
        The value extracted from the query
    """
    if isinstance(query, str):
        operator = re.search("[<>=!]{1,2}[ ]*", query).group().strip()
        (parameter, value) = [part.strip() for part in query.split(operator)]
        if parameter == "":
            parameter = None

    elif isinstance(query, dict):
        parameter = query.get("parameter")
        operator = query["operator"]
        value = query["value"]

    else:
        try:
            parameter = query[-3]
        except IndexError:
            parameter = None
        operator = query[-2]
        value = query[-1]

    return parameter, operator, value


class ContextQueryBase(SerializableBase, abc.ABC):
    """Superclass for (in)equality-type context filters

    This class handles the extraction and storage of operator (e.g. '>') and value (e.g. 12) for these types of filters

    Attributes
    ----------
    operator_str : str
        Operator given as full-text string (rather than a symbol), e.g. "LESS_THAN"
    value : Any
        The value in the (in)equality
    """
    operator_str = HasOptions(operator_options)

    def __init__(self, client, operator, value):
        super().__init__(client=client)
        self.operator_str = operator
        self.value = value

    @property
    def operator(self):
        """Operator as a symbol

        Returns
        -------
        Operator given as a symbol, e.g. "<"
        """
        return inverted_mapping[self.operator_str]

    def __repr__(self):
        return f'<< {self.__class__.__name__} | {self.operator} {self.value} >>'


class ContextQueryFactoryBase(FactoryBase, abc.ABC):
    """Superclass for factories creating ContextQuery-inheriting filters"""

    @abc.abstractmethod
    def _from_json(self, data):
        pass

    def from_query(self, query):
        """Create query-based context filter instances from a query input

        Attributes
        ----------
        query : str or dict or tuple
            query from which parameter, operator and value need to be extracted

        Returns
        -------
        class instance
            Context filter instance derived from the query
        """
        parameter, operator, value = interpret_query(query)
        return self.tm_class(client=self.client, operator=operator, value=value)

    @property
    def _get_methods(self):
        return self.from_query,





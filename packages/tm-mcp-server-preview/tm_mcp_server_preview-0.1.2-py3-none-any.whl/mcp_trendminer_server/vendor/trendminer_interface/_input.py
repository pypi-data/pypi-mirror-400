import pandas as pd
from uuid import UUID

from .exceptions import ResourceNotFound, AmbiguousResource
from trendminer_interface.base import LazyAttribute


def any_list(i):
    """Outputs list by converting tuple, or encapsulating object

    Parameters
    ----------
    i : Any
        To be converted into list

    Returns
    -------
    list
    """
    if i is None:
        return []
    if isinstance(i, list):
        return i
    if isinstance(i, tuple):
        return list(i)
    if isinstance(i, set):
        return list(i)
    return [i]


def dict_match_nocase(items, key, value):
    """
    Return dict ojbect of which a given key matches given string value.

    Try case-insensitive match when no sensitive match is found.

    Parameters
    ----------
    items : list
        list of dicts
    key : str
        key present in all dicts in the list
    value : str
        string that should match dict[key] (case insenstive)

    Returns
    -------
    data : dict
        dict of which dict[key] matches value
    """

    results = [item for item in items if item[key].casefold() == value.casefold()]

    if len(results) == 1:
        data = results[0]

    elif len(results) == 0:
        raise ResourceNotFound(f'No match for {key}=="{value}"')

    else:
        case_sensitive = [item for item in results if item[key] == value]
        if len(case_sensitive) == 1:
            data = results[0]
        else:
            raise AmbiguousResource(f'Multiple matches for {key}=="{value}": '
                                    f'{", ".join([item[key] for item in results])}')

    return data


def object_match_nocase(object_list, attribute, value):
    """
    Return single object from list of which a given attribute matches given value.

    Try case insensitive match when no sensitive match is found.

    Parameters
    ----------
    object_list : list
        list of objects
    attribute : str
        string attribute present in all object in the list
    value : str
        the string that object.attribute should match (ignoring case if no exact match is found)

    Returns
    -------
    object
        object of which object.attribute == value
    """

    results = [
        item
        for item in object_list
        if getattr(item, attribute).casefold() == value.casefold()
    ]

    if len(results) == 1:
        data = results[0]

    elif len(results) == 0:
        raise ResourceNotFound(f'No match for {attribute}=="{value}"')

    else:
        case_sensitive = [item for item in results if getattr(item, attribute) == value]
        if len(case_sensitive) == 1:
            data = results[0]
        else:
            raise AmbiguousResource(f'{len(case_sensitive)} case-sensitive matches for {attribute}=="{value}"')

    return data


def case_correct(value, value_options):
    """Correct string case by selecting case-insensitive match from list of strings"""

    if isinstance(value, LazyAttribute):
        return value

    if value in value_options:
        return value

    case_in_sensitive = [i for i in value_options if (i is not None) and (value.casefold() == i.casefold())]

    if len(case_in_sensitive) == 1:
        return case_in_sensitive[0]

    if len(case_in_sensitive) == 0:
        raise ResourceNotFound(f"No list entry matching {value} in [{', '.join(value_options)}]")

    raise AmbiguousResource(
        f'Multiple case-insensitive list entries matching {value}: {", ".join(case_in_sensitive)}'
    )


def is_uuid(ref):
    """Check if input is valid UUID"""

    try:
        UUID(ref, version=4)
    except (ValueError, AttributeError):
        return False
    return True


def unique_by_attribute(items, attribute):
    """Keep only instances of which a given attribute is unique"""
    seen = set()
    return [seen.add(getattr(obj, attribute)) or obj for obj in items if getattr(obj, attribute) not in seen]


def correct_value(value, value_options):
    """Correct the input value base on a fixed selection of possibilities, given as list or dict. Corrects case and can
    map values (if options are given as a dict). Throws a clear error if input value does not match any option."""
    if value is None:
        return value
    if isinstance(value, LazyAttribute):
        return value
    try:
        if isinstance(value_options, list):
            return case_correct(value, value_options)
        elif isinstance(value_options, dict):
            value = case_correct(value, value_options.keys())
            return value_options[value]
        else:  # pragma: no cover
            raise TypeError
    except ResourceNotFound:
        if isinstance(value_options, dict):
            main_options = set(value_options.values())
            alternative_options = [v for v in value_options.keys() if v not in main_options]
            error_str = f'''
            No list entry matching '{value}'
                Options: [{', '.join(main_options)}]
                Alternative options: [{', '.join(alternative_options)}]
            '''
        else:
            error_str = f"'{value}' not in options: {', '.join(value_options)}"
        raise ValueError(error_str)


def options(value_options):
    """Method decorator for checking/correcting input values using the correct_value function"""
    def fun(f):
        def wrapper(self, value):
            return f(self, correct_value(value, value_options))
        return wrapper
    return fun


def to_local_timestamp(ts, tz):
    """Convert the input timestamp to a pandas Timestamp and make sure it is in the given timezone

    Timezone-aware timestamps are converted to the given timezone, while timezone-naive timestamps are assumed to be
    in the given timezone.

    Parameters
    ----------
    ts : Any
        Timestamp to be converted to pandas.Timestamp. Can be any input that can be handled by `pandas.Timestamp`.
    tz : Any
        Desired timezone. Can be any input that can be used by `pandas.Timestamp.tz_localize` and
        `pandas.Timestamp.tz_convert`.

    Returns
    -------
    ts : pandas.Timestamp
        Timestamp in the provided timezone.
    """
    if not isinstance(ts, LazyAttribute):
        ts = pd.Timestamp(ts)
        if not ts.tz:
            ts = ts.tz_localize(tz)
        else:
            ts = ts.tz_convert(tz)
    return ts

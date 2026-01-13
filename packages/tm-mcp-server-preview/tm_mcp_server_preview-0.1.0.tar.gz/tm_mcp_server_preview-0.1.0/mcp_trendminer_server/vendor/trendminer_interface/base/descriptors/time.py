import pandas as pd
from trendminer_interface.base import LazyAttribute
from trendminer_interface import _input as ip


class AsTimestamp:
    """Descriptor for setting an attribute as pandas Timestamp"""

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, instance, owner):
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        setattr(instance, self.private_name, ip.to_local_timestamp(ts=value, tz=instance.client.tz))


class AsTimedelta:
    """Descriptor for setting an attribute as pandas Timestamp"""

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, instance, owner):
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        if not isinstance(value, LazyAttribute):
            value = pd.Timedelta(value)
        setattr(instance, self.private_name, value)

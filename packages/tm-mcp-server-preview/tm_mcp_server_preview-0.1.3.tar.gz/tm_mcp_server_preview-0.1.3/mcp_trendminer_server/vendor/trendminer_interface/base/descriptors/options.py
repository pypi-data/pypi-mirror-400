import trendminer_interface._input as ip


class HasOptions:
    """Descriptor for when a class attribute needs to be on of fixed set of options

    Case corrects inputs.

    Attributes
    ----------
    options : list or dict
        list of options, or dict with accepted keys, and the final values they map to.
    """
    def __init__(self, options):
        self.options = options

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, instance, owner):
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        setattr(
            instance,
            self.private_name,
            ip.correct_value(value, self.options)
        )

import abc


class LazyAttribute:
    """Placeholder attribute for lazy attributes"""
    def __init__(self, name=""):
        self.name = name

    def __repr__(self):
        return f"<< {self.__class__.__name__} | {self.name} >>"

    def __eq__(self, other):
        """A lazy attribute should never be used in this way

        Raises
        ------
        RuntimeError
        """

        raise RuntimeError("Internal error: Attempted direct __eq__ call on placeholder for a lazy loading attribute")

    def __bool__(self):
        """A lazy attribute should never be used in this way

        Raises
        ------
        RuntimeError
        """
        raise RuntimeError("Internal error: Attempted direct __bool__ call on placeholder for a lazy loading attribute")


class LazyLoadingMixin(abc.ABC):
    """Partially instantiated objects, only send a request for additional data when it is needed"""

    @property
    def lazy(self):
        """List of the names of the lazy attributes of the instance

        Returns
        -------
        list of str
            Names of lazy attributes
        """
        return [key for key, value in self.__dict__.items() if isinstance(value, LazyAttribute)]

    @abc.abstractmethod
    def _full_instance(self):
        """Send a get request to get the fully defined instance from the appliance

        The full instance can be used to set the attributes that are lazy.
        """
        pass

    def _update(self, other):
        """Update the lazy attributes of the object with non-lazy attributes of another object"""
        for attr in self.lazy:
            other_attr = other.__getattribute__(attr)
            if not isinstance(other_attr, LazyAttribute):
                object.__setattr__(self, attr, other_attr)

    def _load(self):
        """Retrieve a full instance from the appliance and fill in the lazy attributes"""
        full = self._full_instance()
        self._update(full)

    def __getattribute__(self, item):
        """Overwrite to check if attribute is lazy, and retrieve data from the appliance if it is """
        value = object.__getattribute__(self, item)
        if isinstance(value, LazyAttribute):
            self._load()
            value = self.__getattribute__(item)
            if isinstance(value, LazyAttribute):  # pragma: no cover
                raise RuntimeError(f'Failed to load lazy attribute "{item}"')
        return value

    def _repr_lazy(self, item):
        """Method to call in class __repr__ method for potential lazy attributes

        Using this method to retrieve an attribute avoids the __repr__ method from loading a lazy attribute. This is
        mainly intended to avoid lazy attributes being loaded by the debugger.
        """
        value = object.__getattribute__(self, item)
        if isinstance(value, LazyAttribute):
            return "..."
        else:
            return value

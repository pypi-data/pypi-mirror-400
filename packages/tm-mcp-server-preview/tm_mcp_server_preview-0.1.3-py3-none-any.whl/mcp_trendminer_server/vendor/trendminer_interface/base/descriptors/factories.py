class ByFactory:
    """Descriptor for converting class attributes into defined classes

    Attributes
    ----------
    factory_class : type
        The class which holds the conversion method
    method : str, default "get"
        The class method (as a string) that needs to be invoked for conversion
    """
    def __init__(self, factory_class, method="_get"):
        self.factory_class = factory_class
        self.method = method

    def __set_name__(self, owner, name):
        self.private_name = '_' + name

    def __get__(self, instance, owner):
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        factory = self.factory_class(client=instance.client)
        setattr(
            instance,
            self.private_name,
            getattr(factory, self.method)(value)
        )

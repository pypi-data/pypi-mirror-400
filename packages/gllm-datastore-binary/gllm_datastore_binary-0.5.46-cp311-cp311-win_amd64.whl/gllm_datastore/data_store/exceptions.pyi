from _typeshed import Incomplete

class NotSupportedException(Exception):
    """Raised when attempting to access an unsupported capability.

    This exception is raised when code attempts to access a capability
    that isn't configured for a datastore.
    """
    capability: Incomplete
    class_name: Incomplete
    class_obj: Incomplete
    def __init__(self, capability: str, class_obj: type) -> None:
        """Initialize the exception.

        Args:
            capability (str): The name of the unsupported capability.
            class_obj (Type): The class object for context.
        """

class NotRegisteredException(Exception):
    """Raised when attempting to access a capability that is not registered.

    This exception is raised when code attempts to access a capability
    that is not registered for a datastore but is supported by the datastore.
    """
    capability: Incomplete
    class_name: Incomplete
    class_obj: Incomplete
    def __init__(self, capability: str, class_obj: type) -> None:
        """Initialize the exception.

        Args:
            capability (str): The name of the unregistered capability.
            class_obj (Type): The class object for context.
        """

"""Exception for the ``django_lockable`` app."""


class LockedField(Exception):
    """Exception raised when a ``Lockable`` is not in a state that permits the edition of a field

    The exception string exposes the string representation of the lockable instance and the field
    that failed to be updated

    Attributes
    ----------
    instance :.models.Lockable
        The ``Lockable`` instance that raised the original exception.
    attribute : str
        Name of the attribute that could not be updated

    """

    def __init__(self, instance, attribute):
        """Save the given instance and attribute in the object to use in ``str``"""

        super().__init__()
        self.instance = instance
        self.attribute = attribute

    def __str__(self):
        """Render a useful representation of the exception."""

        return f'The "{self.attribute}" field of "{repr(self.instance)}" is locked and cannot be edited'

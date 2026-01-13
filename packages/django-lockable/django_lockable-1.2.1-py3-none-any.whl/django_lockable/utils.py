"""Utils for the ``django_lockable`` app."""

from contextlib import contextmanager
from inspect import isclass


@contextmanager
def _no_fields_locking(obj):
    """A context manager to use to allow setting fields on an instance or a class.

    Exists to be used in methods like ``__init__`` or ``refresh_from_db``, or in tests.

    Example
    -------

    # Will deactivate locking for the instance only
    >>> with _no_fields_locking(instance):
    ...     instance.foo = 'bar'

    # Will deactivate locking for all instances of the model
    >>> with _no_fields_locking(MyLokableModel):
    ...     instance.foo = 'bar'

    # Will deactivate locking for all instances of all lockable models
    >>> with _no_fields_locking(Lockable):
    ...     instance.foo = 'bar'

    """

    # Tell pylint that we are allowed to access ``tracking_activated``
    # pylint:disable=protected-access

    cache_key = None
    if not isclass(obj):
        try:
            cache_key = obj.pk
        except AttributeError:
            # ``self.pk`` could not be fetch because we are too early in the initialization of
            # the django model instance
            # At this point we don't need to cache the value because it will be reset soon once
            # the instance will be fully created
            pass
        except StopIteration:
            # PEP 479: StopIteration raised in a generator must be caught to prevent
            # RuntimeError. This can happen during model initialization with polymorphic models.
            pass
        else:
            # Create the cache attribute if it doesn't exist
            if not hasattr(obj.__class__, "tracking_activated_override_cache"):
                obj.__class__.tracking_activated_override_cache = {}
            else:
                # Check if the cache is already set: in this case, we already are in another call of
                # this context manager ad we don't want to clear the cache at the end of THIS call
                if cache_key in obj.__class__.tracking_activated_override_cache:
                    cache_key = None

    # Save the previous value
    old_tracking_activated = obj.tracking_activated

    # Deactivate locking
    # Use object.__setattr__ for instances, type.__setattr__ for classes
    # to avoid triggering our custom __setattr__ which could raise issues
    if isclass(obj):
        type.__setattr__(obj, "tracking_activated", False)
    else:
        object.__setattr__(obj, "tracking_activated", False)

    # Keep that info in cache to use it for another python objects of the same db object
    if cache_key:
        obj.__class__.tracking_activated_override_cache[cache_key] = False

    try:
        # Run the code encapsulated in the ``with`` statement
        yield
    finally:
        # Restore the previous value
        if isclass(obj):
            type.__setattr__(obj, "tracking_activated", old_tracking_activated)
        else:
            object.__setattr__(obj, "tracking_activated", old_tracking_activated)

        # Clear the cache for all python objects of the same db object
        if cache_key:
            del obj.__class__.tracking_activated_override_cache[cache_key]

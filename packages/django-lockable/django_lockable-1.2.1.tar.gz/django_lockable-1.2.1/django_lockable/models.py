"""Base model ``Lockable``, a mixin that allow to forbid some fields to be updated"""

from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models.signals import m2m_changed

from .exceptions import LockedField
from .utils import _no_fields_locking  # pylint:disable=protected-access


class Lockable(models.Model):
    """Base model to deny some fields to be updated once the instance loaded from the database.

    By default all fields are locked. To set some fields as always updatable, add them the the
    ``non_lockable_fields``.

    There is currently no logic on why a lockable field should or should not be updated.
    It's up to the subclasses to override the ``is_field_locked`` method and define what to return.

    Attributes
    ----------
    non_lockable_fields : list
        List of field names on this model that must not be locked.
        A field name is:
        - the name of a field defined on this model, including a FK or M2M.
        - the related name of a field defined on another model pointing to this model.
        There is no need to repeat non lockable fields from parent models when defining
        ones for a subclass.

    _non_lockable_fields_by_class : dict(class: set)
        Will hold the cached set of all non lockable fields by class (defined in the current model
        and all parent models). Should not be used manually: call `get_non_lockable_fields``
        instead.

    _lockable_fields_by_class : dict(class: set)
        Will hold the cached set of all fields by class (defined in the current model and all
        parent models) that could be lockable, ignoring ones defined in ``non_lockable_fields``.
        Should not be used manually: call `get_lockable_fields`` instead.

    _track_fields : boolean
        Set to ``True`` by default, locally changed when calling the context manager
        ``.utils._no_fields_locking``. Used when loading an instance to set its fields.

    LockedFieldException : exception
        The exception to raise when a attempt to edit a locked field is done.
        The exception should expect the instance and the field_name.
        Default to ``.exception.LockedField``.

    Example
    -------

    This example shows how to use ``non_lockable_fields`` with inheritance

    >>> class BaseModel(Lockable):
    ...
    ...     non_lockable_fields = ['bar']
    ...
    ...     # This field will be locked
    ...     foo = models.CharField(max_length=100)
    ...     # This one won't
    ...     bar = models.CharField(max_length=100)
    ...
    ...     class Meta:
    ...         abstract =True
    ...
    ... class MyModel(BaseModel):
    ...
    ...     # We don't need to repeat the non lockable fields from parent models
    ...     non_lockable_fields = ['qux']
    ...
    ...     # This field will be locked
    ...     baz = models.CharField(max_length=100)
    ...     # This one won't
    ...     qux = models.CharField(max_length=100)

    """

    class Meta:
        abstract = True

    _lockable_fields_by_class = {}
    _non_lockable_fields_by_class = {}

    tracking_activated = True

    non_lockable_fields = []

    LockedFieldException = LockedField

    def __init__(self, *args, **kwargs):
        """All fields can be set when creating the instance."""

        with _no_fields_locking(self):
            super().__init__(*args, **kwargs)

    def refresh_from_db(self, *args, **kwargs):
        """All fields can be set when reloading the instance from DB."""

        with _no_fields_locking(self):
            super().refresh_from_db(*args, **kwargs)

    def set_duplicated_field(self, field_name, value):
        """All fields can be set when duplicating the instance."""

        with _no_fields_locking(self):
            super().set_duplicated_field(field_name, value)

    @property
    def is_tracking_activated(self):
        """Tells if we currenty track the fields of this instance.

        Returns
        -------
        bool
            ``True`` by default, but ``False`` when in the ``with`` block of the
            ``.utils._no_fields_locking`` context manager for the instance, its class or any
            other parent class.

        """

        # Check at the instance level
        if not self.tracking_activated:
            return False

        # Check if we are in the ``_no_fields_locking`` context manager for another python
        # object of the same db object
        try:
            key = self.pk
        except AttributeError:
            # ``self.pk`` could not be fetch because we are too early in the initialization of
            # the django model instance
            pass
        else:
            if not getattr(self.__class__, "tracking_activated_override_cache", {}).get(key, True):
                return False

        # Check for each parent class that have the ``tracking_activated`` attribute
        for klass in self.__class__.mro():
            if hasattr(klass, "tracking_activated") and not klass.tracking_activated:
                return False

        return True

    @classmethod
    def get_lockable_fields(cls):
        """Get all the fields of the model that could be locked.

        It is computed only once and cached at class level in ``cls._lockable_fields``.

        """

        if cls not in Lockable._lockable_fields_by_class:
            # Get all fields that are trackable, ie all fields except PK
            fields = [f for f in cls._meta.get_fields() if not getattr(f, "primary_key", False)]

            # Add attribute names (fields end with '_id' if foreign keys)
            Lockable._lockable_fields_by_class[cls] = {getattr(f, "attname", f.name): f for f in fields}

        # Return the cached set
        return Lockable._lockable_fields_by_class[cls]

    @classmethod
    def get_lockable_attname(cls, field_name):
        """Get the real field attribute name for a given field name.

        A "real field attribute name" is for example "author_id" for a foreign key
        named "author".

        Tracking real attribute names allows to let django set the real instance on "author"
        when we update "author_id".

        Parameters
        ----------
        field_name : str
            The name of the field we want to check
            Must be the name of an existing field (or related_name)

        Returns
        -------
        str
            The real attribute name if different from ``field_name``, or given ``field_name``.

        """

        if field_name not in cls.get_lockable_fields():
            try:
                field = cls._meta.get_field(field_name)

            except FieldDoesNotExist:
                # It's not a field, but a simple attribute, so we'll exit the if and return
                # the original attribute name
                pass

            else:
                # We have a field with this name. Check if the "real" name is different
                attname = getattr(field, "attname", field_name)
                if attname != field_name:
                    return attname

        return field_name

    @classmethod
    def get_non_lockable_fields(cls):
        """Get all the fields of the model that must not be locked.

        It read the ``non_lockable_fields`` attribute of the current model and all
        its parents to avoid redefining in sub-models the list of fields defined in
        parents.

        It is computed only once and cached at class level in ``cls._non_lockable_fields``.

        """

        # First time we call this for this class, create the cached set
        if cls not in Lockable._non_lockable_fields_by_class:
            lockable_fields = cls.get_lockable_fields()

            # Fill a temporary variable to set the class attribute atomically at the end
            _non_lockable_fields = set()

            # Get non lockable fields for all parent classes
            for parent_model in cls.__mro__:
                _non_lockable_fields.update(getattr(parent_model, "non_lockable_fields", []))

            # Get the relation ``attname`` if we have the name (ie "author_id" for "author")
            for field_name in list(_non_lockable_fields):
                attname = cls.get_lockable_attname(field_name)
                if attname != field_name:
                    # Remove field like "author"
                    _non_lockable_fields.remove(field_name)
                    # Add "author_id"
                    _non_lockable_fields.add(attname)

            # We keep only fields that are lockable fields
            Lockable._non_lockable_fields_by_class[cls] = _non_lockable_fields.intersection(lockable_fields)

        # Return the cached set
        return Lockable._non_lockable_fields_by_class[cls]

    def is_field_lockable(self, field_name):
        """Tell if the given field name is lockable.

        Parameters
        ----------
        field_name : str
            The name of the field we want to check
            Must be the name of an existing field (or related_name)

        Returns
        -------
        bool
            ``True`` if the field can be locked, ``False`` otherwise

        """

        # In loading mode, no fields can be locked
        if not self.is_tracking_activated:
            return False

        attname = self.get_lockable_attname(field_name)

        return attname in self.get_lockable_fields() and attname not in self.get_non_lockable_fields()

    def is_field_locked(self, field_name):
        """Tell if a field is actually locked.

        Actually this method always returns ``True`` if the field is lockable and the instance
        is not in loading mode.

        This method **MUST** be overridden to add specific logic.

        Parameters
        ----------
        field_name : str
            The name of the field we want to check
            Must be the name of an existing field (or related_name)

        Returns
        -------
        bool
            ``True`` if the field is locked, ``False`` otherwise.

        """

        if not self.is_field_lockable(field_name):
            return False

        # By default we mark the field as locked
        return True

    def __setattr__(self, key, value):
        """Deny updating locked fields.

        Parameters
        ----------
        key : str
            Name of the attribute to update
        value : ?
            New value to set for this attribute

        Raises
        ------
        self.LockedFieldException
            The exception class defined in the ``LockedFieldException`` attribute.
            Raised when the new value is different from the existing one and the key is a locked
            field.

        """

        if key != "tracking_activated" and self.is_tracking_activated:
            # Get, for example, `parent_id` for a `parent` FK
            attname = self.get_lockable_attname(key)

            # We assume that if ``attname`` is different, it's a Django model instance and setting
            # it will, in a second step, set the real key (ie setting a FK  "user" will first
            # pass here with "user", then with "user_id"). So we can ignore the first case, to avoid
            # fetching the object if not already loaded. This happens when loading related objects,
            # like ``myobject.users.all()``, because in this case Django will set the known
            # attribute.
            if attname == key and key in self.get_lockable_fields():
                # We do some checks only if the value is different or is not an attribute yet
                try:
                    # we disable lock in case django tries to set an attribute in the meantime
                    with _no_fields_locking(self):
                        old_value = getattr(self, key)
                except (AttributeError, KeyError):
                    check_value = True
                else:
                    check_value = old_value != value

                if check_value and self.is_field_locked(key):
                    raise self.LockedFieldException(self, key)

        return super().__setattr__(key, value)


# pylint: disable=unused-argument
def m2m_changed_lockable(sender, instance, action, reverse, model, pk_set, **kwargs):
    """Receiver for the ``m2m_changed`` signal to check that m2m are updatable.

    We only check for ``pre_*`` actions, and only if the model declaring the m2m is a subclass of
    ``Lockable``, and in this case we raise an exception if the m2m field is not editable.

    Parameters
    ----------
    sender : through instance
        Instance of the ``through`` model of the m2m relation (automatic or manual)
    action : str
        One of ``pre_add``, ``pre_remove``, ``pre_clear``, ``post_add``, ``post_remove``,
        ``post_clear``
    reverse : bool
        If the m2m is updated from an instance of the model declaring the m2m field (``reverse``
        is ``False``) or from an instance of the model on the other side (``reverse`` is ``False``)

        ``instance``, ``model`` and ``pk_set`` arguments depends on the value of ``reverse``:

        If ``reverse`` is ``False``:
          - ``instance`` is an instance of the model declaring the m2m field
          - ``model`` is the model on the other side of the m2m relation
          - ``pk_set`` are PKs of the model defined in ``model``.
        If ``reverse`` is ``True``:
          - ``instance`` is an instance of the other side of the relation
          - ``model`` is the model declaring the m2m relation
          - ``pk_set`` are PKs of the model defined in ``model``

    Raises
    ------
    self.LockedFieldException
        The exception class defined in the ``LockedFieldException`` attribute.
        If the m2m field on the related versionable instance is not editable.

    """

    # We only care about "pre" actions, to be able to abort an update
    if action not in {"pre_add", "pre_remove", "pre_clear"}:
        return

    # Get the model that defines the m2m relation
    tracked_model = model if reverse else instance.__class__
    related_model = instance.__class__ if reverse else model

    # We only care about ``Lockable`` models
    if not issubclass(tracked_model, Lockable):
        return

    # Get the related field
    related_field = [
        field
        for field in tracked_model._meta.get_fields()
        if isinstance(field, models.ManyToManyField) and field.related_model == related_model
    ][0]

    # Get all the updated instances
    if reverse:
        filters = {}
        if action == "pre_clear":
            # Removed PKs are not given when clearing the relation, so we need to get the
            # ones that have ``instance`` (ie the related entry, at the other side of the m2m
            # relation)
            filters[related_field.name] = instance
        else:
            filters["pk__in"] = pk_set
        instances = tracked_model.objects.filter(**filters)
    else:
        instances = [instance]

    # For each instance, check if the m2m field it is editable and if not, raise
    for instance in instances:
        if instance.is_field_locked(related_field.name):
            raise instance.LockedFieldException(instance, related_field.name)


# Connect the ``m2m_changed_lockable`` method to the ``m2m_signal`` without specifying the
# ``sender`` argument, as we'll do all the check in the function itself.
m2m_changed.connect(m2m_changed_lockable, weak=False, dispatch_uid="m2m_changed_lockable")

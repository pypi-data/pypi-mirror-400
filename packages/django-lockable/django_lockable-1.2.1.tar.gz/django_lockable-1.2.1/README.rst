===============
Django Lockable
===============

Purpose
=======

The ``django-lockable`` app provides a ``Lockable`` model mixin allowing to "lock" a model by
denying the update of its fields under certain conditions to be defined in the models using it.

About
=====

How it works
************

When a model inherits from the ``Lockable`` mixin, automatically all its fields will be locked
against update, as well as ``ManyToMany`` relations.

This is done, for normal fields, by an override of the attribute setter (the ``__setattr__``
method), and for ``ManyToMany``, by catching the ``m2m_changed`` signal ("pre*" actions).

Then, the ``is_field_locked`` method of the model is called, with the name of the field to update
as argument (for a ``ManyToManyField`` that points to the current model, it will be the
``related_name`` of this field).

This method will:

- return ``False`` if the model is currently being loaded (ie during the execution of the
  ``__init__`` and ``refresh_from_db`` methods)
- return ``False`` if the field is "not lockable" (see below)
- return ``True`` in all other cases (It's here that you can override the logic)


Exclude fields
**************

To exclude some fields from the lockable ones, simply add their name to ``non_lockable_fields``
attribute of the model. It's a list (or other iterable), and when a field name is present in it,
the ``is_field_locked`` will always return ``False`` when called with this name.

Note that this list does not need to includes fields to ignore already defined in parent classes:

.. code-block:: python

    class ParentModel(Lockable):
        field1 = models.CharField()
        field2 = models.CharField()

        non_lockable_fields = ['field2']

    class ChildModel(ParentModel):
        field3 = models.CharField()
        field4 = models.CharField()

        non_lockable_fields = ['field4']  # ``field2`` is already included


Specific logic
**************

To add some logic to decide when to lock or not a model, simply override ``is_field_locked`` by
first calling ``super``, and if the result is ``True``, manage your own logic:

.. code-block:: python

    class MyModel(Lockable):
        """Example that lock the model when a flag is True."""

        is_published = models.BooleanField()
        field = models.CharField()

        def is_field_locked(self, field_name):
            locked = super().is_field_locked(field_name)

            if locked:
                locked = self.is_published

            return locked


Update a locked model
*********************

In some case you may want to update a locked model, for example in a shell to debug something, or
in tests.

The ``django_lockable.utils`` module provides a context manager, ``_no_fields_locking`` for this,
and it's what is used to manage the initialization of a object (``__ini__`` and
``__refresh_from_db__``).

It's really not recommended to use it in normal code as it's in violation of the whole principle of
this app. It's why it is prefixed with a ``_`` to mark is a private, but it's documented because of
its usefulness in some cases.

Use it this way:

.. code-block:: python

    # Will deactivate locking for the instance only
    with _no_fields_locking(instance):
        instance.foo = 'bar'

    # Will deactivate locking for all instances of the model
    with _no_fields_locking(MyLokableModel):
        instance.foo = 'bar'

    # Will deactivate locking for all instances of all lockable models
    with _no_fields_locking(Lockable):
        instance.foo = 'bar'


Installation
============

Install from PyPI:

.. code-block:: sh

    pip install django-lockable


Requirements
============

- Python 3.9, 3.10, 3.11, 3.12
- Django 4.2, 5.0, 5.1

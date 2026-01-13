======================
Django-fields-iterator
======================

Purpose
=======

The purpose of the ``django_fields_iterator`` package is to provide a convenient way to iterate on
all fields of a model, or only a subset.

Example
-------

It's as easy as instantiating the ``FieldsIterator`` class with your model, and then iterate:

.. code-block:: python

    from django_fields_iterator import FieldsIterator

    iterator = FieldsIterator(MyModel)

    for field, name, field_type in iterator:
        do_stuff()


The field is the real ``Field`` object from django.
The name is the attribute name to access this name from an instance
the field type is one of ``FieldTypes`` object, as defined later in this document.


Excluding fields by name
------------------------

If you don't want some fields to be returned, you can do it by passing the ``ignore_fields`` to
the ``FieldsIterator`` constructor:

.. code-block:: python

    iterator = FieldsIterator(MyModel, ignore_fields=['afield', 'anotherfield'])


Excluding fields by type
------------------------

Some times you don't want some fields, for example, to exclude the ``ManyToManyField``:

.. code-block:: python

    from django_fields_iterator import FieldsIterator, FieldTypes

    iterator = FieldsIterator(MyModel)

    for field, name, field_type in iterator.iter_fields(exclude=[FieldTypes.M2M]):
        do_stuff()


The ``exclude`` argument is a list that can be empty, or a combination of the following:

- ``FieldTypes.SIMPLE``: For simple fields
- ``FieldTypes.FK``: For foreign keys (and one to one fields)
- ``FieldTypes.M2M``: For many to many fields
- ``FieldTypes.REVERSE_FK``: For reverse foreign keys, ie foreign keys defined on another model, pointing on the model we use
- ``FieldTypes.REVERSE_M2M``: For reverse many to many fields, ie many to many fields defined on another model, pointing on the model we use
- ``FieldTypes.REVERSE_O2O``: For reverse one to one fields, ie one to one fields defined on another model, pointing on the model we use


Including only some field types
-------------------------------

The ``iter_fields`` method also accepts a ``only`` argument, accepting the same kind of value than
the ``exclude`` argument. Both arguments cannot be set at the same time.

If for example you only want simple fields:

.. code-block:: python

    from django_fields_iterator import FieldsIterator, FieldTypes

    iterator = FieldsIterator(MyModel)

    for field, name, field_type in iterator.iter_fields(only=[FieldTypes.SIMPLE]):
        do_stuff()


Iterating fields for a specific type
------------------------------------

The ``FieldsIterator`` class provides methods to iterate on fields of a certain type:

- ``iter_simple_fields``, for fields of type ``FieldTypes.SIMPLE``
- ``iter_foreign_keys``, for fields of type ``FieldTypes.FK``
- ``iter_manytomany_fields``, for fields of type ``FieldTypes.M2M``
- ``iter_reverse_foreign_keys``, for fields of type ``FieldTypes.REVERSE_FK``
- ``iter_reverse_manytomany_fields``, for fields of type ``FieldTypes.REVERSE_M2M``
- ``iter_reverse_onetoone_fields``, for fields of type ``FieldTypes.REVERSE_O2O``


Overriding
----------

The ``FieldsIterator`` provides two methods that are great to override to avoid some fields to be
returned, based on their class for example:

- ``can_return_field``: for fields directly defined on the model
- ``can_return_reverse_field``: for fields defined on another model that point to the current one

They simple accept the field (as returned by the ``get_fields`` django method on the model ``_meta``
attribute) and the field type (maybe useful in subclasses), and should return a boolean.

They simply check if the field name (the accessor name for the reverse fields) is in
the ``ignore_fields`` attribute, but can be overridden to add more logic.

Installation
============

Install from PyPI:

.. code-block:: sh

    pip install django-fields-iterator


Requirements
============

- Python 3.9, 3.10, 3.11, 3.12
- Django 4.2, 5.0, 5.1

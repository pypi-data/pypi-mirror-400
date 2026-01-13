"""Provides the ``FieldsIterator`` class to iterate on a model fields."""

from django.db import models

from .types import FieldTypes


class FieldsIterator:
    """Utility class to iterate on all fields of a model.

    Attributes
    ----------
    model : django.db.models.Model
        The django model for which fields will be iterated
    meta : django.db.models.options.Options
        The ``_meta`` object linked to ``model``
    all_fields : list
        The list of all fields defined on the model, and on other models that point to it
        It's simply the result of calling ``self.meta.get_fields()``
    ignore_fields : set
        The name of the fields on ``model`` that must not be returned by the iterators

    """

    def __init__(self, model, ignore_fields=None):
        self.model = model
        self.meta = model._meta

        self.all_fields = self.meta.get_fields()

        self.ignore_fields = set(ignore_fields or [])

    def can_return_field(self, field, field_type):  # pylint: disable=unused-argument
        """Helper to know if a field (defined on this another model) can be returned by an iterator.

        By default it returns ``True`` except if the name is in the ``self.ignore_fields`` set.

        Parameters
        ----------
        field : django.db.models.fields.Field
            A field defined on the current model
        field_type : str
            The type of the field, one of FieldTypes.allowed_types
            Not used in this default implementation but could be useful in subclasses.

        Returns
        -------
        bool
            ``True`` if the field is returnable. Otherwise ``False``.

        """

        return field.name not in self.ignore_fields

    def can_return_reverse_field(self, field, field_type):  # pylint: disable=unused-argument
        """Helper to know if a related field (on another model) can be returned by an iterator.

        By default it returns ``True`` except if the related name is in the ``self.ignore_fields``
        set.

        Parameters
        ----------
        field : django.db.models.fields.related.ForeignObjectRel
            A "relation field" based on a ForeignKey, OneToOneField or ManyToManyField defined
            on another model (or the same with (``to='self'``), pointing to the current instance.
        field_type : str
            The type of the field, one of FieldTypes.allowed_types
            Not used in this default implementation but could be useful in subclasses.

        Returns
        -------
        bool
            ``True`` if the related field is returnable. Otherwise ``False``.

        """

        return field.get_accessor_name() not in self.ignore_fields

    def iter_simple_fields(self):
        """Iterate on all normal fields (ie non relations) of ``self.model``

        Yields
        ------
        tuple(Field, str, str)
            A tuple with:
            - a ``django.db.models.fields.Field``
            - the name used to access the field from the model
            - the type of field (``FieldTypes.SIMPLE``)

        Notes
        -----
        Primary key is not included in returned fields.

        ``can_return_field`` will be called to check if the field should be returned

        """

        for field in self.all_fields:
            if field.is_relation or field.primary_key:
                continue

            if not self.can_return_field(field, FieldTypes.SIMPLE):
                continue

            yield field, field.name, FieldTypes.SIMPLE

    def iter_foreign_keys(self):
        """Iterate on all foreign keys (including OneToOne fields) defined on ``self.model``

        Yields
        ------
        tuple(ForeignKey, str)
            A tuple with:
            - a ``django.db.models.fields.related.ForeignKey``
            - the name used to access the field from the instance
            - the type of field (``FieldTypes.FK``)

        Notes
        -----
        ``can_return_field`` will be called to check if the field should be returned

        """

        for field in self.all_fields:
            if not isinstance(field, models.ForeignKey):
                continue

            if not self.can_return_field(field, FieldTypes.FK):
                continue

            yield field, field.name, FieldTypes.FK

    def iter_reverse_onetoone_fields(self):
        """Iterate on all OneToOne fields pointing to ``self.model``.

        Yields
        ------
        tuple(OneToOneRel, str)
            A tuple with:
            - a ``django.db.models.fields.related.OneToOneRel``
            - the name used to access the field from the instance
            - the type of field (``FieldTypes.REVERSE_O2O``)

        Notes
        -----
        ``can_return_reverse_field`` will be called to check if the field should be returned

        """

        for field in self.all_fields:
            if not isinstance(field, models.OneToOneRel):
                continue

            if not self.can_return_reverse_field(field, FieldTypes.REVERSE_O2O):
                continue

            yield field, field.get_accessor_name(), FieldTypes.REVERSE_O2O

    def iter_manytomany_fields(self):
        """Iterate on all ManyToMany fields defined on ``self.model``

        Yields
        ------
        tuple(ManyToManyField, str)
            A tuple with:
            - a ``django.db.models.fields.related.ManyToManyField``
            - the name used to access the field from the instance
            - the type of field (``FieldTypes.M2M``)

        Notes
        -----
        ``can_return_field`` will be called to check if the field should be returned

        """
        for field in self.all_fields:
            if not isinstance(field, models.ManyToManyField):
                continue

            if not self.can_return_field(field, FieldTypes.M2M):
                continue

            yield field, field.name, FieldTypes.M2M

    def iter_reverse_manytomany_fields(self):
        """Iterate on all ManyToMany fields pointing to ``self.model``.

        Yields
        ------
        tuple(ManyToManyRel, str)
            A tuple with:
            - a ``django.db.models.fields.related.ManyToManyRel``
            - the name used to access the field from the instance
            - the type of field (``FieldTypes.REVERSE_M2M``)

        Notes
        -----
        ``can_return_reverse_field`` will be called to check if the field should be returned

        """
        for field in self.all_fields:
            if not isinstance(field, models.ManyToManyRel):
                continue

            if not self.can_return_reverse_field(field, FieldTypes.REVERSE_M2M):
                continue

            yield field, field.get_accessor_name(), FieldTypes.REVERSE_M2M

    def iter_reverse_foreign_keys(self):
        """Iterate on all foreign keys fields pointing to ``self.model``.

        The OneToOne related fields, that are also ``ManyToOneRel`` are excluded because already
        managed by the ``iter_reverse_onetoone_fields`` method.

        Yields
        ------
        tuple
            A tuple with:
            - a ``django.db.models.fields.related.ManyToOneRel``
            - the name used to access the field from the instance
            - the type of field (``FieldTypes.REVERSE_FK``)

        Notes
        -----
        ``can_return_reverse_field`` will be called to check if the field should be returned

        """

        for field in self.all_fields:
            if not isinstance(field, models.ManyToOneRel):
                continue

            if isinstance(field, models.OneToOneRel):
                # Managed in ``iter_reverse_onetoone_fields``
                continue

            if not self.can_return_reverse_field(field, FieldTypes.REVERSE_FK):
                continue

            yield field, field.get_accessor_name(), FieldTypes.REVERSE_FK

    def iter_fields(self, exclude=None, only=None):
        """Iterate on all the returnable fields on ``self.model``

        The iterator yields fields in this order:
        - simple fields
        - foreign keys (and one to one fields)
        - related one to one fields (defined on another model, pointing to the current one)
        - many to many fields
        - related many to many fields (defined on another model, pointing to the current one)
        - related foreign keys (defined on another model, pointing to the current one)

        Parameters
        ----------
        exclude : list
            If passed, a list of field types to ignore.
            Cannot be set if ``only`` is set.
            Available field types are the ones available in ``FieldsType``

        only : list
            The reverse of ``exclude``, to only retrieve the fields of the given types.
            Cannot be set if ``exclude`` is set.

        Yields
        ------
        tuple
            A tuple with:
            - a field
            - the name used to access the field from the instance
            - the type of field (``one in ``FieldTypes.allowed_types````)

        Raises
        ------
        ValueError
            - when `only` and `exclude` are both defined
            - when a field type in `only` or `exclude` is not valid

        """

        if only is not None and exclude is not None:
            raise ValueError("`only` and `exclude` are exclusive")

        for container in (only, exclude):
            if not container:
                continue
            for field_type in container:
                if field_type not in FieldTypes:
                    raise ValueError(f"`{field_type}` is not a valid field type")

        for field_type in FieldTypes.allowed_types:
            if exclude is not None and field_type in exclude:
                continue

            if only is not None and field_type not in only:
                continue

            iterator = getattr(self, f"iter_{field_type}")

            yield from iterator()

    def __iter__(self):
        """Iterate on all the returnable fields on ``self.model``

        Simply call ``self.iter_fields`` without arguments.

        """

        return self.iter_fields()

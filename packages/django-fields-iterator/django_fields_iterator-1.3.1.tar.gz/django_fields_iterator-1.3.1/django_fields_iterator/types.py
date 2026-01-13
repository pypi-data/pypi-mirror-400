"""Provides "constants" to use for ``only`` and ``exclude`` arguments of ``FieldsIterator``"""

from django.db import models


# pylint: disable=invalid-name
class _FieldTypes:
    """Provides "constants" to use for ``only`` and ``exclude`` arguments of ``FieldsIterator``

    Attributes
    ----------
    SIMPLE : str
        The attribute to use for simple fields
    FK : str
        The attribute to use for foreign keys (and one to one fields)
    M2M : str
        The attribute to use for many to many fields
    REVERSE_FK : str
        The attribute to use for reverse foreign keys, ie foreign keys defined on another model,
        pointing on the model we use
    REVERSE_M2M : str
        The attribute to use for reverse many to many fields, ie many to many fields defined on
        another model, pointing on the model we use
    REVERSE_O2O : str
        The attribute to use for reverse one to one fields, ie one to one fields defined on
        another model, pointing on the model we use
    allowed_types : list of str
        List with all allowed types that can be used.
        Used to check validity of ``only`` and ``exclude`` arguments in the iterator, and to
        go through the whole list of fields in a consistent order.
    direct_types: list of str
        Extract from `allowed_types` for fields directly defined on a model: SIMPLE and FK
    reverse_types: list of str
        Extract from `allowed_types` for fields defined on another (REVERSE_*)
    reverse_matching: dict
        A dict having as keys all types that can have a reverse type, and as values, the reverse
        types.

    """

    SIMPLE = "simple_fields"

    FK = "foreign_keys"
    M2M = "manytomany_fields"

    REVERSE_FK = "reverse_foreign_keys"
    REVERSE_M2M = "reverse_manytomany_fields"
    REVERSE_O2O = "reverse_onetoone_fields"

    # simple fields, then fields that point to a simple instance, than fields that point to many
    allowed_types = [SIMPLE, FK, REVERSE_O2O, M2M, REVERSE_M2M, REVERSE_FK]

    direct_types = [SIMPLE, FK]
    reverse_types = [REVERSE_O2O, REVERSE_M2M, REVERSE_FK]

    reverse_matching = {
        FK: REVERSE_FK,
        M2M: REVERSE_M2M,
        REVERSE_FK: FK,
        REVERSE_M2M: M2M,
        REVERSE_O2O: FK,
    }

    def __contains__(self, item):
        """Check if the given item is in the allowed types

        Parameters
        ----------
        item
            The item to search for in ``allowed_types``

        Returns
        -------
        bool
            ``True`` if `item` is in ``allowed_types`, otherwise ``False``

        """

        return item in self.allowed_types

    @classmethod
    def for_field(cls, field):
        """Get the field type given a django ``Field``

        Parameters
        ----------
        field: models.Field
            The django field for which we want the type

        Returns
        -------
        str
            The field type

        Raises
        ------
        ValueError
            When the given argument is not a django field

        """

        if isinstance(field, models.ForeignKey):
            return cls.FK
        if isinstance(field, models.ManyToManyField):
            return cls.M2M
        if isinstance(field, models.ManyToManyRel):
            return cls.REVERSE_M2M
        if isinstance(field, models.OneToOneRel):
            return cls.REVERSE_O2O
        if isinstance(field, models.ManyToOneRel):
            return cls.REVERSE_FK
        if isinstance(field, models.Field):
            return cls.SIMPLE

        raise ValueError("`FieldTypes.for_field` expects a django `Field`")


# Provide an instance instead of the class (to make ``__contains__`` work)
FieldTypes = _FieldTypes()

"""Provides ``Hashable``, a base django model for the ``django-hashable-file-fields`` app.

The simplest usage is:

>>> class MyModel(HashableFileFieldsBaseModel):
...     img = models.ImageField(...)
...     hash = models.CharField(...)
...
...     hashable_fields = [
...         ('img', 'hash')
...     ]

It will save the md5 hash value of the ``img`` field in the ``hash`` field on each save, raising
on exception.

"""

from django.db import models

from .hashers import md5_hash


class HashableFileFieldsBaseModel(models.Model):
    """A base model to easily compute and store hashed values of file fields.

    Attributes
    ----------
    hashable_fields : list
        The list of all fields to hash. This may be the only thing to configure in models that
        inherit from ``HashableFileFieldsBaseModel``.
        Each entry is a tuple composed of two or three elements:
        1. The name of the file field to hash
        2. The name of the file that will contain the hash
        3. The function to use to compute the hash. If not set, the function defined in the
           ``default_hash_function`` attribute will be used (default to ``md5_hash`` from
            ``hashable.hashers``.

    default_hash_function : str
        The function used to compute the hash of a field if the third element of a tuple defined in
        ``hashable_fields`` is not set.
        This function takes a file field and its parent model instance, and return a computed
        hash of this field.

    compute_hash_method_pattern : str
        Instead of using an external hash function (or use ``default_hash_function``, it's
        possible to use a method of the model to compute the hash for a field. This function
        must follow the pattern defined in ``compute_hash_method_pattern``, which is a formatable
        string where ``%(field_name)s`` and ``%(hash_field_name)s`` will be replaced before
        calling it.
        The method must accept the name of the field to hash, and optionally an external hash
        function and must return the hashed value to save.
        The default pattern is ``'compute_hash_%(field_name)s'`` so if the file to hash is named
        ``img``, the method must be named ``compute_hash_img``.

    default_compute_hash_method : function
        The method that will be used if no methd exists following the pattern defined in
        ``compute_hash_method_pattern``.

    Example
    -------
    The minimal configuration to use this ``HashableFileFieldsBaseModel`` model is to simply
    inherit from it and define the name of the field to hash and the field in which to save the
    hash, this way:

    >>> class MyModel(HashableFileFieldsBaseModel):
    ...     img = models.ImageField(...)
    ...     hash = models.CharField(...)
    ...
    ...     hashable_fields = [
    ...         ('img', 'hash')
    ...     ]

    With this, all the default configuration will be used:
    - the ``compute_hash`` default method will be called
    - this method will call ``md5_hash`` function, raising if something bad happen in it.

    To save a default hash field in the hash function raise, you can define the
    ``default_hash_function`` this way:

    >>> class MyModel(HashableFileFieldsBaseModel):
    ...     # ...
    ...     default_hash_function = with_default(settings.EMPTY_FILE_HASH, md5_hash))

    Or, for a specific field:

    >>> class MyModel(HashableFileFieldsBaseModel):
    ...     # ...
    ...     hashable_fields = [
    ...         ('img', 'hash'),
    ...         ('img2', 'hash2', with_default(settings.EMPTY_FILE_HASH, md5_hash))
    ...         # ``with_default`` without hash function will use the default one
    ...         ('img3', 'hash3', with_default(settings.EMPTY_FILE_HASH))
    ...     ]

    OR it can be defined with a method:

    >>> class MyModel(HashableFileFieldsBaseModel):
    ...     # ...
    ...     hashable_fields = [
    ...         ('img', 'hash'),
    ...         ('img2', 'hash2')
    ...     ]
    ...
    ...     def compute_hash_img2(self, field_name, hash_method=None):
    ...         return do_some_computation_with_field_name_and_maybe_hash_method()

    """

    hashable_fields = []
    default_hash_function = md5_hash
    compute_hash_method_pattern = "compute_hash_%(field_name)s"
    default_compute_hash_method = "compute_hash"

    class Meta:
        abstract = True

    def compute_hash(self, field_name, hash_function=None):
        """Default method that will call a hash_function to compute the hash of a file field.

        Parameters
        ----------
        fied_name : str
            The name of the file field to be hashed

        hash_function : function, optional
            The function that takes a file field, its parent model instance, and return a computed
            hash of this field.
            If not set, the function defined in ``default_hash_function`` will be used.
            A "hash function" expect the file field of an instance (ie ``self.img`` if ``img`` is
            a ``ImageField``), and the instance itself.


        Returns
        -------
            The result of the hash function.

        """

        if hash_function is None:
            # If we get it on the instance using ``self.default_hash_function``, we have a bound
            # method. But we really want the original function not taking ``self`` as first
            # argument so we get it on the class.
            hash_function = self.__class__.default_hash_function

        if not hash_function:
            raise RuntimeError("Cannot call default compute hash method without `hash_function`")

        return hash_function(getattr(self, field_name), self)

    def compute_hashable_fields(self):
        """Compute, and set, all the hash defined in the ``hashable_fields`` attribute.

        For each entry of ``hashable_fields`` it will check if a method matching
        ``compute_hash_method_pattern`` exists and if not, will use ``compute_hash``.
        Then this method will be called to get the hash, and this hash will be set in ``self``.
        The current instance will *not* be saved by this method.

        """
        for hash_infos in self.hashable_fields:
            field_name, hash_field_name = hash_infos[:2]

            # We may not have defined ``hash_function`` in the tuple
            compute_hash_function = hash_infos[2] if len(hash_infos) == 3 else None

            # Get the method to call based on the field name and hash field name.
            hash_method_name = self.compute_hash_method_pattern % {
                "field_name": field_name,
                "hash_field_name": hash_field_name,
            }

            # The default compute method will be used if this specific method doesn't exist.
            hash_method = getattr(self, hash_method_name, getattr(self, self.default_compute_hash_method))

            # Call the method, and set the value in the hash field
            setattr(self, hash_field_name, hash_method(field_name, compute_hash_function))

    def save(self, *args, **kwargs):
        """Compute the hash fields then call ``super`` to save the instance."""

        self.compute_hashable_fields()

        return super().save(*args, **kwargs)

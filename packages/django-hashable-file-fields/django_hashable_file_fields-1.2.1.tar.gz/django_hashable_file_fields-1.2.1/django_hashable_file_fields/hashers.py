"""Simple hashers and utils for the ``django-hashable-file-fields`` app."""

import hashlib


def md5_hash(file_field, instance):  # pylint: disable=unused-argument
    """An example hasher that uses ``hashlib.md5`` to compute the hash of a file field.

    Parameters
    ----------
    file_field : django.db.models.fields.files.FileField
        The file field (or img...) for which we want to compute the hash.
    instance : HashableFileFieldsBaseModel
        The instance holding this field.

    Returns
    -------
    str
        The computed hash for the given file field.


    Example
    -------

    >>> class MyModel(HashableFileFieldsBaseModel):
    ...     img = models.ImageField(...)
    ...     hash = models.CharField(...)
    ...
    ...     hashable_fields = [
    ...         ('img', 'hash', md5_hash)
    ...     ]

    """

    md5 = hashlib.md5()
    for chunk in file_field.chunks():
        md5.update(chunk)
    # Now we reset the offset of the ``file_field`` to 0, for other readers
    file_field.seek(0)
    return md5.hexdigest()


def with_default(default, hash_function=None, exceptions=None):
    """Decorator to a hasher that will return a default value when an exception occurs.

    Parameters
    ----------
    default : ?
        The default value to return as a hash value when an exception is raised during the call
        to ``hash_function``.

    hash_function : function, optional
        The function that takes a file field, its parent model instance, and return a computed
        hash of this field.
        If not defined, the default function defined on the model at call time will be used.

    exceptions : iterable, optional
        A list (or other iterable) of exceptions classes for which to return the value defined in
        ``default`` when an exception is raised during the call to the ``hash_function``.
        Other exceptions will be raised.
        By default all exceptions based on``Exception`` are handled.

    Returns
    -------
        Either the value returned by calling ``hash_function``, or the default value if a valid
        exception is raised.

    Example
    -------

    Using the default hash function:

    >>> class MyModel(HashableFileFieldsBaseModel):
    ...     img = models.ImageField(...)
    ...     hash = models.CharField(...)
    ...
    ...     hashable_fields = [
    ...         ('img', 'hash', with_default(settings.EMPTY_FILE_HASH))
    ...     ]

    Using a specific hash function:

    >>> class MyModel(HashableFileFieldsBaseModel):
    ...     img = models.ImageField(...)
    ...     hash = models.CharField(...)
    ...
    ...     hashable_fields = [
    ...         ('img', 'hash', with_default(settings.EMPTY_FILE_HASH, md5_hash))
    ...     ]

    """

    exceptions = tuple(exceptions) if exceptions is not None else (Exception,)

    def func(file_field, instance):
        """Calls the hash function and returns the default value in case of exception."""
        try:
            final_hash_function = hash_function

            # Use the default hash function if none was passed to ``with_default``
            if not final_hash_function:
                # If we get it on the instance using ``instance.default_hash_function``, we have a
                # bound method. But we really want the original function not taking ``self`` as
                # first argument so we get it on the class.
                final_hash_function = instance.__class__.default_hash_function

            return final_hash_function(file_field, instance)

        except exceptions:  # pylint: disable=catching-non-exception
            return default

    return func

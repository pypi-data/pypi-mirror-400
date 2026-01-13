""" Rally Secret Store support.

Provides management features for secrets and secret stores

Import example:

>>> from rally import secret
"""
__all__ = [
    'get_secret',
    'save_secret'
]

from urllib.parse import quote_plus

from . import exceptions
from ._session import _getSession



def get_secret(secret_store_name, secret_name):
    """ Retrieve a secret value from a secret store.

    :param secret_name: Name of the secret.
    :type secret_name: str
    :param secret_store_name: Name of the secret store. See secret stores in Rally.
    :type secret_store_name: str

    Usage:

    >>> secret.get_secret('YetiSecret', 'YakStore')
    Th3y4k5ay58a4!
    """
    secret_name = quote_plus(quote_plus(secret_name))

    value = _getSession().get(f'v1.0/secretStore/{secret_store_name}/{secret_name}').json()['secret']
    if not value:
        raise exceptions.NotFound(f'secret {secret_name}')
    return value


def save_secret(secret_store_name, secret_name, secret_value, kms_key_id=None, auto_delete=None):
    """ Save a secret name/value in a secret store.

    :param secret_name: Name of the secret.
    :type secret_name: str
    :param secret_value: Value of the secret.
    :type secret_value: str
    :param secret_store_name: Name of the secret store. See secret stores in Rally.
    :type secret_store_name: str
    :param kms_key_id: Id of AWS KMS key, defaults to `None`
    :type kms_key_id: str, optional
    :param auto_delete: Flag indicating automatic deletion of the secret after a job accesses the secret and
        *successfully* completes, defaults to `None` (meaning the secret will not be deleted)
    :type auto_delete: bool, optional

    Usage:

    >>> secret.save_secret('YetiSecret', 'Th3y4k5ay58a4!', 'YakStore', kms_key_id=1, auto_delete=True)
    """
    secret_name = quote_plus(quote_plus(secret_name))

    payload = {'value': secret_value, 'kmsKeyId': kms_key_id}
    if auto_delete:
        payload['autoDelete'] = True

    _getSession().post(f'v1.0/secretStore/{secret_store_name}/{secret_name}', json=payload)

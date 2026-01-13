import functools
import json
import posixpath
from urllib.parse import urlparse

from . import exceptions
from ._session import _getSession


@functools.lru_cache()
def _getStoragePartsFromUrl(url):
    """
    Returns a storage location representation and filename that corresponds to a supplied URL.

    --> Utilize new search capability of v2/storageLocations/ to find the correct location
    --> Use the parsed.path minus the location prefix to find file name

    :param url: the url that corresponds to a Rally storage location.
        URLs for directories should end in a `/`
        URLs containing file names should not end in a `/`
    :type url: str
    :return: a storage location schema object (please see API documentation) and an object name
    :rtype: tuple(dict, str)
    """
    # Use the API to get the storage location
    resp = _getSession().get('v2/storageLocations', params={'search': json.dumps({'url': url})})

    # Rally API calls that error are thrown as RallyApiErrors, so only check for results
    location = resp.json()['data']
    if not location:
        raise exceptions.NotFound(url)
    if len(location) > 1:
        raise exceptions.RallyApiError(f'ambiguous location url {url}')

    location = location[0]

    # Figure out the filename, which involves removing the prefix from the path. Use `str.partition` to accomplish this.
    # RSL: split on location name, and add '/' to the end. `posixpath.join` will not add an extra one ;)
    if urlparse(url).scheme == 'rsl':
        separator = posixpath.join(location['attributes']['name'], '')
    # all others: split on `bucketName/prefix/`: We cannot use just prefix, as the prefix could be None or '/'.
    #  posixpath.join helps us here, too: repeating empty strings result in one trailing slash
    else:
        separator = posixpath.join(location['attributes']['bucketName'], location['attributes']['prefix'] or '', '')

    return location, url.partition(separator)[2]

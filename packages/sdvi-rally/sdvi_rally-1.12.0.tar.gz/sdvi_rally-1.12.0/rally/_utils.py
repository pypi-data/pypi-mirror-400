from datetime import datetime, timezone


def _posixToDatetime(ts, tz=timezone.utc):
    """ Converts POSIX timestamps (sec) to timezone-aware (UTC) datetime """
    if not ts:
        return
    return datetime.fromtimestamp(ts, tz=tz)


def _toDatetime(ts_ms, tz=timezone.utc):
    """ Converts Rally API timestamps (ms) to timezone-aware (UTC) datetime """
    if not ts_ms:
        return
    return datetime.fromtimestamp(ts_ms / 1000, tz=tz)


def _datetimeToTimestamp(d):
    """ Converts a timezone-aware datetime to a Rally API timestamp (ms) """
    return int(_datetimeToPosixTimestamp(d) * 1000)


def _datetimeToPosixTimestamp(d):
    """ Converts a timezone-aware datetime to a POSIX timestamp (sec) """
    if not isinstance(d, datetime):
        raise TypeError('must be a datetime')

    # https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive
    assert d.tzinfo is not None and d.tzinfo.utcoffset(d) is not None, 'datetime must be timezone aware'

    return d.timestamp()

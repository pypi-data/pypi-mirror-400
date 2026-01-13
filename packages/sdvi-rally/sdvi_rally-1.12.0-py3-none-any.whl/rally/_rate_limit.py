import collections
import os
import threading
from functools import wraps
from time import monotonic, sleep


class RateLimit:
    """
    Provides a context manager that limits invocations to a number of calls per time period.

    Time period is a sliding window. Rate-limited invocations block. The first thread to get limited
    will be the first to proceed. Order in which subsequently blocked requests proceed is undetermined.

    Note: only limits the rate at which requests are made. Request duration (and hence number of in-flight requests)
    is not taken into account.

    Usage:
    >>> from time import time
    >>> f = lambda: None
    >>> limit = RateLimit(period_seconds=0.1, calls_per_period=5)
    >>> for i in range(16):
    ...     with limit:
    ...         f()
    >>> limit.wait_time
    >>> # 0.1 second wait before calls 6 through 10, 11 through 15, and 16, respectively.
    >>> 0.3 < limit.wait_time < 0.4
    True
    >>> limit.call_count
    16
    """

    def __init__(self, period_seconds, calls_per_period, debug_label=None):
        self._period = period_seconds
        self._calls_per_period = calls_per_period
        self.debug = debug_label
        self._call_log = collections.deque()  # timestamps of when recent call were allowed
        self._semaphore = threading.Semaphore(1)  # acquired by threads wanting to make a request
        self._call_count = 0
        self._wait_time = 0.0

    def __enter__(self):
        start = monotonic()
        # Semaphore is held by thread next in line to make a request. So acquire and hold it until allowed to proceed.
        with self._semaphore:
            if self._call_count == 0:
                # This logic is done here (on the first pass through) because the decorator creation logic runs at
                # class load before PYTEST_CURRENT_TEST is set.
                self._period = _get_adjusted_period(self._period)
            while True:
                # Forget about calls that happened before the sliding period window
                now = monotonic()
                expire_before = now - self._period
                while self._call_log and self._call_log[0] < expire_before:
                    self._call_log.pop()

                if len(self._call_log) < self._calls_per_period:
                    # not throttled; release semaphore and allow request to proceed
                    wait = monotonic() - start
                    self._wait_time += wait
                    self._call_count += 1
                    if self.debug:
                        print(
                            f"{self.debug}: {len(self._call_log)} calls in last {self._period} seconds; proceeding after waiting {round(wait, 2)}s. Total {round(self._wait_time,2)} wait across {self._call_count} calls")
                    self._call_log.append(now)
                    return

                # throttled; keep the semaphore and sleep. Subsequent requests from other threads will block on the
                # semaphore until this thread was allowed to proceed.
                next_opportunity = self._call_log[0] + self._period  # time a request drops out of window, creating room
                sleep(next_opportunity - now)

    def __exit__(self, *args):
        pass

    @property
    def call_count(self):
        return self._call_count

    @property
    def wait_time(self):
        return self._wait_time

    @property
    def period(self):
        return self._period

    @property
    def calls_per_period(self):
        return self._calls_per_period


def rate_limit(period_seconds, calls_per_period, debug_label=None):
    """
    Provides a decorator for applying RateLimit

    Usage:
    >>> from time import time
    >>> @rate_limit(period_seconds=0.1, calls_per_period=5)
    ... def f():
    ...     pass
    >>> start = time()
    >>> for i in range(16):
    ...         f()
    >>> 0.3 < time() - start < 0.4
    True
    """
    limit = RateLimit(period_seconds, calls_per_period, debug_label=debug_label)

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):
            with limit:
                return function(*args, **kwargs)

        return wrapper

    return decorator


def _get_adjusted_period(period):
    # Rate limit makes unit tests slow (and needlessly so, since they're hitting betamax or local API, not
    # a live silo). So check if it is a unit test and increase to 10x if so.
    return period / 10.0 if "PYTEST_CURRENT_TEST" in os.environ else period

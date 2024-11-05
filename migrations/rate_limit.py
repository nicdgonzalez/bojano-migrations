import random
from typing import NamedTuple

__all__ = (
    "RateLimit",
    "get_sleep_duration_between_requests",
)


class RateLimit(NamedTuple):
    """Represents the maximum number of requests allowed per second.

    Examples
    --------
    For an API that has a limit of 20 requests per 10 seconds:

    >>> RateLimit(requests_max=20, duration_sec=10.0)
    """

    requests_max: int
    duration_sec: float


def get_sleep_duration_between_requests(
    requests_total: int, rate_limit: RateLimit
) -> float:
    """Based on the total number of requests, calculates how long the program
    should sleep between requests to not exceed the target API's rate limit.

    Parameters
    ----------
    requests_total:
        The total number of requests waiting to be sent
    rate_limit: tuple
        The maximum requests allowed, and the duration of that limit

    Returns
    -------
    :class:`float`: The number of seconds to sleep between requests.
    """
    # For a rate limit of 60 requests per 60 seconds, a maximum sleep duration
    # of 1 second is sufficient regardless of the number of requests.
    # You do not benefit from sleeping longer than this value,
    # as the rate limit would have already reset by the time you finished.
    upper_limit = rate_limit.duration_sec / rate_limit.requests_max

    if requests_total <= rate_limit.requests_max:
        value = 0.0
    else:
        value = (requests_total / rate_limit.requests_max) * upper_limit
        value += random.randint(0, 100) / 100.0

    return min(upper_limit, value)

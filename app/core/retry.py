import time
from typing import Callable, TypeVar

T = TypeVar("T")

def retry(
        operation: Callable[[], T],
        retries: int = 3,
        initial_delay_second: float = 0.1,
        backoff_multiplier: float = 2.0
) -> T:
    """
    :param operation:
    :param retries:
    :param initial_delay_second:
    : param backoff_multiplier:
    :return:
    """

    last_exception = None
    delay = initial_delay_second
    for attempt in range (retries):
        try:
            return operation()
        except Exception as exc:
            last_exception = exc
            if attempt == retries -1:
                break

            time.sleep(delay)
            delay *= backoff_multiplier

    raise last_exception
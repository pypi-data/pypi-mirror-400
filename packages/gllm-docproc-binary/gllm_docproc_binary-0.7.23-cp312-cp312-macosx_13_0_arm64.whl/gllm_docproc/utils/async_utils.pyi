from typing import Awaitable, TypeVar

T = TypeVar('T')

def run_async_in_sync(coro: Awaitable[T]) -> T:
    '''Run an async coroutine from synchronous code safely.

    This function handles the common scenario where you need to call an async function
    from synchronous code, but you\'re not sure if there\'s already an event loop running.

    Args:
        coro (Awaitable[T]): The coroutine to run.

    Returns:
        T: The result of the coroutine.

    Example:
        >>> async def fetch_data():
        ...     return "data"
        >>> result = run_async_in_sync(fetch_data())
        >>> print(result)  # "data"
    '''

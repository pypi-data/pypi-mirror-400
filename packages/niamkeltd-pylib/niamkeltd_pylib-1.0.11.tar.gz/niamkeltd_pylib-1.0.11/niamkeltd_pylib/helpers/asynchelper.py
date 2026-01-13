# https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale#timeout
import asyncio, concurrent.futures, logging
from . import debughelper
from niamkeltd_pylib.models.exceptions.timeoutexception import TimeoutException

FILE_NAME = debughelper.get_filename()

async def run_with_timeout_async(coroutine, timeout: float):
    """
    Run an async coroutine with a timeout.

    :param coroutine: The coroutine to run.
    :param timeout float: The maximum time to allow the coroutine to run (in seconds).
    :return: The result of the coroutine if it completes in time, or throws an exceptions if it times out.
    """

    try:
        logging.info("[%s] Beginning async call with %s second timeout", FILE_NAME, timeout)
        result = await asyncio.wait_for(coroutine, timeout)
        logging.info("[%s] Completed async call with %s second timeout", FILE_NAME, timeout)
        return result

    except asyncio.TimeoutError:
        raise TimeoutException(f"[{FILE_NAME}] Async execution exceeded {timeout} seconds.")

def run_with_timeout(func, timeout, *args, **kwargs):
    """
    Run a function with a timeout.

    :param func: The function to run.
    :param timeout float: The maximum time to allow the function to run (in seconds).
    :param args: The arguments to pass to the function.
    :param kwargs: The keyword arguments to pass to the function.
    :return: The result of the function if it completes in time, or throws an exceptions if it times out.
    """

    with concurrent.futures.ThreadPoolExecutor() as executor:

        future = executor.submit(func, *args, **kwargs)

        try:
            logging.info("[%s] Beginning call with %s second timeout", FILE_NAME, timeout)
            result = future.result(timeout=timeout)  # Wait for the result with a timeout
            logging.info("[%s] Completed call with %s second timeout", FILE_NAME, timeout)
            return result

        except concurrent.futures.TimeoutError:
            raise TimeoutException(f"[{FILE_NAME}] Execution exceeded {timeout} seconds.")
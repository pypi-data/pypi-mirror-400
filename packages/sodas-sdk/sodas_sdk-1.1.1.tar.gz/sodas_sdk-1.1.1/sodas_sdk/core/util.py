from time import sleep
from typing import Any, Callable, Dict, NoReturn, TypeVar

from requests import RequestException, Response

from .error import RetryLimitReachedError

# Constants
SYSTEM_PROCESSING = "SYSTEM_PROCESSING"
LARGE_ENOUGH_NUMBER = 10000

T = TypeVar("T")


# Retry response format
class RetryResponse(Dict[str, Any]):
    errorCode: str
    flag: str


# Error handling
def handle_error(error: Exception) -> NoReturn:
    if hasattr(error, "response"):
        response = getattr(error, "response")
        if response is not None:
            print("Error response:", response.text)
            print("Error status:", response.status_code)
    elif hasattr(error, "request"):
        print("No response received:", getattr(error, "request"))
    else:
        print("Error:", str(error))
    raise error


def handle_request_exception(error: RequestException) -> NoReturn:
    if error.response is not None:
        try:
            error_data = error.response.json()
            if "error" in error_data:
                print(f"Error: {error.response.status_code} - {error_data['error']}")
            elif "message" in error_data:
                print(f"Error: {error.response.status_code} - {error_data['message']}")
            else:
                print(f"Error: {error.response.status_code} - {error_data}")
        except Exception:
            print("Failed to parse error response as JSON.")
    else:
        if getattr(error, "errno", None) == "ECONNREFUSED":
            print("CONNECTION ERROR")
        else:
            print(
                {
                    "message": str(error),
                    "code": getattr(error, "code", None),
                    "status": (
                        getattr(error.response, "status_code", None)
                        if hasattr(error, "response")
                        else None
                    ),
                }
            )
    raise error


def destroy(obj: Any) -> None:
    if hasattr(obj, "__dict__"):
        obj.__dict__.clear()


def retry_request(
    request_fn: Callable[[], Response], max_retries: int = 30, delay_ms: int = 1000
) -> Response:
    retries = 0
    while retries < max_retries:
        try:
            response = request_fn()
            if response.status_code == 200:
                data = response.json()
                if data.get("flag") != SYSTEM_PROCESSING:
                    return response
                else:
                    sleep(delay_ms / 1000)
                    retries += 1
            else:
                return response
        except Exception as e:
            raise e
    raise RetryLimitReachedError(max_retries)

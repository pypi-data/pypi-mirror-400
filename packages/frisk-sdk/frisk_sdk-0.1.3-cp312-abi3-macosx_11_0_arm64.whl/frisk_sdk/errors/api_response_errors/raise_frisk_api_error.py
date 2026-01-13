from typing import Optional

from frisk_sdk.errors import FriskError
from frisk_sdk.errors.api_response_errors import (
    FriskBadRequestError,
    FriskForbiddenError,
    FriskConflictError,
    FriskPayloadTooLargeError,
    FriskUnprocessableEntityError,
    FriskRateLimitError,
    FriskInternalServerError,
    FriskBadGatewayError,
    FriskServiceUnavailableError,
    FriskGatewayTimeoutError,
    FriskAPIResponseError,
    FriskBaseURLNotFoundError,
    FriskInvalidAPIKeyError,
    FriskGenericAPIResponseError,
)


def get_frisk_api_error_from_http_status(
    status: int, details: Optional[str] = None
) -> FriskError:
    if status == 400:
        return FriskBadRequestError()
    elif status == 401:
        return FriskInvalidAPIKeyError()
    elif status == 403:
        return FriskForbiddenError()
    elif status == 404:
        return FriskBaseURLNotFoundError()
    elif status == 409:
        return FriskConflictError()
    elif status == 413:
        return FriskPayloadTooLargeError()
    elif status == 422:
        return FriskUnprocessableEntityError()
    elif status == 429:
        return FriskRateLimitError()
    elif status == 500:
        return FriskInternalServerError()
    elif status == 502:
        return FriskBadGatewayError()
    elif status == 503:
        return FriskServiceUnavailableError()
    elif status == 504:
        return FriskGatewayTimeoutError()
    else:
        return FriskGenericAPIResponseError(status_code=status, error_details=details)

from ..configuration_errors import FriskConfigurationError
from ..frisk_error import FriskError


class FriskAuthenticationError(FriskError):
    """Raised when authentication fails."""


class FriskInvalidAPIKeyError(FriskAuthenticationError):
    code = "invalid_api_key"
    message = """\
Frisk API key authentication failed.
    The provided API key is invalid, expired, or has been revoked.
    Please verify that you are using a valid Frisk API key.

    You can:
        • Double-check the API key value
        • Regenerate a new API key from the Frisk dashboard
        • Ensure the key matches the correct environment (dev vs prod)
"""


class FriskAPIResponseError(FriskError):
    """Raised when the Frisk API returns an unexpected HTTP response."""


class FriskGenericAPIResponseError(FriskAPIResponseError):
    """Raised when the Frisk API returns an unexpected HTTP response that doesn't fit into any concrete subclass."""

    code = "generic_api_response_error"

    def __init__(self, status_code: int, error_details: str | None = None):
        self.status_code = status_code
        self.error_details = error_details

        details_block = ""
        if error_details:
            details_block = f"\n    Error details:\n        {error_details}"

        self.message = f"""\
Unexpected response from Frisk API.
    Status code: {status_code}.{details_block}

    If this persists, verify your configuration and contact support.\
"""
        super().__init__()


class FriskBadRequestError(FriskAPIResponseError):
    code = "bad_request"
    message = """\
Frisk API returned 400 Bad Request.
    The request was rejected due to invalid parameters or malformed input.
    Please verify your request payload and try again.

    If you believe this is a bug, contact support with request details.\
"""


class FriskForbiddenError(FriskAPIResponseError):
    code = "forbidden"
    message = """\
Frisk API returned 403 Forbidden.
    Your API key is valid, but it does not have permission to perform this action.
    This can also occur if your organization or project is disabled.

    Please verify your permissions and account status.\
"""


class FriskConflictError(FriskAPIResponseError):
    code = "conflict"
    message = """\
Frisk API returned 409 Conflict.
    The request could not be completed due to a conflict with the current state.
    This can happen when creating a resource that already exists, or when state has changed.

    Please retry or reconcile the conflicting state before trying again.\
"""


class FriskPayloadTooLargeError(FriskAPIResponseError):
    code = "payload_too_large"
    message = """\
Frisk API returned 413 Payload Too Large.
    The request payload exceeds the maximum allowed size.

    Please reduce the payload size and try again.\
"""


class FriskUnprocessableEntityError(FriskAPIResponseError):
    code = "unprocessable_entity"
    message = """\
Frisk API returned 422 Unprocessable Entity.
    The request was well-formed, but failed validation.
    Please verify required fields and value formats.

    If available, inspect error details returned by the API for field-level feedback.\
"""


class FriskRateLimitError(FriskAPIResponseError):
    code = "rate_limited"
    message = """\
Frisk API returned 429 Too Many Requests.
    Your requests are being rate limited.

    Please back off and retry after a short delay.
    If you need higher limits, contact support.\
"""


class FriskInternalServerError(FriskAPIResponseError):
    code = "internal_server_error"
    message = """\
Frisk API returned 500 Internal Server Error.
    An unexpected error occurred on the Frisk service.

    Please retry. If the issue persists, contact support.\
"""


class FriskBadGatewayError(FriskAPIResponseError):
    code = "bad_gateway"
    message = """\
Frisk API returned 502 Bad Gateway.
    The Frisk service received an invalid response from an upstream dependency.

    Please retry. If the issue persists, contact support.\
"""


class FriskServiceUnavailableError(FriskAPIResponseError):
    code = "service_unavailable"
    message = """\
Frisk API returned 503 Service Unavailable.
    The Frisk service is temporarily unavailable (maintenance or overload).

    Please retry after a short delay.\
"""


class FriskGatewayTimeoutError(FriskAPIResponseError):
    code = "gateway_timeout"
    message = """\
Frisk API returned 504 Gateway Timeout.
    The Frisk service did not respond in time (upstream timeout).

    Please retry. If the issue persists, contact support.\
"""


class FriskBaseURLNotFoundError(FriskConfigurationError):
    code = "base_url_not_found"
    message = """\
Frisk base URL returned 404 Not Found.
    The configured Frisk base URL does not appear to be a valid Frisk API endpoint.
    This usually indicates an incorrect or malformed base URL.

    Please verify that:
        • FRISK_BASE_URL points to the Frisk API (not a dashboard or website)
        • The URL includes the correct scheme (https://)
        • There are no extra or missing path segments

    Example:
        export FRISK_BASE_URL="https://api.frisk.ai"
        frisk = Frisk()\
"""

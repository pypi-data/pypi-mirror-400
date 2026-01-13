from frisk_sdk.errors import FriskError as FriskError


class FriskConfigurationError(FriskError):
    """Raised when the SDK is misconfigured."""


class MissingAPIKeyError(FriskConfigurationError):
    code = "missing_api_key"
    message = """\
Frisk API key not configured.
    You must provide an API key either:
        • via the `api_key` argument: Frisk(api_key="...")
        • or via the environment variable FRISK_API_KEY
    Example:
        export FRISK_API_KEY="..."
        frisk = Frisk()\
"""


class MissingBaseURLError(FriskConfigurationError):
    code = "missing_base_url"
    message = """\
Frisk base URL not configured.
    You must provide a Frisk base URL either:
        • via the environment variable FRISK_BASE_URL
        • or by explicitly passing `base_url` when initializing Frisk

    Example:
        export FRISK_BASE_URL="https://api.frisk.ai"
        frisk = Frisk()\
"""

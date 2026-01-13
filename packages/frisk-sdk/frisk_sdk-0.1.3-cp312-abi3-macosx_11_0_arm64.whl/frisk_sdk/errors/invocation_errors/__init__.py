from ..frisk_error import FriskError


class FriskInvocationError(FriskError):
    """Raised when the SDK is used incorrectly at runtime."""


class MissingFriskSessionContextError(FriskInvocationError):
    code = "missing_frisk_session_context"
    message = """\
Missing required Frisk execution context.
    Frisk requires a `context` object containing a valid `frisk_session`
    to be passed when invoking an agent.

    Please ensure your agent invocation includes:
        context={"frisk_session": frisk_session}

    Example:
        frisk = Frisk()
        frisk_session = frisk.create_session()
        agent.invoke(
            inputs,
            config={...},
            context={"frisk_session": frisk_session},
        )

    This context is required for policy enforcement, tracing,
    and tool-call governance.\
"""


class InvalidFriskSessionError(FriskInvocationError):
    code = "invalid_frisk_session"
    message = """\
Invalid Frisk session provided.
    A `frisk_session` was found in the execution context, but it is not a valid FriskSession object.

    Please ensure you are passing a valid, active Frisk session:
    
    Example:
        frisk = Frisk()
        frisk_session = frisk.create_session()
        agent.invoke(
            inputs,
            config={...},
            context={"frisk_session": frisk_session},
        )
"""

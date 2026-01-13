class FriskError(Exception):
    """Base class for all Frisk SDK errors."""

    message: str
    code: str | None = None
    docs_url: str | None = None

    def __init__(self):
        super().__init__(self.message)

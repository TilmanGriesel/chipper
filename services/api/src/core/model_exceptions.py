class ModelNotFoundError(Exception):
    """Raised when a required model is not available and auto-pull is disabled."""

    pass

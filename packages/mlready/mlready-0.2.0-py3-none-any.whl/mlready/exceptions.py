class MLReadyError(Exception):
    """Base exception for mlready."""
    pass


class RecipeError(MLReadyError):
    """Raised when a recipe is invalid or cannot be applied."""
    pass

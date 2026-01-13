import logging

from .operators import (
    ArrayOperator,
    ComparisonOperator,
    EqualityOperator,
    ExistsOperator,
    OperatorHandler,
    RegexOperator,
)

logger = logging.getLogger(__name__)


class OperatorRegistry:
    """
    Registry of operator handlers.
    Follows Open/Closed: New operators can be added
    without modifying existing code.
    """

    def __init__(self):
        self._handlers = []
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default MongoDB operators."""
        # Order matters! More specific handlers first
        self.register(RegexOperator())
        self.register(ArrayOperator())
        self.register(ComparisonOperator())
        self.register(ExistsOperator())
        self.register(EqualityOperator())  # Fallback

    def register(self, handler: OperatorHandler):
        """Register a new operator handler."""
        self._handlers.append(handler)

    def get_handler(self, key: str) -> OperatorHandler:
        """Get the appropriate handler for a filter key."""
        fallback = None

        for handler in self._handlers:
            if isinstance(handler, EqualityOperator):
                fallback = handler
                continue

            try:
                if handler.can_handle(key):
                    return handler
            except Exception as e:
                # Log but continue to next handler
                # - allows graceful degradation
                logger.warning(
                    f"Error in handler {handler.__class__.__name__} "
                    f"for key '{key}': {e}",
                    exc_info=True,
                )
                continue

        if fallback:
            return fallback

        raise ValueError(f"No handler found for key: {key}")

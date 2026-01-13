class HistoryError(Exception):
    """Base exception for history-related errors."""

    pass


class HistoryNotFoundError(HistoryError):
    """Raised when a history entry is not found."""

    pass


class HistoryAccessDeniedError(HistoryError):
    """Raised when access to history is denied."""

    pass


def raise_for_history_error_detail(detail: str) -> Exception:
    """
    Factory function to raise appropriate history error based on detail message.

    Args:
        detail: Error detail message from API

    Returns:
        Appropriate HistoryError subclass instance
    """
    detail_lower = detail.lower() if detail else ""

    if "not found" in detail_lower:
        return HistoryNotFoundError(detail)
    elif "access denied" in detail_lower or "permission" in detail_lower:
        return HistoryAccessDeniedError(detail)
    else:
        return HistoryError(detail)

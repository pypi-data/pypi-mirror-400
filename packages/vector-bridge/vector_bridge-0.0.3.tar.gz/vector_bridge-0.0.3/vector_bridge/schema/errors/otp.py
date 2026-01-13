class OTPError(Exception):
    """Base exception for OTP-related errors."""

    pass


class OTPInvalidError(OTPError):
    """Raised when OTP code is invalid."""

    pass


class OTPExpiredError(OTPError):
    """Raised when OTP code has expired."""

    pass


class OTPGenerationError(OTPError):
    """Raised when OTP generation fails."""

    pass


def raise_for_otp_error_detail(detail: str) -> Exception:
    """
    Factory function to raise appropriate OTP error based on detail message.

    Args:
        detail: Error detail message from API

    Returns:
        Appropriate OTPError subclass instance
    """
    detail_lower = detail.lower() if detail else ""

    if "invalid" in detail_lower:
        return OTPInvalidError(detail)
    elif "expired" in detail_lower:
        return OTPExpiredError(detail)
    elif "generation" in detail_lower or "generate" in detail_lower:
        return OTPGenerationError(detail)
    else:
        return OTPError(detail)

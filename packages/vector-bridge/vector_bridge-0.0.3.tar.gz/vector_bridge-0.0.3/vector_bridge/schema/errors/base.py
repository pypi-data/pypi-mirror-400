from enum import StrEnum


class BaseError(Exception):
    """Base class for general authentication or base-level errors."""


class IncorrectUsernameOrPassword(BaseError):
    """Raised when the username or password is incorrect."""


class BaseErrorDetail(StrEnum):
    INCORRECT_USERNAME_OR_PASSWORD = "Incorrect username or password"

    def to_exception(self) -> type[BaseError]:
        """Return the exception class that corresponds to this Base error detail."""
        mapping = {
            BaseErrorDetail.INCORRECT_USERNAME_OR_PASSWORD: IncorrectUsernameOrPassword,
        }
        return mapping[self]


def raise_for_base_error_detail(detail: str) -> None:
    """
    Raises the corresponding BaseError based on the given error detail string.
    """
    try:
        detail_enum = BaseErrorDetail(detail)
    except ValueError as e:
        raise BaseError(detail) from e
    raise detail_enum.to_exception()(detail)

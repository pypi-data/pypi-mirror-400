from enum import StrEnum


class WorkflowError(Exception):
    """Base class for Workflow-related errors."""


class WorkflowAlreadyExists(WorkflowError):
    """Raised when a workflow with this ID already exists."""


class WorkflowNotCreated(WorkflowError):
    """Raised when a workflow was not created."""


class WorkflowNotFound(WorkflowError):
    """Raised when a workflow was not found."""


class WorkflowGenericError(WorkflowError):
    """Raised for unspecified workflow-related errors."""


class WorkflowErrorDetail(StrEnum):
    ALREADY_EXISTS = "Workflow with this ID already exists"
    NOT_CREATED = "Workflow was not created"
    NOT_FOUND = "Workflow not found"
    GENERIC_ERROR = "Something went wrong. Try again later"

    def to_exception(self) -> type[WorkflowError]:
        """Return the exception class that corresponds to this workflow error detail."""
        mapping = {
            WorkflowErrorDetail.ALREADY_EXISTS: WorkflowAlreadyExists,
            WorkflowErrorDetail.NOT_CREATED: WorkflowNotCreated,
            WorkflowErrorDetail.NOT_FOUND: WorkflowNotFound,
            WorkflowErrorDetail.GENERIC_ERROR: WorkflowGenericError,
        }
        return mapping[self]


def raise_for_workflow_detail(detail: str) -> None:
    """
    Raises the corresponding WorkflowError based on the given workflow error detail string.
    """
    try:
        detail_enum = WorkflowErrorDetail(detail)
    except ValueError as e:
        raise WorkflowError(detail) from e
    raise detail_enum.to_exception()(detail)

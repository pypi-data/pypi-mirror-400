"""
Event definitions for service layer.

These events are published via EventBus to decouple services from UI.
"""

from dataclasses import dataclass
from vultus_serpentis import Event
from theca_procurator.domain.models import DuplicationOperation, OperationResult


@dataclass
class ProgressEvent(Event):
    """Published when operation progress changes.

    Attributes:
        current: Current operation number (1-indexed)
        total: Total number of operations
        percentage: Progress percentage (0-100)
        message: Optional progress message
    """

    current: int
    total: int
    percentage: float
    message: str = ""


@dataclass
class OperationStartedEvent(Event):
    """Published when an individual operation starts.

    Attributes:
        operation: The operation that started
    """

    operation: DuplicationOperation


@dataclass
class OperationCompletedEvent(Event):
    """Published when an individual operation completes successfully.

    Attributes:
        result: The operation result
    """

    result: OperationResult


@dataclass
class OperationFailedEvent(Event):
    """Published when an individual operation fails.

    Attributes:
        result: The operation result with error information
    """

    result: OperationResult


@dataclass
class ExecutionCompletedEvent(Event):
    """Published when entire execution completes.

    Attributes:
        total_operations: Total number of operations
        successful: Number of successful operations
        failed: Number of failed operations
        cancelled: Whether execution was cancelled
    """

    total_operations: int
    successful: int
    failed: int
    cancelled: bool = False

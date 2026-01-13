"""
Domain models for folder duplication operations.

This module defines the core data structures used throughout the application
for planning, executing, and tracking folder duplication operations.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional
from datetime import datetime


class OperationStatus(Enum):
    """Status of an operation."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


@dataclass
class DuplicationOperation:
    """Represents a single folder duplication operation.

    Attributes:
        source_path: Path to the source folder to copy
        destination_path: Path where the folder will be copied
        folder_name: Name of the destination folder
        status: Current status of the operation
        error_message: Error message if operation failed
    """

    source_path: Path
    destination_path: Path
    folder_name: str
    status: OperationStatus = OperationStatus.PENDING
    error_message: Optional[str] = None

    @property
    def full_destination_path(self) -> Path:
        """Get the full destination path including folder name."""
        return self.destination_path / self.folder_name

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.folder_name} -> {self.full_destination_path}"


@dataclass
class DuplicationPlan:
    """Represents a complete folder duplication plan.

    Attributes:
        source_path: Path to the source folder
        destination_path: Base destination path
        base_name: Base name for duplicated folders
        count: Number of folders to create
        start_number: Starting number for sequencing
        padding: Number of digits for zero-padding
        operations: List of individual duplication operations
        created_at: Timestamp when plan was created
    """

    source_path: Path
    destination_path: Path
    base_name: str
    count: int
    start_number: int
    padding: int
    operations: list[DuplicationOperation] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate plan parameters and generate operations."""
        if self.count < 1:
            raise ValueError("Count must be at least 1")
        if self.start_number < 0:
            raise ValueError("Start number must be non-negative")
        if self.padding < 1:
            raise ValueError("Padding must be at least 1")
        if not self.base_name:
            raise ValueError("Base name cannot be empty")

        # Generate operations if not provided
        if not self.operations:
            self._generate_operations()

    def _generate_operations(self) -> None:
        """Generate individual duplication operations based on plan parameters."""
        self.operations = []
        for i in range(self.count):
            number = self.start_number + i
            folder_name = f"{self.base_name}{str(number).zfill(self.padding)}"

            operation = DuplicationOperation(
                source_path=self.source_path,
                destination_path=self.destination_path,
                folder_name=folder_name,
            )
            self.operations.append(operation)

    @property
    def total_operations(self) -> int:
        """Get total number of operations in the plan."""
        return len(self.operations)

    @property
    def completed_operations(self) -> int:
        """Get number of completed operations."""
        return sum(
            1 for op in self.operations
            if op.status == OperationStatus.COMPLETED
        )

    @property
    def failed_operations(self) -> int:
        """Get number of failed operations."""
        return sum(
            1 for op in self.operations
            if op.status == OperationStatus.FAILED
        )

    @property
    def progress_percentage(self) -> float:
        """Get progress as a percentage (0-100)."""
        if self.total_operations == 0:
            return 0.0
        completed = sum(
            1 for op in self.operations
            if op.status in (OperationStatus.COMPLETED, OperationStatus.FAILED,
                             OperationStatus.SKIPPED, OperationStatus.CANCELLED)
        )
        return (completed / self.total_operations) * 100.0


@dataclass
class OperationResult:
    """Result of executing a duplication operation.

    Attributes:
        operation: The operation that was executed
        success: Whether the operation succeeded
        error_message: Error message if operation failed
        duration_seconds: How long the operation took
    """

    operation: DuplicationOperation
    success: bool
    error_message: Optional[str] = None
    duration_seconds: float = 0.0

    def __str__(self) -> str:
        """Return string representation."""
        status = "SUCCESS" if self.success else "FAILED"
        msg = f"{status}: {self.operation.folder_name}"
        if self.error_message:
            msg += f" ({self.error_message})"
        return msg

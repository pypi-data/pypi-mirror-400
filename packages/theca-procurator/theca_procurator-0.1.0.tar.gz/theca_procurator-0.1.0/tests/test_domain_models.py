"""
Unit tests for domain models.
"""

import sys
from pathlib import Path
from datetime import datetime
import pytest

# Add theca_procurator to path
_main_dir = Path(__file__).parent.parent
if str(_main_dir) not in sys.path:
    sys.path.insert(0, str(_main_dir))

from theca_procurator.domain.models import (
    OperationStatus,
    DuplicationOperation,
    DuplicationPlan,
    OperationResult,
)


class TestOperationStatus:
    """Tests for OperationStatus enum."""

    def test_status_values(self) -> None:
        """Test that all expected status values exist."""
        assert OperationStatus.PENDING.value == "pending"
        assert OperationStatus.IN_PROGRESS.value == "in_progress"
        assert OperationStatus.COMPLETED.value == "completed"
        assert OperationStatus.FAILED.value == "failed"
        assert OperationStatus.SKIPPED.value == "skipped"
        assert OperationStatus.CANCELLED.value == "cancelled"


class TestDuplicationOperation:
    """Tests for DuplicationOperation model."""

    def test_create_operation(self) -> None:
        """Test creating a duplication operation."""
        source = Path("/source/folder")
        dest = Path("/dest")
        name = "Episode 001"

        op = DuplicationOperation(
            source_path=source,
            destination_path=dest,
            folder_name=name
        )

        assert op.source_path == source
        assert op.destination_path == dest
        assert op.folder_name == name
        assert op.status == OperationStatus.PENDING
        assert op.error_message is None

    def test_full_destination_path(self) -> None:
        """Test full_destination_path property."""
        op = DuplicationOperation(
            source_path=Path("/source"),
            destination_path=Path("/dest"),
            folder_name="Test 01"
        )

        assert op.full_destination_path == Path("/dest/Test 01")

    def test_string_representation(self) -> None:
        """Test string representation."""
        op = DuplicationOperation(
            source_path=Path("/source"),
            destination_path=Path("/dest"),
            folder_name="Test 01"
        )

        str_repr = str(op)
        assert "Test 01" in str_repr
        assert "/dest" in str_repr or "\\dest" in str_repr  # Handle Windows paths


class TestDuplicationPlan:
    """Tests for DuplicationPlan model."""

    def test_create_plan_with_valid_params(self) -> None:
        """Test creating a plan with valid parameters."""
        plan = DuplicationPlan(
            source_path=Path("/source"),
            destination_path=Path("/dest"),
            base_name="Episode ",
            count=5,
            start_number=1,
            padding=3
        )

        assert plan.source_path == Path("/source")
        assert plan.destination_path == Path("/dest")
        assert plan.base_name == "Episode "
        assert plan.count == 5
        assert plan.start_number == 1
        assert plan.padding == 3
        assert len(plan.operations) == 5
        assert isinstance(plan.created_at, datetime)

    def test_plan_generates_operations(self) -> None:
        """Test that plan automatically generates operations."""
        plan = DuplicationPlan(
            source_path=Path("/source"),
            destination_path=Path("/dest"),
            base_name="Test ",
            count=3,
            start_number=10,
            padding=2
        )

        assert len(plan.operations) == 3
        assert plan.operations[0].folder_name == "Test 10"
        assert plan.operations[1].folder_name == "Test 11"
        assert plan.operations[2].folder_name == "Test 12"

    def test_plan_with_zero_padding(self) -> None:
        """Test plan with single digit padding."""
        plan = DuplicationPlan(
            source_path=Path("/source"),
            destination_path=Path("/dest"),
            base_name="Item",
            count=3,
            start_number=1,
            padding=1
        )

        assert plan.operations[0].folder_name == "Item1"
        assert plan.operations[1].folder_name == "Item2"
        assert plan.operations[2].folder_name == "Item3"

    def test_plan_with_large_padding(self) -> None:
        """Test plan with large padding."""
        plan = DuplicationPlan(
            source_path=Path("/source"),
            destination_path=Path("/dest"),
            base_name="File",
            count=2,
            start_number=5,
            padding=5
        )

        assert plan.operations[0].folder_name == "File00005"
        assert plan.operations[1].folder_name == "File00006"

    def test_plan_validation_count(self) -> None:
        """Test that plan validates count parameter."""
        with pytest.raises(ValueError, match="Count must be at least 1"):
            DuplicationPlan(
                source_path=Path("/source"),
                destination_path=Path("/dest"),
                base_name="Test",
                count=0,
                start_number=1,
                padding=2
            )

    def test_plan_validation_start_number(self) -> None:
        """Test that plan validates start_number parameter."""
        with pytest.raises(ValueError, match="Start number must be non-negative"):
            DuplicationPlan(
                source_path=Path("/source"),
                destination_path=Path("/dest"),
                base_name="Test",
                count=1,
                start_number=-1,
                padding=2
            )

    def test_plan_validation_padding(self) -> None:
        """Test that plan validates padding parameter."""
        with pytest.raises(ValueError, match="Padding must be at least 1"):
            DuplicationPlan(
                source_path=Path("/source"),
                destination_path=Path("/dest"),
                base_name="Test",
                count=1,
                start_number=1,
                padding=0
            )

    def test_plan_validation_base_name(self) -> None:
        """Test that plan validates base_name parameter."""
        with pytest.raises(ValueError, match="Base name cannot be empty"):
            DuplicationPlan(
                source_path=Path("/source"),
                destination_path=Path("/dest"),
                base_name="",
                count=1,
                start_number=1,
                padding=2
            )

    def test_total_operations_property(self) -> None:
        """Test total_operations property."""
        plan = DuplicationPlan(
            source_path=Path("/source"),
            destination_path=Path("/dest"),
            base_name="Test",
            count=7,
            start_number=1,
            padding=2
        )

        assert plan.total_operations == 7

    def test_completed_operations_property(self) -> None:
        """Test completed_operations property."""
        plan = DuplicationPlan(
            source_path=Path("/source"),
            destination_path=Path("/dest"),
            base_name="Test",
            count=5,
            start_number=1,
            padding=2
        )

        # Initially no operations completed
        assert plan.completed_operations == 0

        # Mark some as completed
        plan.operations[0].status = OperationStatus.COMPLETED
        plan.operations[1].status = OperationStatus.COMPLETED

        assert plan.completed_operations == 2

    def test_failed_operations_property(self) -> None:
        """Test failed_operations property."""
        plan = DuplicationPlan(
            source_path=Path("/source"),
            destination_path=Path("/dest"),
            base_name="Test",
            count=5,
            start_number=1,
            padding=2
        )

        # Initially no operations failed
        assert plan.failed_operations == 0

        # Mark some as failed
        plan.operations[0].status = OperationStatus.FAILED
        plan.operations[1].status = OperationStatus.FAILED
        plan.operations[2].status = OperationStatus.FAILED

        assert plan.failed_operations == 3

    def test_progress_percentage(self) -> None:
        """Test progress_percentage property."""
        plan = DuplicationPlan(
            source_path=Path("/source"),
            destination_path=Path("/dest"),
            base_name="Test",
            count=4,
            start_number=1,
            padding=2
        )

        # Initially 0%
        assert plan.progress_percentage == 0.0

        # Mark one as completed (25%)
        plan.operations[0].status = OperationStatus.COMPLETED
        assert plan.progress_percentage == 25.0

        # Mark another as failed (50%)
        plan.operations[1].status = OperationStatus.FAILED
        assert plan.progress_percentage == 50.0

        # Mark another as skipped (75%)
        plan.operations[2].status = OperationStatus.SKIPPED
        assert plan.progress_percentage == 75.0

        # Mark last as cancelled (100%)
        plan.operations[3].status = OperationStatus.CANCELLED
        assert plan.progress_percentage == 100.0


class TestOperationResult:
    """Tests for OperationResult model."""

    def test_create_successful_result(self) -> None:
        """Test creating a successful operation result."""
        op = DuplicationOperation(
            source_path=Path("/source"),
            destination_path=Path("/dest"),
            folder_name="Test 01"
        )

        result = OperationResult(
            operation=op,
            success=True,
            duration_seconds=1.5
        )

        assert result.operation == op
        assert result.success is True
        assert result.error_message is None
        assert result.duration_seconds == 1.5

    def test_create_failed_result(self) -> None:
        """Test creating a failed operation result."""
        op = DuplicationOperation(
            source_path=Path("/source"),
            destination_path=Path("/dest"),
            folder_name="Test 01"
        )

        result = OperationResult(
            operation=op,
            success=False,
            error_message="Permission denied",
            duration_seconds=0.1
        )

        assert result.operation == op
        assert result.success is False
        assert result.error_message == "Permission denied"
        assert result.duration_seconds == 0.1

    def test_string_representation_success(self) -> None:
        """Test string representation for successful result."""
        op = DuplicationOperation(
            source_path=Path("/source"),
            destination_path=Path("/dest"),
            folder_name="Test 01"
        )

        result = OperationResult(operation=op, success=True)
        str_repr = str(result)

        assert "SUCCESS" in str_repr
        assert "Test 01" in str_repr

    def test_string_representation_failure(self) -> None:
        """Test string representation for failed result."""
        op = DuplicationOperation(
            source_path=Path("/source"),
            destination_path=Path("/dest"),
            folder_name="Test 01"
        )

        result = OperationResult(
            operation=op,
            success=False,
            error_message="Disk full"
        )
        str_repr = str(result)

        assert "FAILED" in str_repr
        assert "Test 01" in str_repr
        assert "Disk full" in str_repr

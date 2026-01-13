"""
Unit tests for duplication services.
"""

import sys
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# Add theca_procurator to path
_main_dir = Path(__file__).parent.parent
if str(_main_dir) not in sys.path:
    sys.path.insert(0, str(_main_dir))

from theca_procurator.domain.models import (
    DuplicationPlan,
    OperationStatus,
)
from theca_procurator.services.duplication import (
    DuplicationPlanBuilder,
    DuplicationService,
)
from theca_procurator.services.events import (
    ProgressEvent,
    OperationStartedEvent,
    OperationCompletedEvent,
    OperationFailedEvent,
    ExecutionCompletedEvent,
)


class TestDuplicationPlanBuilder:
    """Tests for DuplicationPlanBuilder."""

    def test_build_plan_with_valid_params(self, tmp_path: Path) -> None:
        """Test building a plan with valid parameters."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        plan = DuplicationPlanBuilder.build_plan(
            source_path=source,
            destination_path=dest,
            base_name="Test ",
            count=3,
            start_number=1,
            padding=2
        )

        assert isinstance(plan, DuplicationPlan)
        assert plan.source_path == source
        assert plan.destination_path == dest
        assert plan.base_name == "Test "
        assert plan.count == 3
        assert len(plan.operations) == 3

    def test_build_plan_creates_destination(self, tmp_path: Path) -> None:
        """Test that build_plan creates destination directory."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest" / "nested"

        assert not dest.exists()

        DuplicationPlanBuilder.build_plan(
            source_path=source,
            destination_path=dest,
            base_name="Test",
            count=1,
            start_number=1,
            padding=2
        )

        assert dest.exists()
        assert dest.is_dir()

    def test_build_plan_source_not_exists(self, tmp_path: Path) -> None:
        """Test that build_plan raises error if source doesn't exist."""
        source = tmp_path / "nonexistent"
        dest = tmp_path / "dest"

        with pytest.raises(FileNotFoundError, match="Source path does not exist"):
            DuplicationPlanBuilder.build_plan(
                source_path=source,
                destination_path=dest,
                base_name="Test",
                count=1,
                start_number=1,
                padding=2
            )

    def test_build_plan_source_not_directory(self, tmp_path: Path) -> None:
        """Test that build_plan raises error if source is not a directory."""
        source = tmp_path / "file.txt"
        source.write_text("content")
        dest = tmp_path / "dest"

        with pytest.raises(ValueError, match="Source path is not a directory"):
            DuplicationPlanBuilder.build_plan(
                source_path=source,
                destination_path=dest,
                base_name="Test",
                count=1,
                start_number=1,
                padding=2
            )


class TestDuplicationService:
    """Tests for DuplicationService."""

    def test_service_initialization(self) -> None:
        """Test service initialization."""
        service = DuplicationService()

        assert service.is_running is False
        assert service.is_paused is False

    def test_service_with_custom_event_bus(self) -> None:
        """Test service with custom event bus."""
        mock_bus = MagicMock()
        service = DuplicationService(event_bus=mock_bus)

        assert service.event_bus == mock_bus

    def test_execute_plan_simple(self, tmp_path: Path) -> None:
        """Test executing a simple plan."""
        # Create source folder with content
        source = tmp_path / "source"
        source.mkdir()
        (source / "file.txt").write_text("test content")

        # Build plan
        dest = tmp_path / "dest"
        plan = DuplicationPlanBuilder.build_plan(
            source_path=source,
            destination_path=dest,
            base_name="Copy",
            count=2,
            start_number=1,
            padding=1
        )

        # Execute
        service = DuplicationService()
        service.execute_plan(plan)
        service.wait_for_completion(timeout=5.0)

        # Verify results
        assert (dest / "Copy1").exists()
        assert (dest / "Copy2").exists()
        assert (dest / "Copy1" / "file.txt").read_text() == "test content"
        assert (dest / "Copy2" / "file.txt").read_text() == "test content"

    def test_execute_plan_publishes_events(self, tmp_path: Path) -> None:
        """Test that execution publishes progress events."""
        # Create source
        source = tmp_path / "source"
        source.mkdir()

        # Build plan
        dest = tmp_path / "dest"
        plan = DuplicationPlanBuilder.build_plan(
            source_path=source,
            destination_path=dest,
            base_name="Test",
            count=2,
            start_number=1,
            padding=1
        )

        # Track events
        events = []

        def capture_event(event):
            events.append(event)

        # Execute with event tracking
        mock_bus = MagicMock()
        mock_bus.publish.side_effect = capture_event

        service = DuplicationService(event_bus=mock_bus)
        service.execute_plan(plan)
        service.wait_for_completion(timeout=5.0)

        # Verify events were published
        assert len(events) > 0

        # Check for completion event
        completion_events = [e for e in events if isinstance(e, ExecutionCompletedEvent)]
        assert len(completion_events) == 1
        assert completion_events[0].total_operations == 2
        assert completion_events[0].successful == 2

    def test_execute_plan_already_running(self, tmp_path: Path) -> None:
        """Test that execute_plan raises error if already running."""
        source = tmp_path / "source"
        source.mkdir()
        dest = tmp_path / "dest"

        plan = DuplicationPlanBuilder.build_plan(
            source_path=source,
            destination_path=dest,
            base_name="Test",
            count=1,
            start_number=1,
            padding=1
        )

        service = DuplicationService()
        service.execute_plan(plan)

        # Try to execute again while running
        with pytest.raises(RuntimeError, match="already executing"):
            service.execute_plan(plan)

        service.wait_for_completion(timeout=5.0)

    def test_pause_and_resume(self, tmp_path: Path) -> None:
        """Test pause and resume functionality."""
        # Create source with some content to slow down copy
        source = tmp_path / "source"
        source.mkdir()
        for i in range(10):
            (source / f"file{i}.txt").write_text("x" * 1000)

        # Build plan with multiple operations
        dest = tmp_path / "dest"
        plan = DuplicationPlanBuilder.build_plan(
            source_path=source,
            destination_path=dest,
            base_name="Test",
            count=5,
            start_number=1,
            padding=1
        )

        service = DuplicationService()
        
        # Pause before starting
        service.execute_plan(plan)
        service.pause()
        assert service.is_paused is True

        # Wait a bit while paused
        time.sleep(0.2)

        # Resume
        service.resume()
        assert service.is_paused is False

        # Wait for completion
        service.wait_for_completion(timeout=10.0)

        # All operations should complete
        assert plan.completed_operations == 5

    def test_cancel_execution(self, tmp_path: Path) -> None:
        """Test cancelling execution."""
        # Create source with content to slow down operations
        source = tmp_path / "source"
        source.mkdir()
        for i in range(20):
            (source / f"file{i}.txt").write_text("x" * 5000)

        # Build plan with many operations
        dest = tmp_path / "dest"
        plan = DuplicationPlanBuilder.build_plan(
            source_path=source,
            destination_path=dest,
            base_name="Test",
            count=20,
            start_number=1,
            padding=2
        )

        # Track events
        events = []

        def capture_event(event):
            events.append(event)

        mock_bus = MagicMock()
        mock_bus.publish.side_effect = capture_event

        service = DuplicationService(event_bus=mock_bus)
        service.execute_plan(plan)

        # Cancel after allowing first operation to start
        time.sleep(0.05)
        service.cancel()

        # Wait for completion
        service.wait_for_completion(timeout=10.0)

        # Check that execution was cancelled
        completion_events = [e for e in events if isinstance(e, ExecutionCompletedEvent)]
        assert len(completion_events) == 1
        assert completion_events[0].cancelled is True

        # Not all operations should be completed
        assert plan.completed_operations < 20

    def test_operation_skipped_if_exists(self, tmp_path: Path) -> None:
        """Test that operation is skipped if destination exists."""
        # Create source
        source = tmp_path / "source"
        source.mkdir()

        # Create destination that already exists
        dest = tmp_path / "dest"
        dest.mkdir()
        existing = dest / "Test1"
        existing.mkdir()

        # Build plan
        plan = DuplicationPlanBuilder.build_plan(
            source_path=source,
            destination_path=dest,
            base_name="Test",
            count=2,
            start_number=1,
            padding=1
        )

        # Track events
        events = []

        def capture_event(event):
            events.append(event)

        mock_bus = MagicMock()
        mock_bus.publish.side_effect = capture_event

        service = DuplicationService(event_bus=mock_bus)
        service.execute_plan(plan)
        service.wait_for_completion(timeout=5.0)

        # First operation should be skipped
        assert plan.operations[0].status == OperationStatus.SKIPPED

        # Second operation should succeed
        assert plan.operations[1].status == OperationStatus.COMPLETED

        # Check for failed event (skipped counts as failed)
        failed_events = [e for e in events if isinstance(e, OperationFailedEvent)]
        assert len(failed_events) >= 1

    def test_operation_failure_handling(self, tmp_path: Path) -> None:
        """Test handling of operation failures."""
        # Create source
        source = tmp_path / "source"
        source.mkdir()

        # Build plan
        dest = tmp_path / "dest"
        plan = DuplicationPlanBuilder.build_plan(
            source_path=source,
            destination_path=dest,
            base_name="Test",
            count=2,
            start_number=1,
            padding=1
        )

        # Track events
        events = []

        def capture_event(event):
            events.append(event)

        mock_bus = MagicMock()
        mock_bus.publish.side_effect = capture_event

        # Mock shutil.copytree to fail on first operation
        original_copytree = shutil.copytree

        def mock_copytree(src, dst, *args, **kwargs):
            if "Test1" in str(dst):
                raise PermissionError("Access denied")
            return original_copytree(src, dst, *args, **kwargs)

        with patch('shutil.copytree', side_effect=mock_copytree):
            service = DuplicationService(event_bus=mock_bus)
            service.execute_plan(plan)
            service.wait_for_completion(timeout=5.0)

        # First operation should fail
        assert plan.operations[0].status == OperationStatus.FAILED
        assert "Access denied" in (plan.operations[0].error_message or "")

        # Second operation should succeed
        assert plan.operations[1].status == OperationStatus.COMPLETED

        # Check completion event
        completion_events = [e for e in events if isinstance(e, ExecutionCompletedEvent)]
        assert len(completion_events) == 1
        assert completion_events[0].successful == 1
        assert completion_events[0].failed == 1

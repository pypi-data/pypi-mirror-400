"""
Folder duplication services.

This module provides services for building duplication plans and executing
folder duplication operations with pause/resume/cancel support.
"""

import logging
import shutil
import time
import threading
from pathlib import Path
from typing import Optional
from vultus_serpentis import EventBus

from theca_procurator.domain.models import (
    DuplicationPlan,
    DuplicationOperation,
    OperationResult,
    OperationStatus,
)
from theca_procurator.services.events import (
    ProgressEvent,
    OperationStartedEvent,
    OperationCompletedEvent,
    OperationFailedEvent,
    ExecutionCompletedEvent,
)


class DuplicationPlanBuilder:
    """Builds duplication plans from user inputs."""

    @staticmethod
    def build_plan(
        source_path: Path,
        destination_path: Path,
        base_name: str,
        count: int,
        start_number: int,
        padding: int,
    ) -> DuplicationPlan:
        """Build a duplication plan.

        Args:
            source_path: Path to source folder
            destination_path: Base destination path
            base_name: Base name for duplicated folders
            count: Number of folders to create
            start_number: Starting number for sequencing
            padding: Number of digits for zero-padding

        Returns:
            DuplicationPlan instance

        Raises:
            ValueError: If parameters are invalid
            FileNotFoundError: If source path doesn't exist
        """
        # Validate source exists
        if not source_path.exists():
            raise FileNotFoundError(f"Source path does not exist: {source_path}")

        if not source_path.is_dir():
            raise ValueError(f"Source path is not a directory: {source_path}")

        # Create destination if it doesn't exist
        destination_path.mkdir(parents=True, exist_ok=True)

        # Build and return plan
        return DuplicationPlan(
            source_path=source_path,
            destination_path=destination_path,
            base_name=base_name,
            count=count,
            start_number=start_number,
            padding=padding,
        )


class DuplicationService:
    """Executes folder duplication operations with pause/resume/cancel support.

    This service runs operations in a background thread and publishes progress
    events via EventBus.
    """

    def __init__(self, event_bus: Optional[EventBus] = None) -> None:
        """Initialize the duplication service.

        Args:
            event_bus: EventBus for publishing progress events
        """
        self.logger = logging.getLogger(__name__)
        self.event_bus = event_bus or EventBus.default()

        # Threading controls
        self._worker_thread: Optional[threading.Thread] = None
        self._pause_event = threading.Event()
        self._cancel_event = threading.Event()
        self._pause_event.set()  # Start unpaused

        # Current execution state
        self._current_plan: Optional[DuplicationPlan] = None
        self._is_running = False

    @property
    def is_running(self) -> bool:
        """Check if service is currently executing."""
        return self._is_running

    @property
    def is_paused(self) -> bool:
        """Check if service is currently paused."""
        return not self._pause_event.is_set()

    def execute_plan(self, plan: DuplicationPlan) -> None:
        """Execute a duplication plan in a background thread.

        Args:
            plan: The duplication plan to execute

        Raises:
            RuntimeError: If service is already running
        """
        if self._is_running:
            raise RuntimeError("Service is already executing a plan")

        self._current_plan = plan
        self._is_running = True
        self._cancel_event.clear()
        self._pause_event.set()

        # Start worker thread
        self._worker_thread = threading.Thread(
            target=self._execute_plan_worker,
            args=(plan,),
            daemon=True
        )
        self._worker_thread.start()

    def pause(self) -> None:
        """Pause the current execution."""
        if self._is_running:
            self._pause_event.clear()
            self.logger.info("Execution paused")

    def resume(self) -> None:
        """Resume the paused execution."""
        if self._is_running:
            self._pause_event.set()
            self.logger.info("Execution resumed")

    def cancel(self) -> None:
        """Cancel the current execution."""
        if self._is_running:
            self._cancel_event.set()
            self._pause_event.set()  # Unpause to allow cancellation to proceed
            self.logger.info("Execution cancelled")

    def wait_for_completion(self, timeout: Optional[float] = None) -> bool:
        """Wait for current execution to complete.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if execution completed, False if timeout occurred
        """
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout)
            return not self._worker_thread.is_alive()
        return True

    def _execute_plan_worker(self, plan: DuplicationPlan) -> None:
        """Worker thread function that executes the plan.

        Args:
            plan: The duplication plan to execute
        """
        successful = 0
        failed = 0
        cancelled = False

        try:
            for idx, operation in enumerate(plan.operations, start=1):
                # Check for cancellation
                if self._cancel_event.is_set():
                    operation.status = OperationStatus.CANCELLED
                    cancelled = True
                    self.logger.info(f"Operation cancelled: {operation.folder_name}")
                    break

                # Wait if paused
                self._pause_event.wait()

                # Execute operation
                result = self._execute_operation(operation)

                # Update counters
                if result.success:
                    successful += 1
                else:
                    failed += 1

                # Publish progress
                progress = ProgressEvent(
                    current=idx,
                    total=plan.total_operations,
                    percentage=plan.progress_percentage,
                    message=f"Processed {operation.folder_name}"
                )
                self.event_bus.publish(progress)

        except Exception as e:
            self.logger.error(f"Unexpected error in worker thread: {e}", exc_info=True)
        finally:
            # Publish completion event
            completion = ExecutionCompletedEvent(
                total_operations=plan.total_operations,
                successful=successful,
                failed=failed,
                cancelled=cancelled
            )
            self.event_bus.publish(completion)

            self._is_running = False
            self._current_plan = None

    def _execute_operation(self, operation: DuplicationOperation) -> OperationResult:
        """Execute a single duplication operation.

        Args:
            operation: The operation to execute

        Returns:
            OperationResult with execution details
        """
        start_time = time.time()

        # Publish operation started event
        self.event_bus.publish(OperationStartedEvent(operation=operation))

        operation.status = OperationStatus.IN_PROGRESS

        try:
            # Perform the actual folder copy
            dest_path = operation.full_destination_path

            if dest_path.exists():
                error_msg = f"Destination already exists: {dest_path}"
                self.logger.warning(error_msg)
                operation.status = OperationStatus.SKIPPED
                operation.error_message = error_msg

                result = OperationResult(
                    operation=operation,
                    success=False,
                    error_message=error_msg,
                    duration_seconds=time.time() - start_time
                )
                self.event_bus.publish(OperationFailedEvent(result=result))
                return result

            # Copy the folder
            shutil.copytree(operation.source_path, dest_path)

            operation.status = OperationStatus.COMPLETED
            duration = time.time() - start_time

            result = OperationResult(
                operation=operation,
                success=True,
                duration_seconds=duration
            )

            self.logger.info(
                f"Completed: {operation.folder_name} in {duration:.2f}s"
            )
            self.event_bus.publish(OperationCompletedEvent(result=result))

            return result

        except Exception as e:
            error_msg = str(e)
            operation.status = OperationStatus.FAILED
            operation.error_message = error_msg

            result = OperationResult(
                operation=operation,
                success=False,
                error_message=error_msg,
                duration_seconds=time.time() - start_time
            )

            self.logger.error(f"Failed: {operation.folder_name} - {error_msg}")
            self.event_bus.publish(OperationFailedEvent(result=result))

            return result

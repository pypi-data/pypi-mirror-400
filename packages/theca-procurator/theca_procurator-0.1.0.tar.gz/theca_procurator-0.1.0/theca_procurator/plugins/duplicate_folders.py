"""
Duplicate Folders plugin for Theca Procurator.

Provides UI for sequential folder duplication with configurable naming.
"""

import logging
import tkinter as tk
from pathlib import Path
from typing import TYPE_CHECKING
from yapsy.IPlugin import IPlugin
import ttkbootstrap as ttk
from tkinter import filedialog, messagebox

from theca_procurator.services.duplication import (
    DuplicationPlanBuilder,
    DuplicationService,
)
from theca_procurator.services.events import (
    ExecutionCompletedEvent,
    ProgressEvent,
)

if TYPE_CHECKING:
    from theca_procurator.main import ProgramReceiver


class DuplicateFoldersPlugin(IPlugin):
    """Plugin for duplicating folders with sequential naming."""

    def __init__(self) -> None:
        """Initialize the plugin."""
        super().__init__()
        self.name = "Duplicate Folders"
        self.logger = logging.getLogger(__name__)
        self.program_receiver: 'ProgramReceiver | None' = None
        self.tab_frame: 'ttk.Frame | None' = None
        self.duplication_service: 'DuplicationService | None' = None

        # UI control references
        self.start_button: 'ttk.Button | None' = None
        self.pause_button: 'ttk.Button | None' = None
        self.cancel_button: 'ttk.Button | None' = None
        self.progress_bar: 'ttk.Progressbar | None' = None
        self.progress_label: 'ttk.Label | None' = None
        self._event_subscriptions = []

    def get_ready(self, program_receiver: 'ProgramReceiver') -> None:
        """Prepare plugin during initialization.

        Args:
            program_receiver: Interface to access program components
        """
        self.program_receiver = program_receiver
        self.logger.debug("DuplicateFoldersPlugin get_ready called")

    def activate(self) -> None:
        """Activate the plugin and create UI."""
        super().activate()
        self.logger.info("Activating Duplicate Folders plugin")

        if not self.program_receiver or not self.program_receiver.main_gui:
            self.logger.error("Cannot activate: main_gui not available")
            return

        # Create tab in notebook
        main_gui = self.program_receiver.main_gui
        self.tab_frame = ttk.Frame(main_gui.notebook)
        main_gui.notebook.add(self.tab_frame, text="Duplicate Folders")

        # Build UI
        self._build_ui()

        # Subscribe to events
        self._subscribe_to_events()

    def _build_ui(self) -> None:
        """Build the plugin UI."""
        # Create a canvas with scrollbar for the tab content
        canvas = tk.Canvas(self.tab_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        # Configure the scrollable frame
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Create the window in the canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_width())
        
        # Configure canvas to update window width when canvas is resized
        def on_canvas_configure(event):
            canvas.itemconfig(canvas.find_withtag("all")[0], width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)
        
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack the scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Input section
        input_frame = ttk.LabelFrame(scrollable_frame, text="Configuration", padding=10)
        input_frame.pack(fill='x', padx=10, pady=10)

        # Source folder
        ttk.Label(input_frame, text="Source Folder:").grid(row=0, column=0, sticky='w', pady=5)
        self.source_var = ttk.StringVar()
        source_entry = ttk.Entry(input_frame, textvariable=self.source_var, width=50)
        source_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        ttk.Button(
            input_frame,
            text="Browse...",
            command=self._browse_source,
            bootstyle="secondary"
        ).grid(row=0, column=2, padx=5, pady=5)

        # Destination folder
        ttk.Label(input_frame, text="Destination Folder:").grid(row=1, column=0, sticky='w', pady=5)
        self.dest_var = ttk.StringVar()
        dest_entry = ttk.Entry(input_frame, textvariable=self.dest_var, width=50)
        dest_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        ttk.Button(
            input_frame,
            text="Browse...",
            command=self._browse_destination,
            bootstyle="secondary"
        ).grid(row=1, column=2, padx=5, pady=5)

        # Base name
        ttk.Label(input_frame, text="Base Name:").grid(row=2, column=0, sticky='w', pady=5)
        self.basename_var = ttk.StringVar(value="Episode ")
        ttk.Entry(input_frame, textvariable=self.basename_var, width=30).grid(
            row=2, column=1, sticky='w', padx=5, pady=5
        )

        # Parameters frame
        params_frame = ttk.Frame(input_frame)
        params_frame.grid(row=3, column=0, columnspan=3, sticky='ew', pady=10)

        # Count
        ttk.Label(params_frame, text="Count:").grid(row=0, column=0, sticky='w', padx=5)
        self.count_var = ttk.IntVar(value=5)
        ttk.Spinbox(
            params_frame,
            from_=1,
            to=999,
            textvariable=self.count_var,
            width=10
        ).grid(row=0, column=1, sticky='w', padx=5)

        # Start number
        ttk.Label(params_frame, text="Start Number:").grid(row=0, column=2, sticky='w', padx=5)
        self.start_var = ttk.IntVar(value=1)
        ttk.Spinbox(
            params_frame,
            from_=0,
            to=999,
            textvariable=self.start_var,
            width=10
        ).grid(row=0, column=3, sticky='w', padx=5)

        # Padding
        ttk.Label(params_frame, text="Padding:").grid(row=0, column=4, sticky='w', padx=5)
        self.padding_var = ttk.IntVar(value=3)
        ttk.Spinbox(
            params_frame,
            from_=1,
            to=5,
            textvariable=self.padding_var,
            width=10
        ).grid(row=0, column=5, sticky='w', padx=5)

        input_frame.columnconfigure(1, weight=1)

        # Control buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(
            button_frame,
            text="Generate Preview",
            command=self._generate_preview,
            bootstyle="info"
        ).pack(side='left', padx=5)

        self.start_button = ttk.Button(
            button_frame,
            text="Start",
            command=self._start_operation,
            bootstyle="success"
        )
        self.start_button.pack(side='left', padx=5)

        self.pause_button = ttk.Button(
            button_frame,
            text="Pause",
            command=self._pause_operation,
            bootstyle="warning",
            state='disabled'
        )
        self.pause_button.pack(side='left', padx=5)

        self.cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel_operation,
            bootstyle="danger",
            state='disabled'
        )
        self.cancel_button.pack(side='left', padx=5)

        # Preview section (placeholder for Tabula Mutabilis table)
        preview_frame = ttk.LabelFrame(scrollable_frame, text="Preview", padding=10)
        preview_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # TODO: Add Tabula Mutabilis table here
        self.preview_text = ttk.Text(preview_frame, height=10, width=80)
        self.preview_text.pack(fill='both', expand=True)
        self.preview_text.insert('1.0', "Preview table will appear here...")
        self.preview_text.configure(state='disabled')

        # Progress section
        progress_frame = ttk.LabelFrame(scrollable_frame, text="Progress", padding=10)
        progress_frame.pack(fill='x', padx=10, pady=10)

        # Progress label
        self.progress_label = ttk.Label(
            progress_frame,
            text="Ready",
            font=('TkDefaultFont', 9)
        )
        self.progress_label.pack(fill='x', pady=(0, 5))

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            bootstyle="success-striped",
            length=400
        )
        self.progress_bar.pack(fill='x', pady=(0, 5))
        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = 100

    def _browse_source(self) -> None:
        """Browse for source folder."""
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_var.set(folder)
            # Auto-set destination to parent if empty
            if not self.dest_var.get():
                from pathlib import Path
                self.dest_var.set(str(Path(folder).parent))

    def _browse_destination(self) -> None:
        """Browse for destination folder."""
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.dest_var.set(folder)

    def _generate_preview(self) -> None:
        """Generate preview of planned operations."""
        self.logger.info("Generate preview requested")
        # TODO: Implement preview generation
        self.preview_text.configure(state='normal')
        self.preview_text.delete('1.0', 'end')

        base = self.basename_var.get()
        start = self.start_var.get()
        count = self.count_var.get()
        padding = self.padding_var.get()

        preview_lines = []
        for i in range(count):
            num = start + i
            folder_name = f"{base}{str(num).zfill(padding)}"
            preview_lines.append(folder_name)

        self.preview_text.insert('1.0', '\n'.join(preview_lines))
        self.preview_text.configure(state='disabled')

    def _start_operation(self) -> bool:
        """Start the duplication operation.

        Returns:
            True if operation started successfully, False otherwise
        """
        self.logger.info("Start operation requested")

        # Validate inputs
        source = self.source_var.get().strip()
        dest = self.dest_var.get().strip()

        if not source:
            self.logger.warning("Start operation failed: No source folder selected")
            messagebox.showerror(
                "Validation Error",
                "Please select a source folder."
            )
            return False

        if not dest:
            self.logger.warning("Start operation failed: No destination folder selected")
            messagebox.showerror(
                "Validation Error",
                "Please select a destination folder."
            )
            return False

        source_path = Path(source)
        dest_path = Path(dest)

        # Validate source exists
        if not source_path.exists():
            self.logger.error(f"Start operation failed: Source path does not exist: {source_path}")
            messagebox.showerror(
                "Validation Error",
                f"Source folder does not exist:\n{source_path}"
            )
            return False

        if not source_path.is_dir():
            self.logger.error(
                f"Start operation failed: Source path is not a directory: {source_path}")
            messagebox.showerror(
                "Validation Error",
                f"Source path is not a directory:\n{source_path}"
            )
            return False

        # Get parameters
        base_name = self.basename_var.get()
        count = self.count_var.get()
        start_num = self.start_var.get()
        padding = self.padding_var.get()

        self.logger.info(f"Creating duplication plan: source={source_path}, dest={dest_path}, "
                         f"base={base_name}, count={count}, start={start_num}, padding={padding}")

        try:
            # Build duplication plan
            plan = DuplicationPlanBuilder.build_plan(
                source_path=source_path,
                destination_path=dest_path,
                base_name=base_name,
                count=count,
                start_number=start_num,
                padding=padding,
            )

            self.logger.info(f"Duplication plan created with {plan.total_operations} operations")

            # Initialize service if not already done
            if not self.duplication_service:
                if self.program_receiver and self.program_receiver.program:
                    event_bus = self.program_receiver.program.event_bus
                    self.duplication_service = DuplicationService(event_bus=event_bus)
                    self.logger.info("Duplication service initialized")
                else:
                    self.logger.warning("No event bus available, creating service without it")
                    self.duplication_service = DuplicationService()

            # Execute the plan
            self.logger.info("Starting duplication execution")
            self.duplication_service.execute_plan(plan)

            # Reset progress bar
            if self.progress_bar:
                self.progress_bar['value'] = 0
            if self.progress_label:
                self.progress_label.config(text="Starting duplication...")

            # Update UI state
            self._set_operation_running(True)

            self.logger.info("Duplication operation started successfully")
            return True

        except FileNotFoundError as e:
            self.logger.error(f"Start operation failed: {e}")
            messagebox.showerror(
                "File Error",
                str(e)
            )
            return False
        except ValueError as e:
            self.logger.error(f"Start operation failed: {e}")
            messagebox.showerror(
                "Validation Error",
                str(e)
            )
            return False
        except RuntimeError as e:
            self.logger.error(f"Start operation failed: {e}")
            messagebox.showerror(
                "Operation Error",
                str(e)
            )
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error starting operation: {e}", exc_info=True)
            messagebox.showerror(
                "Unexpected Error",
                f"An unexpected error occurred:\n{str(e)}"
            )
            return False

    def _pause_operation(self) -> None:
        """Pause the current operation."""
        self.logger.info("Pause operation requested")

        if self.duplication_service and self.duplication_service.is_running:
            if self.duplication_service.is_paused:
                self.logger.info("Resuming operation")
                self.duplication_service.resume()
                if self.pause_button:
                    self.pause_button.configure(text="Pause")
            else:
                self.logger.info("Pausing operation")
                self.duplication_service.pause()
                if self.pause_button:
                    self.pause_button.configure(text="Resume")
        else:
            self.logger.warning("Pause requested but no operation is running")

    def _cancel_operation(self) -> None:
        """Cancel the current operation."""
        self.logger.info("Cancel operation requested")

        if self.duplication_service and self.duplication_service.is_running:
            self.logger.info("Cancelling operation")
            self.duplication_service.cancel()
            self._set_operation_running(False)
        else:
            self.logger.warning("Cancel requested but no operation is running")

    def _set_operation_running(self, running: bool) -> None:
        """Update UI state based on operation status.

        Args:
            running: True if operation is running, False otherwise
        """
        if self.start_button:
            self.start_button.configure(state='disabled' if running else 'normal')
        if self.pause_button:
            self.pause_button.configure(state='normal' if running else 'disabled')
        if self.cancel_button:
            self.cancel_button.configure(state='normal' if running else 'disabled')

        self.logger.debug(f"UI state updated: operation_running={running}")

    def _subscribe_to_events(self) -> None:
        """Subscribe to duplication service events."""
        if not self.program_receiver or not self.program_receiver.program:
            self.logger.warning("Cannot subscribe to events: program not available")
            return

        event_bus = self.program_receiver.program.event_bus

        # Subscribe to execution completed event
        completion_sub = event_bus.subscribe(
            ExecutionCompletedEvent,
            self._on_execution_completed
        )
        self._event_subscriptions.append(completion_sub)

        # Subscribe to progress events for status bar updates
        progress_sub = event_bus.subscribe(
            ProgressEvent,
            self._on_progress_update
        )
        self._event_subscriptions.append(progress_sub)

        self.logger.info("Subscribed to duplication service events")

    def _on_execution_completed(self, event: ExecutionCompletedEvent) -> None:
        """Handle execution completion event.

        Args:
            event: The execution completed event
        """
        self.logger.info(f"Execution completed: {event.successful} successful, "
                         f"{event.failed} failed, cancelled={event.cancelled}")

        # Reset button states
        self._set_operation_running(False)

        # Reset progress bar
        if self.progress_bar:
            self.progress_bar['value'] = 0
        if self.progress_label:
            if event.cancelled:
                self.progress_label.config(text=f"Cancelled at {event.successful}/{event.total}")
            elif event.failed > 0:
                self.progress_label.config(
                    text=f"Completed with errors: {event.successful} success, {event.failed} failed")
            else:
                self.progress_label.config(text=f"Completed: {event.successful} folders created")

        # Update status bar
        if self.program_receiver and self.program_receiver.main_gui:
            if event.cancelled:
                status_msg = f"Operation cancelled. Completed: {event.successful}/{event.total_operations}"
            elif event.failed > 0:
                status_msg = f"Operation finished with errors. Success: {event.successful}, Failed: {event.failed}"
            else:
                status_msg = f"Operation completed successfully! Created {event.successful} folders."

            self.program_receiver.main_gui.update_status(status_msg)
            self.logger.info(f"Status bar updated: {status_msg}")

        # Show completion message box
        if event.cancelled:
            messagebox.showinfo(
                "Operation Cancelled",
                f"Duplication cancelled.\n\nCompleted: {event.successful}/{event.total_operations}"
            )
        elif event.failed > 0:
            messagebox.showwarning(
                "Operation Completed with Errors",
                f"Duplication finished with some errors.\n\n"
                f"Successful: {event.successful}\n"
                f"Failed: {event.failed}\n"
                f"Total: {event.total_operations}"
            )
        else:
            messagebox.showinfo(
                "Operation Completed",
                f"Duplication completed successfully!\n\n"
                f"Created {event.successful} folders."
            )

    def _on_progress_update(self, event: ProgressEvent) -> None:
        """Handle progress update event.

        Args:
            event: The progress event
        """
        # Update progress bar
        if self.progress_bar:
            self.progress_bar['value'] = event.percentage

        # Update progress label
        if self.progress_label:
            self.progress_label.config(
                text=f"{event.current}/{event.total} folders ({event.percentage:.1f}%) - {event.message}"
            )

        # Update status bar with progress
        if self.program_receiver and self.program_receiver.main_gui:
            status_msg = f"Duplicating: {event.current}/{event.total} ({event.percentage:.1f}%) - {event.message}"
            self.program_receiver.main_gui.update_status(status_msg)
            self.logger.debug(f"Progress: {event.current}/{event.total}")

    def deactivate(self) -> None:
        """Deactivate the plugin."""
        super().deactivate()
        self.logger.info("Deactivating Duplicate Folders plugin")

        # Unsubscribe from events
        if self.program_receiver and self.program_receiver.program:
            event_bus = self.program_receiver.program.event_bus
            for subscription in self._event_subscriptions:
                event_bus.unsubscribe(subscription)
            self._event_subscriptions.clear()
            self.logger.info("Unsubscribed from duplication service events")

        # Cancel any running operation
        if self.duplication_service and self.duplication_service.is_running:
            self.logger.info("Cancelling running operation before deactivation")
            self.duplication_service.cancel()
            self.duplication_service.wait_for_completion(timeout=5.0)

        # Clean up UI
        if self.tab_frame and self.program_receiver and self.program_receiver.main_gui:
            try:
                self.program_receiver.main_gui.notebook.forget(self.tab_frame)
            except Exception as e:
                self.logger.error(f"Error removing tab: {e}")

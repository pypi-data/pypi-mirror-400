"""
Bulk Rename plugin for Theca Procurator.

Imports a text-delimited list with old and new file names, searches a target
folder tree for matching files, and renames them with preview capability.
"""

import logging
import csv
import tkinter as tk
from pathlib import Path
from typing import TYPE_CHECKING, List, Tuple, Optional
from yapsy.IPlugin import IPlugin
import ttkbootstrap as ttk
from tkinter import filedialog, messagebox
from tabula_mutabilis import TabulaMutabilis

if TYPE_CHECKING:
    from theca_procurator.main import ProgramReceiver


class BulkRenamePlugin(IPlugin):
    """Plugin for bulk renaming files based on import list."""

    def __init__(self) -> None:
        """Initialize the plugin."""
        super().__init__()
        self.name = "Bulk Rename"
        self.logger = logging.getLogger(__name__)
        self.program_receiver: 'ProgramReceiver | None' = None
        self.tab_frame: 'ttk.Frame | None' = None

        # UI control references
        self.import_file_var: 'ttk.StringVar | None' = None
        self.target_folder_var: 'ttk.StringVar | None' = None
        self.delimiter_var: 'ttk.StringVar | None' = None
        self.preview_table: 'TabulaMutabilis | None' = None
        self.search_button: 'ttk.Button | None' = None
        self.rename_button: 'ttk.Button | None' = None
        self.status_label: 'ttk.Label | None' = None

        # Data
        self.rename_mappings: List[Tuple[str, str]] = []  # (old_name, new_name)
        self.found_files: List[Tuple[Path, str]] = []  # (file_path, new_name)

    def get_ready(self, program_receiver: 'ProgramReceiver') -> None:
        """Prepare plugin during initialization.

        Args:
            program_receiver: Interface to access program components
        """
        self.program_receiver = program_receiver
        self.logger.debug("BulkRenamePlugin get_ready called")

    def activate(self) -> None:
        """Activate the plugin and create UI."""
        super().activate()
        self.logger.info("Activating Bulk Rename plugin")

        if not self.program_receiver or not self.program_receiver.main_gui:
            self.logger.error("Cannot activate: main_gui not available")
            return

        # Create tab in notebook
        main_gui = self.program_receiver.main_gui
        self.tab_frame = ttk.Frame(main_gui.notebook)
        main_gui.notebook.add(self.tab_frame, text="Bulk Rename")

        # Build UI
        self._build_ui()

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
        
        # Import section
        import_frame = ttk.LabelFrame(scrollable_frame, text="Import Settings", padding=10)
        import_frame.pack(fill='x', padx=10, pady=10)

        # Import file
        ttk.Label(import_frame, text="Import File:").grid(row=0, column=0, sticky='w', pady=5)
        self.import_file_var = ttk.StringVar()
        ttk.Entry(import_frame, textvariable=self.import_file_var, width=50).grid(
            row=0, column=1, sticky='ew', padx=5, pady=5
        )
        ttk.Button(
            import_frame,
            text="Browse...",
            command=self._browse_import_file,
            bootstyle="secondary"
        ).grid(row=0, column=2, padx=5, pady=5)

        # Delimiter
        ttk.Label(import_frame, text="Delimiter:").grid(row=1, column=0, sticky='w', pady=5)
        self.delimiter_var = ttk.StringVar(value="\\t")
        delimiter_entry = ttk.Entry(
            import_frame,
            textvariable=self.delimiter_var,
            width=20
        )
        delimiter_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        ttk.Label(
            import_frame,
            text="(e.g., \\t for tab, , for comma, | for pipe)",
            font=('TkDefaultFont', 8, 'italic')
        ).grid(row=1, column=2, sticky='w', padx=5, pady=5)

        # Target folder
        ttk.Label(import_frame, text="Target Folder:").grid(row=2, column=0, sticky='w', pady=5)
        self.target_folder_var = ttk.StringVar()
        ttk.Entry(import_frame, textvariable=self.target_folder_var, width=50).grid(
            row=2, column=1, sticky='ew', padx=5, pady=5
        )
        ttk.Button(
            import_frame,
            text="Browse...",
            command=self._browse_target_folder,
            bootstyle="secondary"
        ).grid(row=2, column=2, padx=5, pady=5)

        import_frame.columnconfigure(1, weight=1)

        # Control buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill='x', padx=10, pady=10)

        self.search_button = ttk.Button(
            button_frame,
            text="Search & Preview",
            command=self._search_and_preview,
            bootstyle="info"
        )
        self.search_button.pack(side='left', padx=5)

        self.rename_button = ttk.Button(
            button_frame,
            text="Execute Rename",
            command=self._execute_rename,
            bootstyle="success",
            state='disabled'
        )
        self.rename_button.pack(side='left', padx=5)

        # Status label
        self.status_label = ttk.Label(
            button_frame,
            text="Ready",
            font=('TkDefaultFont', 9, 'italic')
        )
        self.status_label.pack(side='left', padx=20)

        # Preview section
        preview_frame = ttk.LabelFrame(scrollable_frame, text="Preview", padding=10)
        preview_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Create Tabula Mutabilis table
        self.preview_table = TabulaMutabilis(preview_frame)
        self.preview_table.pack(fill='both', expand=True)

        # Set initial empty data with headers
        headers = ['File Path', 'Old Name', 'New Name']
        initial_data = [['Import a file and search to see preview...', '', '']]
        self.preview_table.set_data(initial_data, headers)

    def _browse_import_file(self) -> None:
        """Browse for import file."""
        file_path = filedialog.askopenfilename(
            title="Select Import File",
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv"),
                ("TSV files", "*.tsv"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.import_file_var.set(file_path)
            self.logger.info(f"Import file selected: {file_path}")

    def _browse_target_folder(self) -> None:
        """Browse for target folder."""
        folder = filedialog.askdirectory(title="Select Target Folder")
        if folder:
            self.target_folder_var.set(folder)
            self.logger.info(f"Target folder selected: {folder}")

    def _get_delimiter(self) -> str:
        """Get the actual delimiter character from user input.

        Returns:
            Delimiter character (with escape sequences processed)
        """
        delimiter = self.delimiter_var.get()
        # Process common escape sequences
        delimiter = delimiter.replace('\\t', '\t')
        delimiter = delimiter.replace('\\n', '\n')
        delimiter = delimiter.replace('\\r', '\r')
        return delimiter if delimiter else '\t'

    def _parse_import_file(self, file_path: Path) -> List[Tuple[str, str]]:
        """Parse the import file and extract rename mappings.

        Args:
            file_path: Path to import file

        Returns:
            List of (old_name, new_name) tuples

        Raises:
            ValueError: If file format is invalid
        """
        mappings = []
        delimiter = self._get_delimiter()

        self.logger.info(f"Parsing import file: {file_path} with delimiter: {repr(delimiter)}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # Handle multi-character delimiters by splitting manually
                # CSV reader only supports single-character delimiters
                if len(delimiter) == 1:
                    # Use CSV reader for single-char delimiters
                    reader = csv.reader(f, delimiter=delimiter)
                    for line_num, row in enumerate(reader, start=1):
                        if len(row) < 2:
                            self.logger.warning(f"Line {line_num}: Skipping - insufficient columns")
                            continue

                        old_name = row[0].strip()
                        new_name = row[1].strip()

                        if not old_name or not new_name:
                            self.logger.warning(f"Line {line_num}: Skipping - empty name(s)")
                            continue

                        mappings.append((old_name, new_name))
                        self.logger.debug(f"Mapping: '{old_name}' -> '{new_name}'")
                else:
                    # Handle multi-character delimiters with manual split
                    for line_num, line in enumerate(f, start=1):
                        line = line.rstrip('\n\r')
                        if not line:
                            continue

                        parts = line.split(delimiter)
                        if len(parts) < 2:
                            self.logger.warning(f"Line {line_num}: Skipping - insufficient columns")
                            continue

                        old_name = parts[0].strip()
                        new_name = parts[1].strip()

                        if not old_name or not new_name:
                            self.logger.warning(f"Line {line_num}: Skipping - empty name(s)")
                            continue

                        mappings.append((old_name, new_name))
                        self.logger.debug(f"Mapping: '{old_name}' -> '{new_name}'")

            self.logger.info(f"Parsed {len(mappings)} rename mappings")
            return mappings

        except Exception as e:
            self.logger.error(f"Error parsing import file: {e}", exc_info=True)
            raise ValueError(f"Failed to parse import file: {e}")

    def _search_folder_tree(self, target_folder: Path, old_names: List[str]) -> List[Tuple[Path, str]]:
        """Search folder tree for files matching old names.

        Args:
            target_folder: Root folder to search
            old_names: List of old file names to search for

        Returns:
            List of (file_path, old_name) tuples for found files
        """
        found = []
        old_names_set = set(old_names)

        self.logger.info(f"Searching folder tree: {target_folder}")
        self.logger.info(f"Looking for {len(old_names_set)} unique file names")

        try:
            for file_path in target_folder.rglob('*'):
                if file_path.is_file():
                    if file_path.name in old_names_set:
                        found.append((file_path, file_path.name))
                        self.logger.debug(f"Found: {file_path}")

            self.logger.info(f"Found {len(found)} matching files")
            return found

        except Exception as e:
            self.logger.error(f"Error searching folder tree: {e}", exc_info=True)
            raise

    def _search_and_preview(self) -> None:
        """Search for files and generate preview."""
        self.logger.info("Search and preview requested")

        # Validate inputs
        import_file = self.import_file_var.get().strip()
        target_folder = self.target_folder_var.get().strip()

        if not import_file:
            messagebox.showerror("Validation Error", "Please select an import file.")
            return

        if not target_folder:
            messagebox.showerror("Validation Error", "Please select a target folder.")
            return

        import_path = Path(import_file)
        target_path = Path(target_folder)

        if not import_path.exists():
            messagebox.showerror("Validation Error", f"Import file does not exist:\n{import_path}")
            return

        if not target_path.exists() or not target_path.is_dir():
            messagebox.showerror("Validation Error",
                                 f"Target folder does not exist:\n{target_path}")
            return

        try:
            # Update status
            self.status_label.config(text="Parsing import file...")
            self.tab_frame.update_idletasks()

            # Parse import file
            self.rename_mappings = self._parse_import_file(import_path)

            if not self.rename_mappings:
                messagebox.showwarning(
                    "No Mappings", "No valid rename mappings found in import file.")
                self.status_label.config(text="No mappings found")
                return

            # Update status
            self.status_label.config(text=f"Searching for {len(self.rename_mappings)} files...")
            self.tab_frame.update_idletasks()

            # Search for files
            old_names = [old for old, new in self.rename_mappings]
            found_files = self._search_folder_tree(target_path, old_names)

            # Match found files with new names
            name_to_new = {old: new for old, new in self.rename_mappings}
            self.found_files = [(path, name_to_new[old_name]) for path, old_name in found_files]

            # Generate preview
            self._generate_preview()

            # Update status
            self.status_label.config(text=f"Found {len(self.found_files)} files to rename")

            # Enable rename button if files found
            if self.found_files:
                self.rename_button.configure(state='normal')
            else:
                self.rename_button.configure(state='disabled')
                messagebox.showinfo(
                    "No Files Found",
                    f"No files matching the import list were found in:\n{target_path}"
                )

        except ValueError as e:
            messagebox.showerror("Parse Error", str(e))
            self.status_label.config(text="Parse error")
        except Exception as e:
            self.logger.error(f"Search and preview failed: {e}", exc_info=True)
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            self.status_label.config(text="Error")

    def _generate_preview(self) -> None:
        """Generate preview table of rename operations."""
        headers = ['File Path', 'Old Name', 'New Name']

        if not self.found_files:
            data = [['No files found to rename', '', '']]
            self.preview_table.set_data(data, headers)
            return

        # Build data rows and store full paths for tooltips
        data = []
        self.full_paths = {}  # Map row index to full path for tooltips

        for idx, (file_path, new_name) in enumerate(self.found_files):
            old_name = file_path.name
            path_str = str(file_path.parent)

            # Store full path for tooltip
            self.full_paths[idx] = path_str

            # Truncate path if too long
            if len(path_str) > 50:
                path_str = "..." + path_str[-47:]

            data.append([path_str, old_name, new_name])

        # Set all data at once
        self.preview_table.set_data(data, headers)

        # Set up tooltip binding for file path column
        self._setup_path_tooltips()

        self.logger.info(f"Preview generated for {len(self.found_files)} files")

    def _setup_path_tooltips(self) -> None:
        """Set up tooltips to show full file paths on hover."""
        try:
            # Get the canvas from TabulaMutabilis
            canvas = self.preview_table.view.canvas

            # Bind mouse motion to show tooltip
            canvas.bind('<Motion>', self._show_path_tooltip)
            canvas.bind('<Leave>', self._hide_path_tooltip)

            # Create tooltip label (initially hidden)
            self.tooltip_label = None

        except Exception as e:
            self.logger.warning(f"Could not set up tooltips: {e}")

    def _show_path_tooltip(self, event) -> None:
        """Show tooltip with full path when hovering over file path column."""
        try:
            canvas = self.preview_table.view.canvas

            # Find which cell is under the mouse
            x = canvas.canvasx(event.x)
            y = canvas.canvasy(event.y)

            # Get cell position from TabulaMutabilis
            col_widths = self.preview_table.view.column_widths
            row_height = 25  # Default row height
            header_height = 30

            # Calculate row and column
            if y < header_height:
                return  # In header

            row = int((y - header_height) / row_height)

            # Calculate column
            col = 0
            x_pos = 0
            for i, width in enumerate(col_widths):
                if x < x_pos + width:
                    col = i
                    break
                x_pos += width

            # Only show tooltip for file path column (column 0)
            if col == 0 and row < len(self.full_paths):
                full_path = self.full_paths.get(row, '')

                # Hide existing tooltip
                self._hide_path_tooltip(None)

                # Create new tooltip
                self.tooltip_label = ttk.Label(
                    canvas,
                    text=full_path,
                    background='#ffffe0',
                    relief='solid',
                    borderwidth=1,
                    padding=5
                )

                # Position tooltip near mouse
                tooltip_x = event.x + 10
                tooltip_y = event.y + 10

                self.tooltip_window = canvas.create_window(
                    tooltip_x, tooltip_y,
                    window=self.tooltip_label,
                    anchor='nw'
                )
            else:
                self._hide_path_tooltip(None)

        except Exception as e:
            self.logger.debug(f"Tooltip error: {e}")

    def _hide_path_tooltip(self, event) -> None:
        """Hide the tooltip."""
        try:
            if hasattr(self, 'tooltip_label') and self.tooltip_label:
                self.tooltip_label.destroy()
                self.tooltip_label = None
            if hasattr(self, 'tooltip_window'):
                delattr(self, 'tooltip_window')
        except Exception:
            pass

    def _execute_rename(self) -> None:
        """Execute the rename operations."""
        self.logger.info("Execute rename requested")

        if not self.found_files:
            messagebox.showwarning("No Files", "No files to rename.")
            return

        # Confirmation dialog
        result = messagebox.askyesno(
            "Confirm Rename",
            f"Are you sure you want to rename {len(self.found_files)} files?\n\n"
            "This operation cannot be undone."
        )

        if not result:
            self.logger.info("Rename cancelled by user")
            return

        # Execute renames
        success_count = 0
        error_count = 0
        errors = []

        self.status_label.config(text="Renaming files...")
        self.tab_frame.update_idletasks()

        for file_path, new_name in self.found_files:
            try:
                new_path = file_path.parent / new_name

                # Check if target already exists
                if new_path.exists():
                    error_msg = f"Target already exists: {new_path}"
                    self.logger.warning(error_msg)
                    errors.append(error_msg)
                    error_count += 1
                    continue

                # Rename
                file_path.rename(new_path)
                success_count += 1
                self.logger.info(f"Renamed: {file_path.name} -> {new_name}")

            except Exception as e:
                error_msg = f"Failed to rename {file_path.name}: {str(e)}"
                self.logger.error(error_msg)
                errors.append(error_msg)
                error_count += 1

        # Update status
        self.status_label.config(text=f"Completed: {success_count} success, {error_count} errors")

        # Show results
        if error_count > 0:
            error_summary = "\n".join(errors[:10])  # Show first 10 errors
            if len(errors) > 10:
                error_summary += f"\n... and {len(errors) - 10} more errors"

            messagebox.showwarning(
                "Rename Completed with Errors",
                f"Renamed {success_count} files successfully.\n"
                f"{error_count} files failed.\n\n"
                f"Errors:\n{error_summary}"
            )
        else:
            messagebox.showinfo(
                "Rename Completed",
                f"Successfully renamed {success_count} files!"
            )

        # Clear found files and disable rename button
        self.found_files = []
        self.rename_button.configure(state='disabled')

        # Clear preview
        headers = ['File Path', 'Old Name', 'New Name']
        data = [['Rename completed. Search again to see updated results.', '', '']]
        self.preview_table.set_data(data, headers)

    def deactivate(self) -> None:
        """Deactivate the plugin."""
        super().deactivate()
        self.logger.info("Deactivating Bulk Rename plugin")

        # Clean up UI
        if self.tab_frame and self.program_receiver and self.program_receiver.main_gui:
            try:
                self.program_receiver.main_gui.notebook.forget(self.tab_frame)
            except Exception as e:
                self.logger.error(f"Error removing tab: {e}")

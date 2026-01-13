"""
Regex Rename plugin for Theca Procurator.

Advanced file renaming with regex find-replace, prefix/suffix with sequential numbering.
"""

import logging
import re
import toml
import tkinter as tk
from pathlib import Path
from typing import TYPE_CHECKING, List, Tuple, Optional, Dict, Any
from yapsy.IPlugin import IPlugin
import ttkbootstrap as ttk
from tkinter import filedialog, messagebox
from tabula_mutabilis import TabulaMutabilis

if TYPE_CHECKING:
    from theca_procurator.main import ProgramReceiver


class RegexRenamePlugin(IPlugin):
    """Plugin for advanced regex-based file renaming with prefix/suffix sequencing."""

    def __init__(self) -> None:
        """Initialize the plugin."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.tab_frame: Optional[ttk.Frame] = None
        self.receiver: Optional['ProgramReceiver'] = None
        self.found_files: List[Tuple[Path, str]] = []
        self.full_paths: Dict[int, str] = {}
        # These are initialized in _build_ui() during activate()
        self.preview_table: Any = None
        self.status_label: Any = None
        self.rename_button: Any = None
        self.progress_bar: Any = None
        self.progress_label: Any = None

    def get_ready(self, program_receiver: 'ProgramReceiver') -> None:
        """Prepare plugin during initialization.

        Args:
            program_receiver: Interface to access program components
        """
        self.receiver = program_receiver
        self.logger.info("Regex Rename plugin ready")

    def activate(self) -> None:
        """Activate the plugin and create UI."""
        super().activate()
        self.logger.info("Activating Regex Rename plugin")

        if not self.receiver or not self.receiver.main_gui:
            self.logger.error("Cannot activate: main_gui not available")
            return

        # Create tab in notebook
        main_gui = self.receiver.main_gui
        self.tab_frame = ttk.Frame(main_gui.notebook)
        main_gui.notebook.add(self.tab_frame, text="Regex Rename")

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

        # Use scrollable_frame as the parent for all controls
        main_frame = ttk.Frame(scrollable_frame, padding=10)
        main_frame.pack(fill='both', expand=True)

        # Target Folder Section
        folder_frame = ttk.LabelFrame(main_frame, text="Target Folder", padding=10)
        folder_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(folder_frame, text="Folder:").grid(row=0, column=0, sticky='w', pady=5)
        self.target_folder_var = ttk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.target_folder_var, width=60).grid(
            row=0, column=1, sticky='ew', padx=5, pady=5
        )
        ttk.Button(
            folder_frame,
            text="Browse...",
            command=self._browse_target_folder,
            bootstyle="secondary"
        ).grid(row=0, column=2, padx=5, pady=5)

        folder_frame.columnconfigure(1, weight=1)

        # Rename Configuration Section
        config_frame = ttk.LabelFrame(main_frame, text="Rename Configuration", padding=10)
        config_frame.pack(fill='x', pady=(0, 10))

        # Prefix Configuration
        ttk.Label(config_frame, text="Prefix:", font=('TkDefaultFont', 9, 'bold')).grid(
            row=0, column=0, sticky='w', pady=5
        )

        ttk.Label(config_frame, text="Type:").grid(row=1, column=0, sticky='w', padx=(20, 5))
        self.prefix_type_var = ttk.StringVar(value="literal")
        prefix_type_frame = ttk.Frame(config_frame)
        prefix_type_frame.grid(row=1, column=1, sticky='w', pady=2)
        ttk.Radiobutton(
            prefix_type_frame, text="None", variable=self.prefix_type_var,
            value="none", command=self._update_prefix_state
        ).pack(side='left', padx=5)
        ttk.Radiobutton(
            prefix_type_frame, text="Literal", variable=self.prefix_type_var,
            value="literal", command=self._update_prefix_state
        ).pack(side='left', padx=5)
        ttk.Radiobutton(
            prefix_type_frame, text="Sequential Number", variable=self.prefix_type_var,
            value="sequential", command=self._update_prefix_state
        ).pack(side='left', padx=5)

        ttk.Label(config_frame, text="Value:").grid(row=2, column=0, sticky='w', padx=(20, 5))
        self.prefix_value_var = ttk.StringVar()
        self.prefix_value_entry = ttk.Entry(
            config_frame, textvariable=self.prefix_value_var, width=30)
        self.prefix_value_entry.grid(row=2, column=1, sticky='w', pady=2)

        # Sequential number options for prefix
        seq_prefix_frame = ttk.Frame(config_frame)
        seq_prefix_frame.grid(row=3, column=1, sticky='w', pady=2)

        ttk.Label(seq_prefix_frame, text="Start:").pack(side='left', padx=(0, 2))
        self.prefix_start_var = ttk.StringVar(value="1")
        self.prefix_start_entry = ttk.Entry(
            seq_prefix_frame, textvariable=self.prefix_start_var, width=8)
        self.prefix_start_entry.pack(side='left', padx=2)

        ttk.Label(seq_prefix_frame, text="Increment:").pack(side='left', padx=(10, 2))
        self.prefix_increment_var = ttk.StringVar(value="1")
        self.prefix_increment_entry = ttk.Entry(
            seq_prefix_frame, textvariable=self.prefix_increment_var, width=8)
        self.prefix_increment_entry.pack(side='left', padx=2)

        ttk.Label(seq_prefix_frame, text="Padding:").pack(side='left', padx=(10, 2))
        self.prefix_padding_var = ttk.StringVar(value="0")
        self.prefix_padding_entry = ttk.Entry(
            seq_prefix_frame, textvariable=self.prefix_padding_var, width=8)
        self.prefix_padding_entry.pack(side='left', padx=2)

        # Separator
        ttk.Label(config_frame, text="Separator:", font=('TkDefaultFont', 9, 'bold')).grid(
            row=4, column=0, sticky='w', pady=(10, 5)
        )
        ttk.Label(config_frame, text="Value:").grid(row=5, column=0, sticky='w', padx=(20, 5))
        self.separator_var = ttk.StringVar(value="_")
        ttk.Entry(config_frame, textvariable=self.separator_var, width=20).grid(
            row=5, column=1, sticky='w', pady=2
        )

        # File Filter Regex
        ttk.Label(config_frame, text="File Filter:", font=('TkDefaultFont', 9, 'bold')).grid(
            row=6, column=0, sticky='w', pady=(10, 5)
        )
        ttk.Label(config_frame, text="Match (regex):").grid(
            row=7, column=0, sticky='w', padx=(20, 5))
        self.filter_regex_var = ttk.StringVar()
        ttk.Entry(config_frame, textvariable=self.filter_regex_var, width=50).grid(
            row=7, column=1, sticky='ew', pady=2
        )
        ttk.Label(config_frame, text="(Leave empty to match all files)",
                  font=('TkDefaultFont', 8, 'italic')).grid(
            row=8, column=1, sticky='w', pady=(0, 5)
        )

        # Regex Find/Replace
        ttk.Label(config_frame, text="Filename Replacement:", font=('TkDefaultFont', 9, 'bold')).grid(
            row=9, column=0, sticky='w', pady=(10, 5)
        )
        ttk.Label(config_frame, text="Find (regex):").grid(
            row=10, column=0, sticky='w', padx=(20, 5))
        self.regex_find_var = ttk.StringVar()
        ttk.Entry(config_frame, textvariable=self.regex_find_var, width=50).grid(
            row=10, column=1, sticky='ew', pady=2
        )

        ttk.Label(config_frame, text="Replace With:").grid(
            row=11, column=0, sticky='w', padx=(20, 5))
        self.regex_replace_var = ttk.StringVar()
        ttk.Entry(config_frame, textvariable=self.regex_replace_var, width=50).grid(
            row=11, column=1, sticky='ew', pady=2
        )

        # Suffix Configuration
        ttk.Label(config_frame, text="Suffix:", font=('TkDefaultFont', 9, 'bold')).grid(
            row=12, column=0, sticky='w', pady=(10, 5)
        )

        ttk.Label(config_frame, text="Type:").grid(row=13, column=0, sticky='w', padx=(20, 5))
        self.suffix_type_var = ttk.StringVar(value="literal")
        suffix_type_frame = ttk.Frame(config_frame)
        suffix_type_frame.grid(row=13, column=1, sticky='w', pady=2)
        ttk.Radiobutton(
            suffix_type_frame, text="None", variable=self.suffix_type_var,
            value="none", command=self._update_suffix_state
        ).pack(side='left', padx=5)
        ttk.Radiobutton(
            suffix_type_frame, text="Literal", variable=self.suffix_type_var,
            value="literal", command=self._update_suffix_state
        ).pack(side='left', padx=5)
        ttk.Radiobutton(
            suffix_type_frame, text="Sequential Number", variable=self.suffix_type_var,
            value="sequential", command=self._update_suffix_state
        ).pack(side='left', padx=5)

        ttk.Label(config_frame, text="Value:").grid(row=14, column=0, sticky='w', padx=(20, 5))
        self.suffix_value_var = ttk.StringVar()
        self.suffix_value_entry = ttk.Entry(
            config_frame, textvariable=self.suffix_value_var, width=30)
        self.suffix_value_entry.grid(row=14, column=1, sticky='w', pady=2)

        # Sequential number options for suffix
        seq_suffix_frame = ttk.Frame(config_frame)
        seq_suffix_frame.grid(row=15, column=1, sticky='w', pady=2)

        ttk.Label(seq_suffix_frame, text="Start:").pack(side='left', padx=(0, 2))
        self.suffix_start_var = ttk.StringVar(value="1")
        self.suffix_start_entry = ttk.Entry(
            seq_suffix_frame, textvariable=self.suffix_start_var, width=8)
        self.suffix_start_entry.pack(side='left', padx=2)

        ttk.Label(seq_suffix_frame, text="Increment:").pack(side='left', padx=(10, 2))
        self.suffix_increment_var = ttk.StringVar(value="1")
        self.suffix_increment_entry = ttk.Entry(
            seq_suffix_frame, textvariable=self.suffix_increment_var, width=8)
        self.suffix_increment_entry.pack(side='left', padx=2)

        ttk.Label(seq_suffix_frame, text="Padding:").pack(side='left', padx=(10, 2))
        self.suffix_padding_var = ttk.StringVar(value="0")
        self.suffix_padding_entry = ttk.Entry(
            seq_suffix_frame, textvariable=self.suffix_padding_var, width=8)
        self.suffix_padding_entry.pack(side='left', padx=2)

        config_frame.columnconfigure(1, weight=1)

        # Action Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(
            button_frame,
            text="Search & Preview",
            command=self._search_and_preview,
            bootstyle="primary"
        ).pack(side='left', padx=5)

        self.rename_button = ttk.Button(
            button_frame,
            text="Execute Rename",
            command=self._execute_rename,
            bootstyle="success",
            state='disabled'
        )
        self.rename_button.pack(side='left', padx=5)

        ttk.Button(
            button_frame,
            text="Save Settings",
            command=self._save_settings,
            bootstyle="info"
        ).pack(side='left', padx=5)

        ttk.Button(
            button_frame,
            text="Load Settings",
            command=self._load_settings,
            bootstyle="info"
        ).pack(side='left', padx=5)

        # Status Label
        self.status_label = ttk.Label(button_frame, text="Ready", foreground='gray')
        self.status_label.pack(side='left', padx=20)

        # Progress Bar
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill='x', pady=5)

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            bootstyle="info"
        )
        self.progress_bar.pack(fill='x', padx=10)

        self.progress_label = ttk.Label(progress_frame, text="", foreground='gray')
        self.progress_label.pack(pady=2)

        # Preview Table
        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding=10)
        preview_frame.pack(fill='both', expand=True, pady=(0, 10))

        # Selection controls frame
        selection_frame = ttk.Frame(preview_frame)
        selection_frame.pack(fill='x', pady=(0, 5))

        ttk.Button(
            selection_frame,
            text="Select All Rows",
            command=self._select_all_rows,
            bootstyle="secondary"
        ).pack(side='left', padx=5)

        ttk.Button(
            selection_frame,
            text="Clear Selection",
            command=self._clear_selection,
            bootstyle="secondary"
        ).pack(side='left', padx=5)

        self.selection_label = ttk.Label(selection_frame, text="0 rows selected", foreground='gray')
        self.selection_label.pack(side='left', padx=20)

        self.preview_table = TabulaMutabilis(preview_frame)
        self.preview_table.pack(fill='both', expand=True)

        # Track selected rows manually since TabulaMutabilis doesn't have row selection
        self.selected_rows = set()

        headers = ['File Path', 'Old Name', 'New Name']
        initial_data = [['Select a folder and click Search & Preview...', '', '']]
        self.preview_table.set_data(initial_data, headers)

        # Bind click events for row selection
        self._setup_row_selection_binding()

        # Initialize state
        self._update_prefix_state()
        self._update_suffix_state()

    def _update_prefix_state(self) -> None:
        """Update prefix input fields based on type selection."""
        prefix_type = self.prefix_type_var.get()

        if prefix_type == "none":
            self.prefix_value_entry.configure(state='disabled')
            self.prefix_start_entry.configure(state='disabled')
            self.prefix_increment_entry.configure(state='disabled')
            self.prefix_padding_entry.configure(state='disabled')
        elif prefix_type == "sequential":
            self.prefix_value_entry.configure(state='disabled')
            self.prefix_start_entry.configure(state='normal')
            self.prefix_increment_entry.configure(state='normal')
            self.prefix_padding_entry.configure(state='normal')
        else:  # literal
            self.prefix_value_entry.configure(state='normal')
            self.prefix_start_entry.configure(state='disabled')
            self.prefix_increment_entry.configure(state='disabled')
            self.prefix_padding_entry.configure(state='disabled')

    def _update_suffix_state(self) -> None:
        """Update suffix input fields based on type selection."""
        suffix_type = self.suffix_type_var.get()

        if suffix_type == "none":
            self.suffix_value_entry.configure(state='disabled')
            self.suffix_start_entry.configure(state='disabled')
            self.suffix_increment_entry.configure(state='disabled')
            self.suffix_padding_entry.configure(state='disabled')
        elif suffix_type == "sequential":
            self.suffix_value_entry.configure(state='disabled')
            self.suffix_start_entry.configure(state='normal')
            self.suffix_increment_entry.configure(state='normal')
            self.suffix_padding_entry.configure(state='normal')
        else:  # literal
            self.suffix_value_entry.configure(state='normal')
            self.suffix_start_entry.configure(state='disabled')
            self.suffix_increment_entry.configure(state='disabled')
            self.suffix_padding_entry.configure(state='disabled')

    def _browse_target_folder(self) -> None:
        """Open folder browser dialog."""
        folder = filedialog.askdirectory(title="Select Target Folder")
        if folder:
            self.target_folder_var.set(folder)
            self.logger.info(f"Target folder selected: {folder}")

    def _search_and_preview(self) -> None:
        """Search for files and generate preview."""
        self.logger.info("Search and preview requested")

        target_folder = self.target_folder_var.get()
        if not target_folder:
            messagebox.showwarning("No Folder", "Please select a target folder.")
            return

        target_path = Path(target_folder)
        if not target_path.exists():
            messagebox.showerror("Invalid Path", "Target folder does not exist.")
            return

        # Start progress bar
        self.progress_bar.start(10)
        self.progress_label.configure(text="Searching for files...")
        self.status_label.configure(text="Searching...", foreground='blue')
        if self.tab_frame:
            self.tab_frame.update()

        try:
            # Get filter regex
            filter_regex = self.filter_regex_var.get()

            # Find all files in folder tree
            self.progress_label.configure(text="Scanning directory...")
            if self.tab_frame:
                self.tab_frame.update_idletasks()

            all_files = []
            file_count = 0
            filtered_count = 0

            for f in target_path.rglob('*'):
                if f.is_file():
                    file_count += 1

                    # Apply filter regex if provided
                    if filter_regex:
                        try:
                            if re.search(filter_regex, f.name):
                                all_files.append(f)
                                filtered_count += 1
                        except re.error as e:
                            self.progress_bar.stop()
                            self.progress_label.configure(text="")
                            self.logger.error(f"Invalid filter regex: {e}")
                            messagebox.showerror(
                                "Invalid Filter Regex",
                                f"Filter regex error: {e}"
                            )
                            self.status_label.configure(text="Search failed", foreground='red')
                            return
                    else:
                        # No filter, include all files
                        all_files.append(f)
                        filtered_count += 1

                    # Update progress every 100 files to keep GUI responsive
                    if file_count % 100 == 0:
                        if filter_regex:
                            self.progress_label.configure(
                                text=f"Scanned {file_count} files, matched {filtered_count}..."
                            )
                        else:
                            self.progress_label.configure(text=f"Found {file_count} files...")
                        if self.tab_frame:
                            self.tab_frame.update_idletasks()

            if not all_files:
                self.progress_bar.stop()
                self.progress_label.configure(text="")
                if filter_regex:
                    self.status_label.configure(
                        text=f"No files matched filter (scanned {file_count} files)",
                        foreground='orange'
                    )
                else:
                    self.status_label.configure(text="No files found", foreground='orange')
                self._generate_preview()
                return

            # Update progress
            self.progress_label.configure(text=f"Generating names for {len(all_files)} files...")
            if self.tab_frame:
                self.tab_frame.update_idletasks()

            # Generate new names for all files
            self.found_files = self._generate_new_names(all_files)

            # Stop progress bar
            self.progress_bar.stop()
            self.progress_label.configure(text="")

            self.status_label.configure(
                text=f"Found {len(self.found_files)} files",
                foreground='green'
            )

            self._generate_preview()
            self.rename_button.configure(state='normal')

        except Exception as e:
            self.progress_bar.stop()
            self.progress_label.configure(text="")
            self.logger.error(f"Error during search: {e}", exc_info=True)
            messagebox.showerror("Search Error", f"Error searching files: {e}")
            self.status_label.configure(text="Search failed", foreground='red')

    def _generate_new_names(self, files: List[Path]) -> List[Tuple[Path, str]]:
        """Generate new names for files based on configuration.

        Args:
            files: List of file paths

        Returns:
            List of (file_path, new_name) tuples
        """
        results = []

        # Get configuration
        separator = self.separator_var.get()
        regex_find = self.regex_find_var.get()
        regex_replace = self.regex_replace_var.get()

        # Prefix configuration
        prefix_type = self.prefix_type_var.get()
        prefix_value = self.prefix_value_var.get()
        prefix_start = int(self.prefix_start_var.get() or 0)
        prefix_increment = int(self.prefix_increment_var.get() or 1)
        prefix_padding = int(self.prefix_padding_var.get() or 0)

        # Suffix configuration
        suffix_type = self.suffix_type_var.get()
        suffix_value = self.suffix_value_var.get()
        suffix_start = int(self.suffix_start_var.get() or 0)
        suffix_increment = int(self.suffix_increment_var.get() or 1)
        suffix_padding = int(self.suffix_padding_var.get() or 0)

        # Process each file
        prefix_counter = prefix_start
        suffix_counter = suffix_start
        total_files = len(files)

        for idx, file_path in enumerate(files):
            # Update progress every 50 files to keep GUI responsive
            if idx % 50 == 0 and self.progress_label:
                self.progress_label.configure(
                    text=f"Processing {idx}/{total_files} files..."
                )
                if self.tab_frame:
                    self.tab_frame.update_idletasks()
            # Get filename without extension
            stem = file_path.stem
            extension = file_path.suffix

            # Apply regex find/replace to main filename
            if regex_find:
                try:
                    main_name = re.sub(regex_find, regex_replace, stem)
                except re.error as e:
                    self.logger.warning(f"Regex error for {stem}: {e}")
                    main_name = stem
            else:
                main_name = stem

            # Build prefix
            if prefix_type == "none":
                prefix = ""
            elif prefix_type == "sequential":
                prefix = str(prefix_counter).zfill(prefix_padding)
                prefix_counter += prefix_increment
            else:  # literal
                prefix = prefix_value

            # Build suffix
            if suffix_type == "none":
                suffix = ""
            elif suffix_type == "sequential":
                suffix = str(suffix_counter).zfill(suffix_padding)
                suffix_counter += suffix_increment
            else:  # literal
                suffix = suffix_value

            # Construct new name
            parts = []
            if prefix:
                parts.append(prefix)
            if main_name:
                parts.append(main_name)
            if suffix:
                parts.append(suffix)

            new_name = separator.join(parts) + extension

            results.append((file_path, new_name))

        return results

    def _generate_preview(self) -> None:
        """Generate preview table of rename operations."""
        headers = ['File Path', 'Old Name', 'New Name']

        if not self.found_files:
            data = [['No files found to rename', '', '']]
            self.preview_table.set_data(data, headers)
            return

        # Build data rows and store full paths for tooltips
        data = []
        self.full_paths = {}
        max_path_len = 0
        max_old_len = 0
        max_new_len = 0

        for idx, (file_path, new_name) in enumerate(self.found_files):
            old_name = file_path.name
            path_str = str(file_path.parent)

            # Store full path for tooltip
            self.full_paths[idx] = path_str

            # Track maximum lengths for column sizing
            max_path_len = max(max_path_len, len(path_str))
            max_old_len = max(max_old_len, len(old_name))
            max_new_len = max(max_new_len, len(new_name))

            data.append([path_str, old_name, new_name])

        # Set all data at once
        self.preview_table.set_data(data, headers)

        # Auto-expand columns based on content
        # Calculate column widths (approximate: 8 pixels per character + padding)
        char_width = 8
        padding = 20
        path_width = min(max(max_path_len * char_width + padding, 100), 600)  # Min 100, max 600
        old_width = min(max(max_old_len * char_width + padding, 100), 400)  # Min 100, max 400
        new_width = min(max(max_new_len * char_width + padding, 100), 400)  # Min 100, max 400

        # Set column widths by updating base style
        self.preview_table.style_provider.base_styles['default'].col_width = old_width
        self.preview_table.style_provider.base_styles['header'].col_width = old_width

        # Set text color to white for unselected rows
        self.preview_table.style_provider.base_styles['default'].text_color = '#FFFFFF'

        # Add light gray borders between rows
        self.preview_table.style_provider.base_styles['default'].borders = {
            'bottom': (2, '#D3D3D3')  # 2px light gray bottom border
        }

        # Note: TabulaMutabilis doesn't support per-column widths yet
        # All columns will use the same width from the style
        # Refresh the table to apply new widths
        self.preview_table.refresh()

        # Set up tooltip binding for file path column
        self._setup_path_tooltips()

        # Re-bind row selection after data change
        self._setup_row_selection_binding()

        self.logger.info(f"Preview generated for {len(self.found_files)} files")

    def _setup_path_tooltips(self) -> None:
        """Set up tooltips to show full file paths on hover."""
        try:
            canvas = self.preview_table.view.canvas
            canvas.bind('<Motion>', self._show_path_tooltip)
            canvas.bind('<Leave>', self._hide_path_tooltip)
            self.tooltip_label = None
        except Exception as e:
            self.logger.warning(f"Could not set up tooltips: {e}")

    def _show_path_tooltip(self, event: Any) -> None:
        """Show tooltip with full path when hovering over file path column."""
        try:
            canvas = self.preview_table.view.canvas
            x = canvas.canvasx(event.x)
            y = canvas.canvasy(event.y)

            col_widths = self.preview_table.view.column_widths
            row_height = 25
            header_height = 30

            if y < header_height:
                return

            row = int((y - header_height) / row_height)

            col = 0
            x_pos = 0
            for i, width in enumerate(col_widths):
                if x < x_pos + width:
                    col = i
                    break
                x_pos += width

            if col == 0 and row < len(self.full_paths):
                full_path = self.full_paths.get(row, '')
                self._hide_path_tooltip(None)

                self.tooltip_label = ttk.Label(
                    canvas,
                    text=full_path,
                    background='#ffffe0',
                    relief='solid',
                    borderwidth=1,
                    padding=5
                )

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

    def _hide_path_tooltip(self, event: Any) -> None:
        """Hide the tooltip."""
        if hasattr(self, 'tooltip_label') and self.tooltip_label:
            self.tooltip_label.destroy()
            self.tooltip_label = None
        if hasattr(self, 'tooltip_window'):
            delattr(self, 'tooltip_window')

    def _setup_row_selection_binding(self) -> None:
        """Set up or refresh the row selection click binding."""
        try:
            # Store original handler if not already stored
            if not hasattr(self, '_original_click_handler'):
                self._original_click_handler = self.preview_table.controller.on_click

            # Unbind any existing binding first
            self.preview_table.canvas.unbind('<Button-1>')

            # Bind our wrapper
            self.preview_table.canvas.bind('<Button-1>', self._on_table_click_wrapper)

            # Bind to table redraw event to redraw selection after table redraws
            self.preview_table.canvas.bind('<<RedrawTable>>', self._on_table_redraw)

            self.logger.debug("Row selection binding set up")
        except Exception as e:
            self.logger.error(f"Error setting up row selection binding: {e}")

    def _on_table_click_wrapper(self, event: Any) -> None:
        """Wrapper for table click that handles both selection and original behavior."""
        self.logger.debug(f"Click wrapper called at x={event.x}, y={event.y}")

        # First, handle row selection
        self._on_table_click(event)

        # Then call original handler if it exists
        if hasattr(self, '_original_click_handler') and self._original_click_handler:
            try:
                self._original_click_handler(event)
            except Exception as e:
                self.logger.debug(f"Original click handler error: {e}")

    def _on_table_click(self, event: Any) -> None:
        """Handle table click for row selection."""
        try:
            canvas = self.preview_table.canvas
            x = canvas.canvasx(event.x)
            y = canvas.canvasy(event.y)

            self.logger.debug(
                f"Click at canvas coords: x={x}, y={y}, found_files={len(self.found_files)}")

            # Calculate which row was clicked
            row_height = 25
            header_height = 30

            if y < header_height:
                self.logger.debug("Click in header, ignoring")
                return  # Clicked on header

            row = int((y - header_height) / row_height)
            self.logger.debug(f"Calculated row: {row}")

            # Check if row is valid
            if row < 0 or row >= len(self.found_files):
                self.logger.debug(f"Invalid row {row}, ignoring")
                return

            # Toggle row selection (Ctrl for multi-select)
            if event.state & 0x0004:  # Ctrl key
                if row in self.selected_rows:
                    self.selected_rows.remove(row)
                    self.logger.debug(f"Deselected row {row}")
                else:
                    self.selected_rows.add(row)
                    self.logger.debug(f"Added row {row} to selection")
            else:
                # Single selection
                self.selected_rows = {row}
                self.logger.debug(f"Selected row {row} (single)")

            # Redraw table with selection highlighting
            self._redraw_table_selection()

            # Update selection label
            self._update_selection_label()

        except Exception as e:
            self.logger.error(f"Table click error: {e}", exc_info=True)

    def _on_table_redraw(self, event: Any = None) -> None:
        """Handle table redraw event to redraw selection highlighting."""
        # Use after_idle to ensure we draw after the table finishes
        if self.tab_frame:
            self.tab_frame.after_idle(self._redraw_table_selection)

    def _redraw_table_selection(self) -> None:
        """Redraw table to show selected rows with light blue text."""
        try:
            canvas = self.preview_table.canvas

            # Get actual row height from table view
            if hasattr(self.preview_table.view, 'row_height'):
                row_height = self.preview_table.view.row_height
            else:
                row_height = 25

            if hasattr(self.preview_table.view, 'header_height'):
                header_height = self.preview_table.view.header_height
            else:
                header_height = 30

            # Get column count and widths
            if hasattr(self.preview_table.view, 'column_widths'):
                col_widths = self.preview_table.view.column_widths
            else:
                col_widths = [200, 200, 200]  # Fallback

            # Find all text items on canvas and change color for selected rows
            all_items = canvas.find_all()

            for item_id in all_items:
                tags = canvas.gettags(item_id)

                # Look for cell text items
                for tag in tags:
                    if tag.startswith('cell_'):
                        # Parse row and column from tag like 'cell_0_1'
                        parts = tag.split('_')
                        if len(parts) == 3:
                            try:
                                row = int(parts[1])
                                col = int(parts[2])

                                # Check if this is a text item (not background rectangle)
                                item_type = canvas.type(item_id)
                                if item_type == 'text':
                                    if row in self.selected_rows:
                                        # Change text to light blue for selected rows
                                        canvas.itemconfig(item_id, fill='#4A90E2')
                                        self.logger.debug(
                                            f"Changed text color for row {row}, col {col}")
                                    else:
                                        # Reset to white for unselected rows
                                        canvas.itemconfig(item_id, fill='#FFFFFF')
                            except (ValueError, IndexError):
                                pass

        except Exception as e:
            self.logger.error(f"Selection redraw error: {e}", exc_info=True)

    def _select_all_rows(self) -> None:
        """Select all rows in the table."""
        if not self.found_files:
            return

        self.selected_rows = set(range(len(self.found_files)))
        self._redraw_table_selection()
        self._update_selection_label()
        self.logger.info(f"Selected all {len(self.found_files)} rows")

    def _clear_selection(self) -> None:
        """Clear all row selections."""
        self.selected_rows.clear()
        self._redraw_table_selection()
        self._update_selection_label()
        self.logger.info("Cleared row selection")

    def _update_selection_label(self) -> None:
        """Update the selection count label."""
        count = len(self.selected_rows)
        if count == 0:
            text = "0 rows selected"
        elif count == 1:
            text = "1 row selected"
        else:
            text = f"{count} rows selected"

        if hasattr(self, 'selection_label'):
            self.selection_label.configure(text=text)

    def _execute_rename(self) -> None:
        """Execute the rename operations."""
        self.logger.info("Execute rename requested")

        if not self.found_files:
            messagebox.showwarning("No Files", "No files to rename.")
            return

        # Get selected rows
        selected_indices = sorted(list(self.selected_rows))

        if not selected_indices:
            # Flash warning in status bar
            self._flash_status_warning(
                "No files selected! Click rows to select files for renaming.")
            return

        # Filter found_files to only selected items
        files_to_rename = [self.found_files[i]
                           for i in selected_indices if i < len(self.found_files)]

        if not files_to_rename:
            messagebox.showwarning("No Files", "No valid files selected.")
            return

        result = messagebox.askyesno(
            "Confirm Rename",
            f"Rename {len(files_to_rename)} selected files?\n\nThis action cannot be undone.",
            icon='warning'
        )

        if not result:
            self.logger.info("Rename cancelled by user")
            return

        self.status_label.configure(text="Renaming...", foreground='blue')
        if self.tab_frame:
            self.tab_frame.update()

        success_count = 0
        error_count = 0
        errors = []

        for file_path, new_name in files_to_rename:
            try:
                new_path = file_path.parent / new_name

                if new_path.exists() and new_path != file_path:
                    self.logger.warning(f"Skipping {file_path.name}: {new_name} already exists")
                    error_count += 1
                    errors.append(f"{file_path.name} -> {new_name} (already exists)")
                    continue

                file_path.rename(new_path)
                success_count += 1
                self.logger.info(f"Renamed: {file_path.name} -> {new_name}")

            except Exception as e:
                error_count += 1
                error_msg = f"{file_path.name}: {str(e)}"
                errors.append(error_msg)
                self.logger.error(f"Error renaming {file_path}: {e}")

        self.status_label.configure(
            text=f"Complete: {success_count} renamed, {error_count} errors",
            foreground='green' if error_count == 0 else 'orange'
        )

        if errors:
            error_text = "\n".join(errors[:10])
            if len(errors) > 10:
                error_text += f"\n... and {len(errors) - 10} more errors"
            messagebox.showwarning(
                "Rename Complete with Errors",
                f"Renamed {success_count} files.\n{error_count} errors:\n\n{error_text}"
            )
        else:
            messagebox.showinfo(
                "Rename Complete",
                f"Successfully renamed {success_count} files."
            )

        self.found_files = []
        self.selected_rows.clear()
        self.rename_button.configure(state='disabled')
        self._update_selection_label()

        headers = ['File Path', 'Old Name', 'New Name']
        data = [['Rename completed. Search again to see updated results.', '', '']]
        self.preview_table.set_data(data, headers)

    def _flash_status_warning(self, message: str) -> None:
        """Flash a warning message in the status bar."""
        original_text = self.status_label.cget('text')
        original_color = self.status_label.cget('foreground')

        # Show warning
        self.status_label.configure(text=message, foreground='red')

        # Schedule return to original after 3 seconds
        if self.tab_frame:
            self.tab_frame.after(3000, lambda: self.status_label.configure(
                text=original_text, foreground=original_color
            ))

    def _get_default_settings_path(self) -> Path:
        """Get the default path to the settings file."""
        home = Path.home()
        settings_dir = home / ".theca_procurator"
        settings_dir.mkdir(exist_ok=True)
        return settings_dir / "regex_rename_settings.toml"

    def _save_settings(self) -> None:
        """Save current form settings to TOML file."""
        try:
            # Ask user where to save
            default_path = self._get_default_settings_path()
            settings_path = filedialog.asksaveasfilename(
                title="Save Settings",
                defaultextension=".toml",
                filetypes=[("TOML files", "*.toml"), ("All files", "*.*")],
                initialdir=str(default_path.parent),
                initialfile=default_path.name
            )

            if not settings_path:
                return  # User cancelled

            settings = {
                "prefix": {
                    "type": self.prefix_type_var.get(),
                    "value": self.prefix_value_var.get(),
                    "start": self.prefix_start_var.get(),
                    "increment": self.prefix_increment_var.get(),
                    "padding": self.prefix_padding_var.get(),
                },
                "suffix": {
                    "type": self.suffix_type_var.get(),
                    "value": self.suffix_value_var.get(),
                    "start": self.suffix_start_var.get(),
                    "increment": self.suffix_increment_var.get(),
                    "padding": self.suffix_padding_var.get(),
                },
                "separator": self.separator_var.get(),
                "filter_regex": self.filter_regex_var.get(),
                "regex": {
                    "find": self.regex_find_var.get(),
                    "replace": self.regex_replace_var.get(),
                },
            }

            with open(settings_path, 'w') as f:
                toml.dump(settings, f)

            self.logger.info(f"Settings saved to {settings_path}")
            messagebox.showinfo("Settings Saved", f"Settings saved to:\n{settings_path}")

        except Exception as e:
            self.logger.error(f"Error saving settings: {e}", exc_info=True)
            messagebox.showerror("Save Error", f"Failed to save settings:\n{e}")

    def _load_settings(self) -> None:
        """Load form settings from TOML file."""
        try:
            # Ask user which file to load
            default_path = self._get_default_settings_path()
            settings_path = filedialog.askopenfilename(
                title="Load Settings",
                defaultextension=".toml",
                filetypes=[("TOML files", "*.toml"), ("All files", "*.*")],
                initialdir=str(default_path.parent),
                initialfile=default_path.name if default_path.exists() else ""
            )

            if not settings_path:
                return  # User cancelled

            with open(settings_path, 'r') as f:
                settings = toml.load(f)

            # Load prefix settings
            if "prefix" in settings:
                self.prefix_type_var.set(settings["prefix"].get("type", "literal"))
                self.prefix_value_var.set(settings["prefix"].get("value", ""))
                self.prefix_start_var.set(settings["prefix"].get("start", "1"))
                self.prefix_increment_var.set(settings["prefix"].get("increment", "1"))
                self.prefix_padding_var.set(settings["prefix"].get("padding", "0"))

            # Load suffix settings
            if "suffix" in settings:
                self.suffix_type_var.set(settings["suffix"].get("type", "literal"))
                self.suffix_value_var.set(settings["suffix"].get("value", ""))
                self.suffix_start_var.set(settings["suffix"].get("start", "1"))
                self.suffix_increment_var.set(settings["suffix"].get("increment", "1"))
                self.suffix_padding_var.set(settings["suffix"].get("padding", "0"))

            # Load separator
            if "separator" in settings:
                self.separator_var.set(settings["separator"])

            # Load filter regex
            if "filter_regex" in settings:
                self.filter_regex_var.set(settings["filter_regex"])

            # Load regex settings
            if "regex" in settings:
                self.regex_find_var.set(settings["regex"].get("find", ""))
                self.regex_replace_var.set(settings["regex"].get("replace", ""))

            # Update UI state
            self._update_prefix_state()
            self._update_suffix_state()

            self.logger.info(f"Settings loaded from {settings_path}")
            messagebox.showinfo("Settings Loaded", "Settings loaded successfully!")

        except Exception as e:
            self.logger.error(f"Error loading settings: {e}", exc_info=True)
            messagebox.showerror("Load Error", f"Failed to load settings:\n{e}")

    def deactivate(self) -> None:
        """Deactivate the plugin."""
        super().deactivate()
        self.logger.info("Deactivating Regex Rename plugin")

        if self.tab_frame:
            for widget in self.tab_frame.winfo_children():
                widget.destroy()
            self.tab_frame.destroy()
            self.tab_frame = None

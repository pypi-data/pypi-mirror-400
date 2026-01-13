"""
Main entry point for Theca Procurator application.

This module bootstraps the Extensio Pulchra Skinny framework and loads
Theca Procurator plugins.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional

# Add local packages to path
# __file__ is in: Theca Procurator/Code/Python/Main/theca_procurator/main.py
# We need: Theca Procurator/Code/Python/Local Packages
_main_dir = Path(__file__).parent.parent  # Go up to Main/
_python_dir = _main_dir.parent  # Go up to Python/
_local_packages = _python_dir / "Local Packages"

# Add each local package to sys.path
for pkg_dir in ["Extensio Pulchra Skinny/Code/Python",
                "Tabula Mutabilis",
                "Vultus Serpentis"]:
    pkg_path = str(_local_packages / pkg_dir)
    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

# Also add Tabula Mutabilis parent for direct import
tabula_parent = str(_local_packages / "Tabula Mutabilis")
if tabula_parent not in sys.path:
    sys.path.insert(0, tabula_parent)

# Now we can import from local packages
import ttkbootstrap as ttk  # noqa: E402
from yapsy.PluginManager import PluginManager  # noqa: E402

# Import Extensio Pulchra components
from bucket import Bucket  # noqa: E402
from config_manager import ConfigManager  # noqa: E402
from logging_config import setup_logging  # noqa: E402

# Import Vultus Serpentis
from vultus_serpentis import CommandManager, EventBus  # noqa: E402


class MainGui:
    """Main GUI for Theca Procurator."""

    def __init__(self, config: ConfigManager, style: ttk.Style, root: ttk.Window) -> None:
        """Initialize main GUI.

        Args:
            config: Configuration manager
            style: ttkbootstrap style
            root: Root window
        """
        self.config = config
        self.style = style
        self.root = root
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing MainGui")

        # Configure window
        self.root.title(self.config.get_app_setting('title', 'Theca Procurator'))
        self.root.minsize(
            self.config.get_ui_setting('min_width', 800),
            self.config.get_ui_setting('min_height', 600)
        )
        self.root.geometry(
            f"{self.config.get_ui_setting('window_width', 1000)}x"
            f"{self.config.get_ui_setting('window_height', 700)}"
        )

        # Create menu bar
        self.create_menu_bar()

        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)

        # Set up notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        self.logger.debug("Created notebook widget")

        # Add status bar
        self.status_bar = ttk.Label(
            main_frame,
            text="Ready",
            relief="sunken",
            padding=5,
            bootstyle="secondary"
        )
        self.status_bar.pack(side='bottom', fill='x', padx=5, pady=(0, 5))

        self.logger.info("Application initialized and ready")

    def create_menu_bar(self) -> None:
        """Create the menu bar."""
        menubar = ttk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = ttk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.file_exit)

        # Edit menu
        edit_menu = ttk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.edit_undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.edit_redo, accelerator="Ctrl+Y")

        # Help menu
        help_menu = ttk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About...", command=self.show_about)

    def file_exit(self) -> None:
        """Exit the application."""
        self.logger.info("Exiting application")
        self.root.quit()

    def edit_undo(self) -> None:
        """Undo last operation."""
        # Will be wired to CommandManager
        self.logger.info("Undo requested")

    def edit_redo(self) -> None:
        """Redo last undone operation."""
        # Will be wired to CommandManager
        self.logger.info("Redo requested")

    def show_about(self) -> None:
        """Show about dialog."""
        from tkinter import messagebox
        title = self.config.get_app_setting('title', 'Theca Procurator')
        version = self.config.get_app_setting('version', '0.1.0')
        author = self.config.get_app_setting('author', 'RH Labs')
        description = self.config.get_app_setting('description', '')

        message = f"{title}\nVersion {version}\nBy {author}\n\n{description}"
        messagebox.showinfo(f"About {title}", message)

    def update_status(self, message: str) -> None:
        """Update the status bar message.
        
        Args:
            message: Status message to display
        """
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def show(self) -> None:
        """Start the main event loop."""
        self.logger.debug("Starting main event loop")
        self.root.mainloop()


class ProgramReceiver:
    """Allows plugins to access Program and MainGui objects."""

    def __init__(self, main_gui: Optional[MainGui], program: 'Program') -> None:
        """Initialize program receiver.

        Args:
            main_gui: Main GUI instance (may be None initially)
            program: Program instance
        """
        self.logger = logging.getLogger(__name__)
        self.main_gui = main_gui
        self.program = program
        self.logger.debug("ProgramReceiver initialized")

    def put_in_bucket(self, key: str, value: object) -> None:
        """Store a value in the shared bucket."""
        self.program.bucket.put(key, value)

    def get_from_bucket(self, key: str, default: object = None) -> object:
        """Retrieve a value from the shared bucket."""
        return self.program.bucket.get(key, default)

    def remove_from_bucket(self, key: str) -> None:
        """Remove a value from the shared bucket."""
        self.program.bucket.remove(key)

    def get_bucket_keys(self) -> list[str]:
        """Get all keys in the shared bucket."""
        return list(self.program.bucket.keys())


class Program:
    """Main program class that initializes and manages the application."""

    def __init__(self, config: Optional[ConfigManager] = None) -> None:
        """Initialize program components.

        Args:
            config: Optional ConfigManager instance
        """
        # Set up logging with file output
        log_file = os.path.join(os.path.dirname(__file__), '..', 'debug.log')
        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        setup_logging()
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
        root_logger.setLevel(logging.DEBUG)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Starting Theca Procurator")
        self.logger.info(f"Log file: {log_file}")

        # Load configuration
        self.logger.info("Loading configuration...")
        self.config = config if config is not None else self._load_config()
        self.logger.info(f"Configuration loaded successfully")

        # Initialize Vultus Serpentis components
        self.event_bus = EventBus.default()
        max_undo = self.config.get_setting('operations.max_undo_steps', 10)
        self.command_manager = CommandManager(
            event_bus=self.event_bus,
            max_stack_size=max_undo
        )
        self.logger.info(f"Command manager initialized with max_undo_steps={max_undo}")

        # Initialize plugin system
        self.logger.info("Initializing plugin system...")
        self.logger.debug(f"sys.path entries: {[p for p in sys.path if 'Tabula' in p]}")
        self.plugin_manager = PluginManager()
        plugin_path = self._get_plugin_path()
        self.logger.info(f"Plugin path: {plugin_path}")
        self.logger.info(f"Plugin path exists: {os.path.exists(plugin_path)}")
        if os.path.exists(plugin_path):
            self.logger.info(f"Plugin directory contents: {os.listdir(plugin_path)}")
        self.plugin_manager.setPluginPlaces([plugin_path])
        self.logger.info("Collecting plugins...")
        self.plugin_manager.collectPlugins()
        all_plugins = self.plugin_manager.getAllPlugins()
        self.logger.info(f"Found {len(all_plugins)} plugins: {[p.name for p in all_plugins]}")
        self.logger.debug(f"Found plugins: {[p.name for p in self.plugin_manager.getAllPlugins()]}")

        # Initialize data storage
        self.bucket = Bucket()

        # Initialize program receiver for plugins
        self.logger.info("Initializing program receiver and bucket...")
        self.bucket = Bucket()
        self.program_receiver = ProgramReceiver(self.event_bus, self)
        self.main_gui: Optional[MainGui] = None

        # Call get_ready on all plugins
        self.logger.info("Calling get_ready on all plugins...")
        for plugin in self.plugin_manager.getAllPlugins():
            self.logger.info(f"Calling get_ready on plugin: {plugin.name}")
            plugin.plugin_object.get_ready(self.program_receiver)
            self.logger.info(f"get_ready completed for: {plugin.name}")

        # Create root window
        self.logger.info("Creating root window...")
        theme = self.config.get_ui_setting('theme', 'darkly')
        self.logger.info(f"Using theme: {theme}")
        self.root = ttk.Window(themename=theme)
        self.logger.info("Root window created")
        self.root.withdraw()  # Hide initially
        self.logger.info("Root window hidden initially")

    def _load_config(self) -> ConfigManager:
        """Load configuration from config.toml.

        Returns:
            ConfigManager instance
        """
        # Get explicit path to config file in theca_procurator directory
        # Handle both frozen (PyInstaller) and normal execution
        if getattr(sys, 'frozen', False):
            # Running as executable - use _MEIPASS
            base_path = sys._MEIPASS
            config_path = os.path.join(base_path, 'theca_procurator', 'config.toml')
        else:
            # Running as script
            theca_dir = os.path.dirname(__file__)
            config_path = os.path.join(theca_dir, 'config.toml')
        
        self.logger.info(f"Loading config from: {config_path}")
        
        # Create ConfigManager and manually load our config
        config = ConfigManager()
        
        # Override the config by loading our specific file
        import toml
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config.config = toml.load(f)
            self.logger.info(f"Config loaded successfully from: {config_path}")
        else:
            self.logger.error(f"Config file not found: {config_path}")
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        return config

    def _get_plugin_path(self) -> str:
        """Get the plugin directory path.

        Returns:
            Absolute path to plugins directory
        """
        if getattr(sys, 'frozen', False):
            # Running as executable - use _MEIPASS for bundled plugins
            base_path = sys._MEIPASS
            plugin_path = os.path.join(base_path, 'theca_procurator', 'plugins')
        else:
            # Running as script - use plugins folder next to main.py
            base_path = os.path.dirname(os.path.abspath(__file__))
            plugin_path = os.path.join(base_path, 'plugins')

        return plugin_path

    def set_main_gui(self, style: ttk.Style, root: ttk.Window) -> None:
        """Set the main GUI instance.

        Args:
            style: ttkbootstrap style
            root: Root window
        """
        self.main_gui = MainGui(self.config, style, root)
        self.program_receiver.main_gui = self.main_gui
        self.logger.debug("Set main GUI instance")

    def initialize_plugins_ui(self) -> None:
        """Initialize plugin UI components after main window is created."""
        self.logger.info("=== INITIALIZING PLUGIN UI COMPONENTS ===")
        self.logger.info(f"Main GUI exists: {self.main_gui is not None}")
        if self.main_gui:
            self.logger.info(f"Main GUI notebook exists: {self.main_gui.notebook is not None}")

        # Get enabled notebook plugins
        notebook_plugins = self.config.get_setting('plugins.notebook_plugins', [])
        self.logger.info(f"Configured notebook plugins: {notebook_plugins}")

        # Get enabled menu plugins
        menu_plugins = self.config.get_setting('plugins.menu_plugins', [])
        self.logger.info(f"Configured menu plugins: {menu_plugins}")

        # Activate plugins
        self.logger.info("=== ACTIVATING PLUGINS ===")
        all_plugins = self.plugin_manager.getAllPlugins()
        self.logger.info(f"Total plugins to process: {len(all_plugins)}")
        for plugin in all_plugins:
            self.logger.info(f"\n--- Processing plugin: {plugin.name} ---")
            self.logger.info(f"Plugin object type: {type(plugin.plugin_object).__name__}")

            is_notebook = any(
                p.get('name') == plugin.name and p.get('enabled', False)
                for p in notebook_plugins
            )
            is_menu = any(
                p.get('name') == plugin.name and p.get('enabled', False)
                for p in menu_plugins
            )
            
            self.logger.info(f"Plugin name: '{plugin.name}'")
            self.logger.info(f"is_notebook: {is_notebook}")
            self.logger.info(f"is_menu: {is_menu}")

            if is_notebook or is_menu:
                self.logger.info(f"*** ACTIVATING PLUGIN: {plugin.name} ***")
                try:
                    plugin.plugin_object.activate()
                    self.logger.info(f"*** Successfully activated {plugin.name} ***")
                    if hasattr(plugin.plugin_object, 'tab_frame'):
                        self.logger.info(f"Plugin has tab_frame: {plugin.plugin_object.tab_frame}")
                except Exception as e:
                    self.logger.error(
                        f"Error activating plugin {plugin.name}: {str(e)}",
                        exc_info=True
                    )
            else:
                self.logger.warning(f"Plugin {plugin.name} not in enabled plugins list")

        if self.main_gui:
            self.main_gui.status_bar.configure(text="Ready")

    def show_main_window(self) -> None:
        """Show the main window."""
        self.logger.info("=== SHOWING MAIN WINDOW ===")
        self.logger.info("Calling root.deiconify()...")
        self.root.deiconify()
        self.logger.info("root.deiconify() completed")
        if self.main_gui:
            self.logger.info("Calling main_gui.show()...")
            self.main_gui.show()
            self.logger.info("main_gui.show() completed")
        else:
            self.logger.error("main_gui is None!")
        self.logger.info("=== WINDOW SHOULD NOW BE VISIBLE ===")

    def start_up(self) -> None:
        """Start the program."""
        self.logger.info("=== STARTING UP PROGRAM ===")

        # Create main GUI
        if not self.main_gui:
            self.logger.info("Creating MainGui...")
            self.main_gui = MainGui(self.config, self.root.style, self.root)
            self.logger.info("MainGui created successfully")
            self.program_receiver.main_gui = self.main_gui
            self.logger.info("MainGui assigned to program_receiver")

        # Initialize plugin UI components
        self.logger.info("Calling initialize_plugins_ui...")
        self.initialize_plugins_ui()
        self.logger.info("initialize_plugins_ui completed")

        # Show main window
        self.logger.info("Calling show_main_window...")
        self.show_main_window()
        self.logger.info("show_main_window completed")


def main() -> None:
    """Run main entry point."""
    try:
        program = Program()
        program.start_up()
    except Exception as e:
        logging.error(f"Fatal error during startup: {str(e)}", exc_info=True)
        print(f"Fatal error: {str(e)}")
        input("Press Enter to exit...")
        sys.exit(1)


if __name__ == "__main__":
    main()

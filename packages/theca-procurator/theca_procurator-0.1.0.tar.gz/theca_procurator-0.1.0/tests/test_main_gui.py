"""
Unit tests for main.py GUI components using Imitatio Ostendendi.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# Add paths
_main_dir = Path(__file__).parent.parent
_imitatio_path = (
    Path(__file__).parent.parent.parent.parent.parent / 
    "Code" / "Python" / "Scaffold" / "Test Utils" / "Imitatio Ostendendi" / 
    "Code" / "Python" / "Code"
)

if str(_main_dir) not in sys.path:
    sys.path.insert(0, str(_main_dir))
if str(_imitatio_path) not in sys.path:
    sys.path.insert(0, str(_imitatio_path))

# Import mock widgets from imitatio_ostendendi
from imitatio_ostendendi.widgets import Frame, Button, Window, Label, Notebook

# Import modules to test
from theca_procurator.main import MainGui, ProgramReceiver, Program


class MockStyle:
    """Mock ttkbootstrap Style."""
    
    def __init__(self):
        self.theme = MagicMock()


class MockMenu:
    """Mock tkinter Menu."""
    
    def __init__(self, master=None, **kwargs):
        self.master = master
        self.items = []
        self.submenus = {}
        
    def add_command(self, **kwargs):
        self.items.append(('command', kwargs))
        
    def add_separator(self):
        self.items.append(('separator', {}))
        
    def add_cascade(self, **kwargs):
        self.items.append(('cascade', kwargs))
        if 'menu' in kwargs:
            label = kwargs.get('label', 'Menu')
            self.submenus[label] = kwargs['menu']


class TestMainGui:
    """Tests for MainGui class."""
    
    @patch('theca_procurator.main.ttk.Menu', MockMenu)
    def test_maingui_initialization(self):
        """Test MainGui initialization creates all components."""
        # Create mock config
        mock_config = MagicMock()
        mock_config.get_app_setting.return_value = "Theca Procurator"
        
        # Create mock style and root
        mock_style = MockStyle()
        mock_root = Window()
        
        # Create MainGui
        gui = MainGui(mock_config, mock_style, mock_root)
        
        # Verify attributes
        assert gui.config == mock_config
        assert gui.style == mock_style
        assert gui.root == mock_root
        assert gui.menu_bar is not None
        assert gui.notebook is not None
        assert gui.status_bar is not None
        
    @patch('theca_procurator.main.ttk.Menu', MockMenu)
    def test_maingui_creates_menu(self):
        """Test that MainGui creates menu bar with correct structure."""
        mock_config = MagicMock()
        mock_config.get_app_setting.return_value = "Theca Procurator"
        mock_style = MockStyle()
        mock_root = Window()
        
        gui = MainGui(mock_config, mock_style, mock_root)
        
        # Verify menu was created
        assert gui.menu_bar is not None
        assert isinstance(gui.menu_bar, MockMenu)
        
        # Verify submenus exist
        assert 'File' in gui.menu_bar.submenus
        assert 'Edit' in gui.menu_bar.submenus
        assert 'Help' in gui.menu_bar.submenus
        
    @patch('theca_procurator.main.ttk.Menu', MockMenu)
    def test_maingui_undo_action(self):
        """Test undo menu action."""
        mock_config = MagicMock()
        mock_config.get_app_setting.return_value = "Theca Procurator"
        mock_style = MockStyle()
        mock_root = Window()
        
        gui = MainGui(mock_config, mock_style, mock_root)
        
        # Call undo - should not raise error
        gui.undo()
        
    @patch('theca_procurator.main.ttk.Menu', MockMenu)
    def test_maingui_redo_action(self):
        """Test redo menu action."""
        mock_config = MagicMock()
        mock_config.get_app_setting.return_value = "Theca Procurator"
        mock_style = MockStyle()
        mock_root = Window()
        
        gui = MainGui(mock_config, mock_style, mock_root)
        
        # Call redo - should not raise error
        gui.redo()
        
    @patch('theca_procurator.main.ttk.Menu', MockMenu)
    @patch('tkinter.messagebox.showinfo')
    def test_maingui_show_about(self, mock_showinfo):
        """Test show about dialog."""
        mock_config = MagicMock()
        mock_config.get_app_setting.side_effect = lambda key, default: {
            'title': 'Theca Procurator',
            'version': '0.1.0',
            'author': 'RH Labs',
            'description': 'Test Description'
        }.get(key, default)
        
        mock_style = MockStyle()
        mock_root = Window()
        
        gui = MainGui(mock_config, mock_style, mock_root)
        gui.show_about()
        
        # Verify messagebox was called
        assert mock_showinfo.called
        call_args = mock_showinfo.call_args
        assert 'Theca Procurator' in str(call_args)
        
    @patch('theca_procurator.main.ttk.Menu', MockMenu)
    def test_maingui_show(self):
        """Test show method starts mainloop."""
        mock_config = MagicMock()
        mock_config.get_app_setting.return_value = "Theca Procurator"
        mock_style = MockStyle()
        mock_root = Window()
        
        gui = MainGui(mock_config, mock_style, mock_root)
        gui.show()
        
        # Verify mainloop was called
        assert mock_root.mainloop_called


class TestProgramReceiver:
    """Tests for ProgramReceiver class."""
    
    def test_program_receiver_initialization(self):
        """Test ProgramReceiver initialization."""
        mock_program = MagicMock()
        receiver = ProgramReceiver(None, mock_program)
        
        assert receiver.main_gui is None
        assert receiver.program == mock_program
        
    def test_put_in_bucket(self):
        """Test put_in_bucket method."""
        mock_program = MagicMock()
        receiver = ProgramReceiver(None, mock_program)
        
        # Test putting items in bucket
        receiver.put_in_bucket("test_key", "test_value")
        
        # Verify put was called on program.bucket
        assert mock_program.bucket.put.called
        
    def test_get_from_bucket(self):
        """Test getting value from bucket."""
        mock_program = MagicMock()
        mock_program.bucket = {'test_key': 'test_value'}
        receiver = ProgramReceiver(None, mock_program)
        
        value = receiver.get_from_bucket('test_key')
        
        assert value == 'test_value'
        
    def test_get_from_bucket_default(self):
        """Test getting value from bucket with default."""
        mock_program = MagicMock()
        mock_program.bucket = {}
        receiver = ProgramReceiver(None, mock_program)
        
        value = receiver.get_from_bucket('missing_key', 'default_value')
        
        assert value == 'default_value'
        
    def test_get_bucket_keys(self):
        """Test getting all bucket keys."""
        mock_program = MagicMock()
        mock_program.bucket.keys.return_value = ['key1', 'key2', 'key3']
        receiver = ProgramReceiver(None, mock_program)
        
        keys = receiver.get_bucket_keys()
        
        assert keys == ['key1', 'key2', 'key3']


class TestProgram:
    """Tests for Program class."""
    
    @patch('theca_procurator.main.setup_logging')
    @patch('theca_procurator.main.ConfigManager')
    @patch('theca_procurator.main.EventBus')
    @patch('theca_procurator.main.CommandManager')
    @patch('theca_procurator.main.PluginManager')
    @patch('theca_procurator.main.ttk.Window', Window)
    def test_program_initialization(self, mock_plugin_mgr, mock_cmd_mgr, 
                                    mock_event_bus, mock_config_mgr, mock_logging):
        """Test Program initialization."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.get_setting.return_value = 10
        mock_config_mgr.return_value = mock_config
        
        mock_eb = MagicMock()
        mock_event_bus.default.return_value = mock_eb
        
        mock_cm = MagicMock()
        mock_cmd_mgr.return_value = mock_cm
        
        mock_pm = MagicMock()
        mock_pm.getAllPlugins.return_value = []
        mock_plugin_mgr.return_value = mock_pm
        
        # Create program
        program = Program()
        
        # Verify initialization
        assert program.config == mock_config
        assert program.event_bus == mock_eb
        assert program.command_manager == mock_cm
        assert program.plugin_manager == mock_pm
        assert program.bucket is not None
        assert program.program_receiver is not None
        
    @patch('theca_procurator.main.setup_logging')
    @patch('theca_procurator.main.ConfigManager')
    @patch('theca_procurator.main.EventBus')
    @patch('theca_procurator.main.CommandManager')
    @patch('theca_procurator.main.PluginManager')
    @patch('theca_procurator.main.ttk.Window', Window)
    def test_program_with_custom_config(self, mock_plugin_mgr, mock_cmd_mgr,
                                       mock_event_bus, mock_config_mgr, mock_logging):
        """Test Program with custom config."""
        # Setup mocks
        custom_config = MagicMock()
        custom_config.get_setting.return_value = 10
        
        mock_eb = MagicMock()
        mock_event_bus.default.return_value = mock_eb
        
        mock_cm = MagicMock()
        mock_cmd_mgr.return_value = mock_cm
        
        mock_pm = MagicMock()
        mock_pm.getAllPlugins.return_value = []
        mock_plugin_mgr.return_value = mock_pm
        
        # Create program with custom config
        program = Program(config=custom_config)
        
        # Verify custom config was used
        assert program.config == custom_config
        # ConfigManager should not have been called
        assert not mock_config_mgr.called
        
    @patch('theca_procurator.main.setup_logging')
    @patch('theca_procurator.main.ConfigManager')
    @patch('theca_procurator.main.EventBus')
    @patch('theca_procurator.main.CommandManager')
    @patch('theca_procurator.main.PluginManager')
    @patch('theca_procurator.main.ttk.Window', Window)
    @patch('theca_procurator.main.ttk.Menu', MockMenu)
    def test_program_startup(self, mock_plugin_mgr, mock_cmd_mgr,
                            mock_event_bus, mock_config_mgr, mock_logging):
        """Test Program startup sequence."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.get_setting.return_value = 10
        mock_config.get_app_setting.return_value = "Theca Procurator"
        mock_config.get_ui_setting.return_value = "darkly"
        mock_config_mgr.return_value = mock_config
        
        mock_eb = MagicMock()
        mock_event_bus.default.return_value = mock_eb
        
        mock_cm = MagicMock()
        mock_cmd_mgr.return_value = mock_cm
        
        mock_pm = MagicMock()
        mock_pm.getAllPlugins.return_value = []
        mock_plugin_mgr.return_value = mock_pm
        
        # Create and start program
        program = Program()
        program.start_up()
        
        # Verify main_gui was created
        assert program.main_gui is not None
        assert program.program_receiver.main_gui is not None
        
    @patch('theca_procurator.main.setup_logging')
    @patch('theca_procurator.main.ConfigManager')
    @patch('theca_procurator.main.EventBus')
    @patch('theca_procurator.main.CommandManager')
    @patch('theca_procurator.main.PluginManager')
    @patch('theca_procurator.main.ttk.Window', Window)
    def test_program_plugin_activation(self, mock_plugin_mgr, mock_cmd_mgr,
                                      mock_event_bus, mock_config_mgr, mock_logging):
        """Test plugin activation during initialization."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.get_setting.side_effect = lambda key, default: {
            'operations.max_undo_steps': 10,
            'plugins.notebook_plugins': [{'name': 'TestPlugin', 'enabled': True}],
            'plugins.menu_plugins': []
        }.get(key, default)
        mock_config_mgr.return_value = mock_config
        
        mock_eb = MagicMock()
        mock_event_bus.default.return_value = mock_eb
        
        mock_cm = MagicMock()
        mock_cmd_mgr.return_value = mock_cm
        
        # Create mock plugin
        mock_plugin = MagicMock()
        mock_plugin.name = 'TestPlugin'
        mock_plugin.plugin_object.get_ready = MagicMock()
        mock_plugin.plugin_object.activate = MagicMock()
        
        mock_pm = MagicMock()
        mock_pm.getAllPlugins.return_value = [mock_plugin]
        mock_plugin_mgr.return_value = mock_pm
        
        # Create program
        program = Program()
        
        # Verify plugin get_ready was called
        assert mock_plugin.plugin_object.get_ready.called
        
    @patch('theca_procurator.main.setup_logging')
    @patch('theca_procurator.main.ConfigManager')
    @patch('theca_procurator.main.EventBus')
    @patch('theca_procurator.main.CommandManager')
    @patch('theca_procurator.main.PluginManager')
    @patch('theca_procurator.main.ttk.Window', Window)
    @patch('theca_procurator.main.ttk.Menu', MockMenu)
    def test_program_show_main_window(self, mock_plugin_mgr, mock_cmd_mgr,
                                     mock_event_bus, mock_config_mgr, mock_logging):
        """Test showing main window."""
        # Setup mocks
        mock_config = MagicMock()
        mock_config.get_setting.return_value = 10
        mock_config.get_app_setting.return_value = "Theca Procurator"
        mock_config.get_ui_setting.return_value = "darkly"
        mock_config_mgr.return_value = mock_config
        
        mock_eb = MagicMock()
        mock_event_bus.default.return_value = mock_eb
        
        mock_cm = MagicMock()
        mock_cmd_mgr.return_value = mock_cm
        
        mock_pm = MagicMock()
        mock_pm.getAllPlugins.return_value = []
        mock_plugin_mgr.return_value = mock_pm
        
        # Create program
        program = Program()
        program.start_up()
        
        # Show window
        program.show_main_window()
        
        # Verify window is shown
        assert program.root.shown or not program.root.withdrawn


class TestMainFunction:
    """Tests for main() entry point."""
    
    @patch('theca_procurator.main.Program')
    def test_main_success(self, mock_program_class):
        """Test successful main execution."""
        from theca_procurator.main import main
        
        mock_program = MagicMock()
        mock_program_class.return_value = mock_program
        
        # Call main
        main()
        
        # Verify program was created and started
        assert mock_program_class.called
        assert mock_program.start_up.called
        
    @patch('theca_procurator.main.Program')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_main_exception_handling(self, mock_print, mock_input, mock_program_class):
        """Test main handles exceptions."""
        from theca_procurator.main import main
        
        # Make Program raise exception
        mock_program_class.side_effect = RuntimeError("Test error")
        
        # Call main - should not raise
        with pytest.raises(SystemExit) as exc_info:
            main()
            
        # Verify exit code
        assert exc_info.value.code == 1

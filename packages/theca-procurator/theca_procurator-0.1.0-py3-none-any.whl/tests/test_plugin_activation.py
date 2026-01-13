"""
Tests for plugin activation and discovery.

This test file identifies bugs in plugin loading and activation.
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

from imitatio_ostendendi.widgets import Frame, Button, Window, Label, Notebook
from theca_procurator.main import Program


class TestPluginActivation:
    """Tests for plugin activation."""
    
    @patch('theca_procurator.main.setup_logging')
    @patch('theca_procurator.main.ttk.Window', Window)
    def test_plugin_discovery(self, mock_logging):
        """Test that plugins are discovered by Yapsy."""
        program = Program()
        
        # Check that plugin manager found plugins
        all_plugins = program.plugin_manager.getAllPlugins()
        plugin_names = [p.name for p in all_plugins]
        
        print(f"Discovered plugins: {plugin_names}")
        
        # Should find at least the Duplicate Folders plugin
        assert len(all_plugins) > 0, "No plugins were discovered"
        assert any("Duplicate" in name or "duplicate" in name.lower() 
                   for name in plugin_names), \
            f"Duplicate Folders plugin not found. Found: {plugin_names}"
    
    @patch('theca_procurator.main.setup_logging')
    @patch('theca_procurator.main.ttk.Window', Window)
    @patch('theca_procurator.main.ttk.Menu')
    def test_plugin_get_ready_called(self, mock_menu, mock_logging):
        """Test that get_ready is called on plugins during initialization."""
        program = Program()
        
        # Check that plugins have program_receiver set
        for plugin in program.plugin_manager.getAllPlugins():
            if hasattr(plugin.plugin_object, 'program_receiver'):
                assert plugin.plugin_object.program_receiver is not None, \
                    f"Plugin {plugin.name} program_receiver not set"
    
    @patch('theca_procurator.main.setup_logging')
    @patch('theca_procurator.main.ttk.Window', Window)
    @patch('theca_procurator.main.ttk.Menu')
    def test_plugin_activation_on_startup(self, *args):
        """Test that enabled plugins are activated during startup."""
        program = Program()
        program.start_up()
        
        # Check that main_gui has notebook
        assert program.main_gui is not None, "MainGui not created"
        assert program.main_gui.notebook is not None, "Notebook not created"
        
        # Check that plugins were activated
        activated_plugins = []
        for plugin in program.plugin_manager.getAllPlugins():
            if hasattr(plugin.plugin_object, 'tab_frame'):
                if plugin.plugin_object.tab_frame is not None:
                    activated_plugins.append(plugin.name)
        
        print(f"Activated plugins: {activated_plugins}")
        
        # Should have activated Duplicate Folders plugin
        assert len(activated_plugins) > 0, \
            "No plugins were activated (no tab_frame created)"
        
        # Specifically check for Duplicate Folders
        assert "Duplicate Folders" in activated_plugins, \
            f"Duplicate Folders plugin was not activated. Activated: {activated_plugins}"
    
    @patch('ttkbootstrap.Text', Frame)
    @patch('ttkbootstrap.IntVar', MagicMock)
    @patch('ttkbootstrap.StringVar', MagicMock)
    @patch('ttkbootstrap.Spinbox', Frame)
    @patch('ttkbootstrap.Button', Button)
    @patch('ttkbootstrap.Entry', Frame)
    @patch('ttkbootstrap.Label', Label)
    @patch('ttkbootstrap.LabelFrame', Frame)
    @patch('ttkbootstrap.Frame', Frame)
    @patch('theca_procurator.main.ttk.Menu')
    @patch('theca_procurator.main.ttk.Window', Window)
    @patch('theca_procurator.main.setup_logging')
    def test_duplicate_folders_tab_added_to_notebook(self, mock_logging, mock_window, mock_menu, *args):
        """Test that Duplicate Folders tab is added to the notebook."""
        program = Program()
        program.start_up()
        
        # Check notebook has tabs
        notebook = program.main_gui.notebook
        
        # The mock Notebook should have tabs added via add()
        assert notebook.add.called, "No tabs were added to notebook"
        
        # Check that at least one tab was added
        call_count = notebook.add.call_count
        print(f"Notebook.add() called {call_count} times")
        
        assert call_count > 0, "Notebook.add() was never called"

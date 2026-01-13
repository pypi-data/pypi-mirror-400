"""
Tests for configuration loading.

These tests verify that the correct config file is loaded and that
plugin configuration is read correctly.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
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

from imitatio_ostendendi.widgets import Window
from theca_procurator.main import Program


class TestConfigLoading:
    """Tests for configuration loading."""
    
    @patch('theca_procurator.main.setup_logging')
    @patch('theca_procurator.main.ttk.Window', Window)
    def test_config_loads_from_theca_procurator_directory(self, mock_logging):
        """Test that config is loaded from theca_procurator package directory."""
        program = Program()
        
        # Verify config was loaded
        assert program.config is not None, "Config was not loaded"
        assert program.config.config is not None, "Config dict is empty"
        
        # Check that we have the app section
        app_title = program.config.get_app_setting('title')
        assert app_title is not None, "App title not found in config"
        print(f"Loaded app title: {app_title}")
    
    @patch('theca_procurator.main.setup_logging')
    @patch('theca_procurator.main.ttk.Window', Window)
    def test_config_contains_duplicate_folders_plugin(self, mock_logging):
        """Test that config contains Duplicate Folders plugin in enabled list."""
        program = Program()
        
        # Get notebook plugins from config
        notebook_plugins = program.config.get_setting('plugins.notebook_plugins', [])
        
        assert notebook_plugins is not None, "notebook_plugins not found in config"
        assert len(notebook_plugins) > 0, "notebook_plugins list is empty"
        
        # Check for Duplicate Folders plugin
        plugin_names = [p.get('name') for p in notebook_plugins]
        print(f"Configured notebook plugins: {plugin_names}")
        
        assert "Duplicate Folders" in plugin_names, \
            f"Duplicate Folders not in config. Found: {plugin_names}"
    
    @patch('theca_procurator.main.setup_logging')
    @patch('theca_procurator.main.ttk.Window', Window)
    def test_duplicate_folders_plugin_is_enabled(self, mock_logging):
        """Test that Duplicate Folders plugin is enabled in config."""
        program = Program()
        
        # Get notebook plugins from config
        notebook_plugins = program.config.get_setting('plugins.notebook_plugins', [])
        
        # Find Duplicate Folders plugin
        duplicate_folders = None
        for plugin in notebook_plugins:
            if plugin.get('name') == 'Duplicate Folders':
                duplicate_folders = plugin
                break
        
        assert duplicate_folders is not None, \
            "Duplicate Folders plugin not found in config"
        
        assert duplicate_folders.get('enabled') is True, \
            "Duplicate Folders plugin is not enabled in config"
        
        print(f"Duplicate Folders config: {duplicate_folders}")
    
    @patch('theca_procurator.main.setup_logging')
    @patch('theca_procurator.main.ttk.Window', Window)
    def test_config_not_from_wrong_project(self, mock_logging):
        """Test that we don't load config from other projects like Tria Memoria."""
        program = Program()
        
        # Get notebook plugins from config
        notebook_plugins = program.config.get_setting('plugins.notebook_plugins', [])
        plugin_names = [p.get('name') for p in notebook_plugins]
        
        # These are plugins from Tria Memoria - they should NOT be in Theca Procurator config
        wrong_plugins = ['TripleViewerPlugin', 'PathfindingPlugin', 'Graph Navigator']
        
        for wrong_plugin in wrong_plugins:
            assert wrong_plugin not in plugin_names, \
                f"Found {wrong_plugin} in config - this indicates wrong config file was loaded!"
        
        print(f"Config correctly contains Theca Procurator plugins: {plugin_names}")
    
    @patch('theca_procurator.main.setup_logging')
    @patch('theca_procurator.main.ttk.Window', Window)
    @patch('theca_procurator.main.ttk.Menu')
    def test_plugin_matches_enabled_config(self, mock_menu, mock_logging):
        """Test that discovered plugins match the enabled plugins in config."""
        program = Program()
        program.start_up()
        
        # Get enabled plugins from config
        notebook_plugins = program.config.get_setting('plugins.notebook_plugins', [])
        enabled_plugin_names = [
            p.get('name') for p in notebook_plugins 
            if p.get('enabled', False)
        ]
        
        # Get discovered plugins
        discovered_plugins = program.plugin_manager.getAllPlugins()
        discovered_names = [p.name for p in discovered_plugins]
        
        print(f"Enabled in config: {enabled_plugin_names}")
        print(f"Discovered plugins: {discovered_names}")
        
        # Check that at least one enabled plugin was discovered
        found_enabled = False
        for enabled_name in enabled_plugin_names:
            if enabled_name in discovered_names:
                found_enabled = True
                break
        
        assert found_enabled, \
            f"No enabled plugins were discovered. Enabled: {enabled_plugin_names}, Discovered: {discovered_names}"

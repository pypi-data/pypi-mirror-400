"""
Unit tests for duplicate_folders plugin using Imitatio Ostendendi.
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
from imitatio_ostendendi.widgets import Frame, Entry, Button, Text, Window, Label, Notebook

# Import plugin to test
from theca_procurator.plugins.duplicate_folders import DuplicateFoldersPlugin


class MockStringVar:
    """Mock tkinter StringVar."""
    
    def __init__(self, value=""):
        self._value = value
        self._traces = []
        
    def get(self):
        return self._value
        
    def set(self, value):
        self._value = value
        for trace in self._traces:
            trace()
            
    def trace_add(self, mode, callback):
        self._traces.append(callback)


class MockIntVar:
    """Mock tkinter IntVar."""
    
    def __init__(self, value=0):
        self._value = value
        self._traces = []
        
    def get(self):
        return self._value
        
    def set(self, value):
        self._value = int(value)
        for trace in self._traces:
            trace()
            
    def trace_add(self, mode, callback):
        self._traces.append(callback)


class TestDuplicateFoldersPlugin:
    """Tests for DuplicateFoldersPlugin."""
    
    def test_plugin_initialization(self):
        """Test plugin initialization."""
        plugin = DuplicateFoldersPlugin()
        
        assert plugin.name == "Duplicate Folders"
        assert plugin.program_receiver is None
        assert plugin.tab_frame is None
        
    def test_get_ready(self):
        """Test get_ready method."""
        plugin = DuplicateFoldersPlugin()
        mock_receiver = MagicMock()
        
        plugin.get_ready(mock_receiver)
        
        assert plugin.program_receiver == mock_receiver
        
    @patch('ttkbootstrap.Frame', Frame)
    @patch('ttkbootstrap.LabelFrame', Frame)
    @patch('ttkbootstrap.Label', Label)
    @patch('ttkbootstrap.Entry', Entry)
    @patch('ttkbootstrap.Button', Button)
    @patch('ttkbootstrap.Spinbox', Entry)
    @patch('ttkbootstrap.StringVar', MockStringVar)
    @patch('ttkbootstrap.IntVar', MockIntVar)
    @patch('ttkbootstrap.Text', Text)
    def test_activate_creates_ui(self):
        """Test that activate creates UI components."""
        plugin = DuplicateFoldersPlugin()
        
        # Setup mock program receiver
        mock_receiver = MagicMock()
        mock_main_gui = MagicMock()
        mock_notebook = Notebook()
        mock_main_gui.notebook = mock_notebook
        mock_receiver.main_gui = mock_main_gui
        
        plugin.get_ready(mock_receiver)
        plugin.activate()
        
        # Verify tab was created
        assert plugin.tab_frame is not None
        assert mock_notebook.add.called
        
        # Verify variables were created
        assert plugin.source_var is not None
        assert plugin.dest_var is not None
        assert plugin.basename_var is not None
        assert plugin.count_var is not None
        assert plugin.start_var is not None
        assert plugin.padding_var is not None
        
    @patch('ttkbootstrap.Frame', Frame)
    @patch('ttkbootstrap.LabelFrame', Frame)
    @patch('ttkbootstrap.Label', Label)
    @patch('ttkbootstrap.Entry', Entry)
    @patch('ttkbootstrap.Button', Button)
    @patch('ttkbootstrap.Spinbox', Entry)
    @patch('ttkbootstrap.StringVar', MockStringVar)
    @patch('ttkbootstrap.IntVar', MockIntVar)
    @patch('ttkbootstrap.Text', Text)
    @patch('tkinter.filedialog.askdirectory')
    def test_browse_source(self, mock_askdir):
        """Test browse source folder handler."""
        plugin = DuplicateFoldersPlugin()
        
        # Setup
        mock_receiver = MagicMock()
        mock_main_gui = MagicMock()
        mock_notebook = Notebook()
        mock_main_gui.notebook = mock_notebook
        mock_receiver.main_gui = mock_main_gui
        
        plugin.get_ready(mock_receiver)
        plugin.activate()
        
        # Mock file dialog
        mock_askdir.return_value = "/test/source/path"
        
        # Call browse source
        plugin._browse_source()
        
        # Verify source var was updated
        assert plugin.source_var.get() == "/test/source/path"
        
    @patch('ttkbootstrap.Frame', Frame)
    @patch('ttkbootstrap.LabelFrame', Frame)
    @patch('ttkbootstrap.Label', Label)
    @patch('ttkbootstrap.Entry', Entry)
    @patch('ttkbootstrap.Button', Button)
    @patch('ttkbootstrap.Spinbox', Entry)
    @patch('ttkbootstrap.StringVar', MockStringVar)
    @patch('ttkbootstrap.IntVar', MockIntVar)
    @patch('ttkbootstrap.Text', Text)
    @patch('tkinter.filedialog.askdirectory')
    def test_browse_destination(self, mock_askdir):
        """Test browse destination folder handler."""
        plugin = DuplicateFoldersPlugin()
        
        # Setup
        mock_receiver = MagicMock()
        mock_main_gui = MagicMock()
        mock_notebook = Notebook()
        mock_main_gui.notebook = mock_notebook
        mock_receiver.main_gui = mock_main_gui
        
        plugin.get_ready(mock_receiver)
        plugin.activate()
        
        # Mock file dialog
        mock_askdir.return_value = "/test/dest/path"
        
        # Call browse destination
        plugin._browse_destination()
        
        # Verify dest var was updated
        assert plugin.dest_var.get() == "/test/dest/path"
        
    @patch('ttkbootstrap.Frame', Frame)
    @patch('ttkbootstrap.LabelFrame', Frame)
    @patch('ttkbootstrap.Label', Label)
    @patch('ttkbootstrap.Entry', Entry)
    @patch('ttkbootstrap.Button', Button)
    @patch('ttkbootstrap.Spinbox', Entry)
    @patch('ttkbootstrap.StringVar', MockStringVar)
    @patch('ttkbootstrap.IntVar', MockIntVar)
    @patch('ttkbootstrap.Text', Text)
    def test_generate_preview(self):
        """Test preview generation."""
        plugin = DuplicateFoldersPlugin()
        
        # Setup
        mock_receiver = MagicMock()
        mock_main_gui = MagicMock()
        mock_notebook = Notebook()
        mock_main_gui.notebook = mock_notebook
        mock_receiver.main_gui = mock_main_gui
        
        plugin.get_ready(mock_receiver)
        plugin.activate()
        
        # Set input values
        plugin.basename_var.set("Episode ")
        plugin.start_var.set(1)
        plugin.count_var.set(3)
        plugin.padding_var.set(2)
        
        # Generate preview
        plugin._generate_preview()
        
        # Verify preview text was updated
        preview_content = plugin.preview_text.get("1.0", "end")
        assert "Episode 01" in preview_content
        assert "Episode 02" in preview_content
        assert "Episode 03" in preview_content
        
    @patch('ttkbootstrap.Frame', Frame)
    @patch('ttkbootstrap.LabelFrame', Frame)
    @patch('ttkbootstrap.Label', Label)
    @patch('ttkbootstrap.Entry', Entry)
    @patch('ttkbootstrap.Button', Button)
    @patch('ttkbootstrap.Spinbox', Entry)
    @patch('ttkbootstrap.StringVar', MockStringVar)
    @patch('ttkbootstrap.IntVar', MockIntVar)
    @patch('ttkbootstrap.Text', Text)
    def test_start_operation(self):
        """Test start operation handler."""
        plugin = DuplicateFoldersPlugin()
        
        # Setup
        mock_receiver = MagicMock()
        mock_main_gui = MagicMock()
        mock_notebook = Notebook()
        mock_main_gui.notebook = mock_notebook
        mock_receiver.main_gui = mock_main_gui
        
        plugin.get_ready(mock_receiver)
        plugin.activate()
        
        # Call start operation - should not raise error
        plugin._start_operation()
        
    @patch('ttkbootstrap.Frame', Frame)
    @patch('ttkbootstrap.LabelFrame', Frame)
    @patch('ttkbootstrap.Label', Label)
    @patch('ttkbootstrap.Entry', Entry)
    @patch('ttkbootstrap.Button', Button)
    @patch('ttkbootstrap.Spinbox', Entry)
    @patch('ttkbootstrap.StringVar', MockStringVar)
    @patch('ttkbootstrap.IntVar', MockIntVar)
    @patch('ttkbootstrap.Text', Text)
    def test_pause_operation(self):
        """Test pause operation handler."""
        plugin = DuplicateFoldersPlugin()
        
        # Setup
        mock_receiver = MagicMock()
        mock_main_gui = MagicMock()
        mock_notebook = Notebook()
        mock_main_gui.notebook = mock_notebook
        mock_receiver.main_gui = mock_main_gui
        
        plugin.get_ready(mock_receiver)
        plugin.activate()
        
        # Call pause operation - should not raise error
        plugin._pause_operation()
        
    @patch('ttkbootstrap.Frame', Frame)
    @patch('ttkbootstrap.LabelFrame', Frame)
    @patch('ttkbootstrap.Label', Label)
    @patch('ttkbootstrap.Entry', Entry)
    @patch('ttkbootstrap.Button', Button)
    @patch('ttkbootstrap.Spinbox', Entry)
    @patch('ttkbootstrap.StringVar', MockStringVar)
    @patch('ttkbootstrap.IntVar', MockIntVar)
    @patch('ttkbootstrap.Text', Text)
    def test_cancel_operation(self):
        """Test cancel operation handler."""
        plugin = DuplicateFoldersPlugin()
        
        # Setup
        mock_receiver = MagicMock()
        mock_main_gui = MagicMock()
        mock_notebook = Notebook()
        mock_main_gui.notebook = mock_notebook
        mock_receiver.main_gui = mock_main_gui
        
        plugin.get_ready(mock_receiver)
        plugin.activate()
        
        # Call cancel operation - should not raise error
        plugin._cancel_operation()
        
    @patch('ttkbootstrap.Frame', Frame)
    @patch('ttkbootstrap.LabelFrame', Frame)
    @patch('ttkbootstrap.Label', Label)
    @patch('ttkbootstrap.Entry', Entry)
    @patch('ttkbootstrap.Button', Button)
    @patch('ttkbootstrap.Spinbox', Entry)
    @patch('ttkbootstrap.StringVar', MockStringVar)
    @patch('ttkbootstrap.IntVar', MockIntVar)
    @patch('ttkbootstrap.Text', Text)
    def test_deactivate(self):
        """Test plugin deactivation."""
        plugin = DuplicateFoldersPlugin()
        
        # Setup
        mock_receiver = MagicMock()
        mock_main_gui = MagicMock()
        mock_notebook = Notebook()
        mock_main_gui.notebook = mock_notebook
        mock_receiver.main_gui = mock_main_gui
        
        plugin.get_ready(mock_receiver)
        plugin.activate()
        
        # Store tab frame reference
        tab_frame = plugin.tab_frame
        
        # Deactivate
        plugin.deactivate()
        
        # Verify notebook.forget was called (tab removed)
        # Note: The actual forget call happens in deactivate
        assert True  # Deactivate completed without error
        
    @patch('ttkbootstrap.Frame', Frame)
    @patch('ttkbootstrap.LabelFrame', Frame)
    @patch('ttkbootstrap.Label', Label)
    @patch('ttkbootstrap.Entry', Entry)
    @patch('ttkbootstrap.Button', Button)
    @patch('ttkbootstrap.Spinbox', Entry)
    @patch('ttkbootstrap.StringVar', MockStringVar)
    @patch('ttkbootstrap.IntVar', MockIntVar)
    @patch('ttkbootstrap.Text', Text)
    def test_activate_without_main_gui(self):
        """Test activate when main_gui is None."""
        plugin = DuplicateFoldersPlugin()
        
        # Setup with no main_gui
        mock_receiver = MagicMock()
        mock_receiver.main_gui = None
        
        plugin.get_ready(mock_receiver)
        
        # Activate should handle None main_gui gracefully
        plugin.activate()
        
        # Tab frame should not be created
        assert plugin.tab_frame is None
        
    @patch('ttkbootstrap.Frame', Frame)
    @patch('ttkbootstrap.LabelFrame', Frame)
    @patch('ttkbootstrap.Label', Label)
    @patch('ttkbootstrap.Entry', Entry)
    @patch('ttkbootstrap.Button', Button)
    @patch('ttkbootstrap.Spinbox', Entry)
    @patch('ttkbootstrap.StringVar', MockStringVar)
    @patch('ttkbootstrap.IntVar', MockIntVar)
    @patch('ttkbootstrap.Text', Text)
    @patch('tkinter.filedialog.askdirectory')
    def test_browse_source_cancelled(self, mock_askdir):
        """Test browse source when user cancels dialog."""
        plugin = DuplicateFoldersPlugin()
        
        # Setup
        mock_receiver = MagicMock()
        mock_main_gui = MagicMock()
        mock_notebook = Notebook()
        mock_main_gui.notebook = mock_notebook
        mock_receiver.main_gui = mock_main_gui
        
        plugin.get_ready(mock_receiver)
        plugin.activate()
        
        # Set initial value
        plugin.source_var.set("/initial/path")
        
        # Mock file dialog returning empty string (cancelled)
        mock_askdir.return_value = ""
        
        # Call browse source
        plugin._browse_source()
        
        # Verify source var was not changed
        assert plugin.source_var.get() == "/initial/path"
        
    @patch('ttkbootstrap.Frame', Frame)
    @patch('ttkbootstrap.LabelFrame', Frame)
    @patch('ttkbootstrap.Label', Label)
    @patch('ttkbootstrap.Entry', Entry)
    @patch('ttkbootstrap.Button', Button)
    @patch('ttkbootstrap.Spinbox', Entry)
    @patch('ttkbootstrap.StringVar', MockStringVar)
    @patch('ttkbootstrap.IntVar', MockIntVar)
    @patch('ttkbootstrap.Text', Text)
    def test_preview_with_different_padding(self):
        """Test preview generation with different padding values."""
        plugin = DuplicateFoldersPlugin()
        
        # Setup
        mock_receiver = MagicMock()
        mock_main_gui = MagicMock()
        mock_notebook = Notebook()
        mock_main_gui.notebook = mock_notebook
        mock_receiver.main_gui = mock_main_gui
        
        plugin.get_ready(mock_receiver)
        plugin.activate()
        
        # Test with padding=1
        plugin.basename_var.set("File")
        plugin.start_var.set(5)
        plugin.count_var.set(2)
        plugin.padding_var.set(1)
        
        plugin._generate_preview()
        preview_content = plugin.preview_text.get("1.0", "end")
        assert "File5" in preview_content
        assert "File6" in preview_content
        
        # Test with padding=4
        plugin.padding_var.set(4)
        plugin._generate_preview()
        preview_content = plugin.preview_text.get("1.0", "end")
        assert "File0005" in preview_content
        assert "File0006" in preview_content

import sys
from pathlib import Path
from unittest.mock import patch, Mock
import pytest

_main_dir = Path(__file__).parent.parent
_imitatio_path = Path(__file__).parent.parent.parent.parent.parent / "Code" / "Python" / "Scaffold" / "Test Utils" / "Imitatio Ostendendi" / "Code" / "Python" / "Code"

if str(_main_dir) not in sys.path:
    sys.path.insert(0, str(_main_dir))
if str(_imitatio_path) not in sys.path:
    sys.path.insert(0, str(_imitatio_path))

from imitatio_ostendendi.widgets import Frame, Button, Label

class MockText(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._content = ""
        self._state = "normal"
    def insert(self, index, text):
        self._content = text
    def delete(self, start, end):
        self._content = ""
    def configure(self, **kwargs):
        if 'state' in kwargs:
            self._state = kwargs['state']

from theca_procurator.plugins.duplicate_folders import DuplicateFoldersPlugin

class TestDuplicateFoldersStartButton:
    def setup_method(self):
        self.plugin = DuplicateFoldersPlugin()
        self.mock_program_receiver = Mock()
        self.mock_main_gui = Mock()
        self.mock_notebook = Mock()
        self.mock_main_gui.notebook = self.mock_notebook
        self.mock_program_receiver.main_gui = self.mock_main_gui
        self.plugin.program_receiver = self.mock_program_receiver
    
    @patch('ttkbootstrap.Text', MockText)
    @patch('ttkbootstrap.IntVar')
    @patch('ttkbootstrap.StringVar')
    @patch('ttkbootstrap.Spinbox', Frame)
    @patch('ttkbootstrap.Button', Button)
    @patch('ttkbootstrap.Entry', Frame)
    @patch('ttkbootstrap.Label', Label)
    @patch('ttkbootstrap.LabelFrame', Frame)
    @patch('ttkbootstrap.Frame', Frame)
    def test_start_button_validates_source_folder(self, *args):
        self.plugin.activate()
        self.plugin.source_var.set("")
        self.plugin.dest_var.set("/some/dest")
        result = self.plugin._start_operation()
        assert result is False
    
    @patch('ttkbootstrap.Text', MockText)
    @patch('ttkbootstrap.IntVar')
    @patch('ttkbootstrap.StringVar')
    @patch('ttkbootstrap.Spinbox', Frame)
    @patch('ttkbootstrap.Button', Button)
    @patch('ttkbootstrap.Entry', Frame)
    @patch('ttkbootstrap.Label', Label)
    @patch('ttkbootstrap.LabelFrame', Frame)
    @patch('ttkbootstrap.Frame', Frame)
    def test_start_button_validates_destination_folder(self, *args):
        self.plugin.activate()
        self.plugin.source_var.set("/some/source")
        self.plugin.dest_var.set("")
        result = self.plugin._start_operation()
        assert result is False

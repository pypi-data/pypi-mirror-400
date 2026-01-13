"""
Unit tests for Regex Rename plugin row selection functionality.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock
import tempfile
import pytest

# Add Local Packages to sys.path
test_file = Path(__file__).resolve()
main_dir = test_file.parent.parent
repo_root = main_dir.parent.parent.parent
local_packages = repo_root / "Code" / "Python" / "Local Packages"
tabula_path = local_packages / "Tabula Mutabilis"
if str(tabula_path) not in sys.path:
    sys.path.insert(0, str(tabula_path))

from theca_procurator.plugins.regex_rename import RegexRenamePlugin


@pytest.fixture
def plugin_with_table():
    """Create a RegexRenamePlugin instance with mocked table."""
    plugin = RegexRenamePlugin()
    
    # Mock receiver
    plugin.receiver = Mock()
    plugin.receiver.main_gui = Mock()
    plugin.receiver.main_gui.notebook = Mock()
    
    # Mock UI components
    plugin.tab_frame = Mock()
    plugin.status_label = Mock()
    plugin.rename_button = Mock()
    plugin.selection_label = Mock()
    
    # Mock table with canvas
    plugin.preview_table = Mock()
    plugin.preview_table.canvas = Mock()
    plugin.preview_table.view = Mock()
    plugin.preview_table.view.canvas = Mock()
    plugin.preview_table.controller = Mock()
    plugin.preview_table.controller.on_click = Mock()
    
    # Initialize selected_rows
    plugin.selected_rows = set()
    
    # Mock found_files
    plugin.found_files = []
    
    # Mock logger
    plugin.logger = Mock()
    
    return plugin


def test_row_selection_single_click(plugin_with_table):
    """Test single click selects a single row."""
    plugin = plugin_with_table
    
    # Setup: Add some files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        file1 = tmppath / "test1.txt"
        file1.touch()
        file2 = tmppath / "test2.txt"
        file2.touch()
        
        plugin.found_files = [
            (file1, "new1.txt"),
            (file2, "new2.txt")
        ]
        
        # Mock event for row 0
        event = Mock()
        event.x = 50
        event.y = 40  # Header is 30, so this is row 0
        event.state = 0  # No Ctrl key
        
        # Mock canvas methods
        plugin.preview_table.canvas.canvasx = Mock(return_value=50)
        plugin.preview_table.canvas.canvasy = Mock(return_value=40)
        plugin.preview_table.canvas.winfo_width = Mock(return_value=800)
        plugin.preview_table.canvas.delete = Mock()
        plugin.preview_table.canvas.create_rectangle = Mock()
        plugin.preview_table.canvas.tag_lower = Mock()
        
        # Execute
        plugin._on_table_click(event)
        
        # Verify
        assert 0 in plugin.selected_rows
        assert len(plugin.selected_rows) == 1


def test_row_selection_ctrl_click_multi_select(plugin_with_table):
    """Test Ctrl+click adds to selection."""
    plugin = plugin_with_table
    
    # Setup: Add some files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        file1 = tmppath / "test1.txt"
        file1.touch()
        file2 = tmppath / "test2.txt"
        file2.touch()
        file3 = tmppath / "test3.txt"
        file3.touch()
        
        plugin.found_files = [
            (file1, "new1.txt"),
            (file2, "new2.txt"),
            (file3, "new3.txt")
        ]
        
        # Mock canvas methods
        plugin.preview_table.canvas.canvasx = Mock(return_value=50)
        plugin.preview_table.canvas.winfo_width = Mock(return_value=800)
        plugin.preview_table.canvas.delete = Mock()
        plugin.preview_table.canvas.create_rectangle = Mock()
        plugin.preview_table.canvas.tag_lower = Mock()
        
        # First click - select row 0
        event1 = Mock()
        event1.x = 50
        event1.y = 40  # Row 0
        event1.state = 0  # No Ctrl
        plugin.preview_table.canvas.canvasy = Mock(return_value=40)
        plugin._on_table_click(event1)
        
        # Second click with Ctrl - add row 2
        event2 = Mock()
        event2.x = 50
        event2.y = 90  # Row 2 (30 header + 25*2 + some)
        event2.state = 0x0004  # Ctrl key
        plugin.preview_table.canvas.canvasy = Mock(return_value=90)
        plugin._on_table_click(event2)
        
        # Verify both rows selected
        assert 0 in plugin.selected_rows
        assert 2 in plugin.selected_rows
        assert len(plugin.selected_rows) == 2


def test_row_selection_ctrl_click_toggle(plugin_with_table):
    """Test Ctrl+click on selected row deselects it."""
    plugin = plugin_with_table
    
    # Setup
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        file1 = tmppath / "test1.txt"
        file1.touch()
        
        plugin.found_files = [(file1, "new1.txt")]
        plugin.selected_rows = {0}  # Already selected
        
        # Mock canvas methods
        plugin.preview_table.canvas.canvasx = Mock(return_value=50)
        plugin.preview_table.canvas.canvasy = Mock(return_value=40)
        plugin.preview_table.canvas.winfo_width = Mock(return_value=800)
        plugin.preview_table.canvas.delete = Mock()
        plugin.preview_table.canvas.create_rectangle = Mock()
        plugin.preview_table.canvas.tag_lower = Mock()
        
        # Ctrl+click on already selected row
        event = Mock()
        event.x = 50
        event.y = 40
        event.state = 0x0004  # Ctrl key
        
        plugin._on_table_click(event)
        
        # Verify row deselected
        assert 0 not in plugin.selected_rows
        assert len(plugin.selected_rows) == 0


def test_row_selection_ignores_header_click(plugin_with_table):
    """Test clicking on header doesn't select anything."""
    plugin = plugin_with_table
    
    # Setup
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        file1 = tmppath / "test1.txt"
        file1.touch()
        
        plugin.found_files = [(file1, "new1.txt")]
        
        # Mock canvas methods
        plugin.preview_table.canvas.canvasx = Mock(return_value=50)
        plugin.preview_table.canvas.canvasy = Mock(return_value=15)  # In header (< 30)
        
        # Click on header
        event = Mock()
        event.x = 50
        event.y = 15
        event.state = 0
        
        plugin._on_table_click(event)
        
        # Verify nothing selected
        assert len(plugin.selected_rows) == 0


def test_row_selection_ignores_invalid_row(plugin_with_table):
    """Test clicking beyond valid rows doesn't select anything."""
    plugin = plugin_with_table
    
    # Setup - only 1 file
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        file1 = tmppath / "test1.txt"
        file1.touch()
        
        plugin.found_files = [(file1, "new1.txt")]
        
        # Mock canvas methods
        plugin.preview_table.canvas.canvasx = Mock(return_value=50)
        plugin.preview_table.canvas.canvasy = Mock(return_value=200)  # Way beyond row 0
        
        # Click on non-existent row
        event = Mock()
        event.x = 50
        event.y = 200
        event.state = 0
        
        plugin._on_table_click(event)
        
        # Verify nothing selected
        assert len(plugin.selected_rows) == 0


def test_selection_highlighting_draws_rectangles(plugin_with_table):
    """Test that selection highlighting draws blue rectangles."""
    plugin = plugin_with_table
    
    # Setup
    plugin.selected_rows = {0, 2}
    
    # Mock canvas methods
    plugin.preview_table.view.canvas.delete = Mock()
    plugin.preview_table.view.canvas.winfo_width = Mock(return_value=800)
    plugin.preview_table.view.canvas.create_rectangle = Mock()
    plugin.preview_table.view.canvas.tag_lower = Mock()
    
    # Execute
    plugin._redraw_table_selection()
    
    # Verify
    plugin.preview_table.view.canvas.delete.assert_called_once_with('selection_highlight')
    assert plugin.preview_table.view.canvas.create_rectangle.call_count == 2
    
    # Check that rectangles were created with light blue fill
    calls = plugin.preview_table.view.canvas.create_rectangle.call_args_list
    for call in calls:
        kwargs = call[1]
        assert kwargs['fill'] == '#ADD8E6'  # Light blue
        assert kwargs['tags'] == 'selection_highlight'


def test_wrapper_calls_both_handlers(plugin_with_table):
    """Test that wrapper calls both selection and original handlers."""
    plugin = plugin_with_table
    
    # Setup
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        file1 = tmppath / "test1.txt"
        file1.touch()
        
        plugin.found_files = [(file1, "new1.txt")]
        plugin._original_click_handler = Mock()
        
        # Mock canvas methods
        plugin.preview_table.canvas.canvasx = Mock(return_value=50)
        plugin.preview_table.canvas.canvasy = Mock(return_value=40)
        plugin.preview_table.canvas.winfo_width = Mock(return_value=800)
        plugin.preview_table.canvas.delete = Mock()
        plugin.preview_table.canvas.create_rectangle = Mock()
        plugin.preview_table.canvas.tag_lower = Mock()
        
        event = Mock()
        event.x = 50
        event.y = 40
        event.state = 0
        
        # Execute
        plugin._on_table_click_wrapper(event)
        
        # Verify both handlers called
        assert 0 in plugin.selected_rows  # Selection happened
        plugin._original_click_handler.assert_called_once_with(event)


def test_select_all_rows(plugin_with_table):
    """Test Select All Rows button selects all rows."""
    plugin = plugin_with_table
    
    # Setup: Add some files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        file1 = tmppath / "test1.txt"
        file1.touch()
        file2 = tmppath / "test2.txt"
        file2.touch()
        file3 = tmppath / "test3.txt"
        file3.touch()
        
        plugin.found_files = [
            (file1, "new1.txt"),
            (file2, "new2.txt"),
            (file3, "new3.txt")
        ]
        
        # Mock canvas methods
        plugin.preview_table.view.canvas.delete = Mock()
        plugin.preview_table.view.canvas.winfo_width = Mock(return_value=800)
        plugin.preview_table.view.canvas.create_rectangle = Mock()
        plugin.preview_table.view.canvas.tag_lower = Mock()
        
        # Execute
        plugin._select_all_rows()
        
        # Verify all rows selected
        assert len(plugin.selected_rows) == 3
        assert 0 in plugin.selected_rows
        assert 1 in plugin.selected_rows
        assert 2 in plugin.selected_rows
        
        # Verify selection label updated
        plugin.selection_label.configure.assert_called_with(text="3 rows selected")


def test_clear_selection(plugin_with_table):
    """Test Clear Selection button clears all selections."""
    plugin = plugin_with_table
    
    # Setup: Pre-select some rows
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        file1 = tmppath / "test1.txt"
        file1.touch()
        file2 = tmppath / "test2.txt"
        file2.touch()
        
        plugin.found_files = [
            (file1, "new1.txt"),
            (file2, "new2.txt")
        ]
        plugin.selected_rows = {0, 1}
        
        # Mock canvas methods
        plugin.preview_table.view.canvas.delete = Mock()
        plugin.preview_table.view.canvas.winfo_width = Mock(return_value=800)
        plugin.preview_table.view.canvas.create_rectangle = Mock()
        plugin.preview_table.view.canvas.tag_lower = Mock()
        
        # Execute
        plugin._clear_selection()
        
        # Verify all selections cleared
        assert len(plugin.selected_rows) == 0
        
        # Verify selection label updated
        plugin.selection_label.configure.assert_called_with(text="0 rows selected")


def test_update_selection_label_counts(plugin_with_table):
    """Test selection label shows correct counts."""
    plugin = plugin_with_table
    
    # Test 0 rows
    plugin.selected_rows = set()
    plugin._update_selection_label()
    plugin.selection_label.configure.assert_called_with(text="0 rows selected")
    
    # Test 1 row
    plugin.selected_rows = {0}
    plugin._update_selection_label()
    plugin.selection_label.configure.assert_called_with(text="1 row selected")
    
    # Test multiple rows
    plugin.selected_rows = {0, 1, 2, 3}
    plugin._update_selection_label()
    plugin.selection_label.configure.assert_called_with(text="4 rows selected")


def test_select_all_with_no_files(plugin_with_table):
    """Test Select All does nothing when no files present."""
    plugin = plugin_with_table
    
    plugin.found_files = []
    plugin.selected_rows = set()
    
    # Execute
    plugin._select_all_rows()
    
    # Verify nothing selected
    assert len(plugin.selected_rows) == 0

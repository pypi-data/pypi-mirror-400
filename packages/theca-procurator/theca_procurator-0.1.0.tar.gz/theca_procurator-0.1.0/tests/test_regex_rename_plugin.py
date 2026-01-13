"""
Unit tests for Regex Rename plugin.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
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
def plugin():
    """Create a RegexRenamePlugin instance with mocked UI components."""
    plugin = RegexRenamePlugin()
    
    # Mock receiver
    plugin.receiver = Mock()
    plugin.receiver.main_gui = Mock()
    plugin.receiver.main_gui.notebook = Mock()
    
    # Mock UI components with Mock objects instead of real tkinter
    plugin.tab_frame = Mock()
    plugin.target_folder_var = Mock()
    plugin.prefix_type_var = Mock()
    plugin.prefix_value_var = Mock()
    plugin.prefix_start_var = Mock()
    plugin.prefix_increment_var = Mock()
    plugin.prefix_padding_var = Mock()
    plugin.separator_var = Mock()
    plugin.regex_find_var = Mock()
    plugin.regex_replace_var = Mock()
    plugin.suffix_type_var = Mock()
    plugin.suffix_value_var = Mock()
    plugin.suffix_start_var = Mock()
    plugin.suffix_increment_var = Mock()
    plugin.suffix_padding_var = Mock()
    plugin.status_label = Mock()
    plugin.rename_button = Mock()
    plugin.preview_table = Mock()
    plugin.progress_bar = Mock()
    plugin.progress_label = Mock()
    plugin.filter_regex_var = Mock()
    plugin.selection_label = Mock()
    
    # Initialize selected_rows set
    plugin.selected_rows = set()
    
    return plugin


def test_plugin_initialization():
    """Test plugin initializes with correct attributes."""
    plugin = RegexRenamePlugin()
    
    assert plugin.tab_frame is None
    assert plugin.receiver is None
    assert plugin.found_files == []
    assert plugin.full_paths == {}


def test_get_ready(plugin):
    """Test get_ready method sets receiver."""
    receiver = Mock()
    plugin.get_ready(receiver)
    
    assert plugin.receiver == receiver


def test_generate_new_names_with_literal_prefix_suffix(plugin):
    """Test generating new names with literal prefix and suffix."""
    # Setup
    plugin.prefix_type_var.get.return_value = "literal"
    plugin.prefix_value_var.get.return_value = "PRE"
    plugin.prefix_start_var.get.return_value = "0"
    plugin.prefix_increment_var.get.return_value = "1"
    plugin.prefix_padding_var.get.return_value = "0"
    plugin.suffix_type_var.get.return_value = "literal"
    plugin.suffix_value_var.get.return_value = "SUF"
    plugin.suffix_start_var.get.return_value = "0"
    plugin.suffix_increment_var.get.return_value = "1"
    plugin.suffix_padding_var.get.return_value = "0"
    plugin.separator_var.get.return_value = "_"
    plugin.regex_find_var.get.return_value = ""
    plugin.regex_replace_var.get.return_value = ""
    
    # Create temp files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        file1 = tmppath / "test1.txt"
        file1.touch()
        file2 = tmppath / "test2.txt"
        file2.touch()
        
        files = [file1, file2]
        
        # Execute
        result = plugin._generate_new_names(files)
        
        # Verify
        assert len(result) == 2
        assert result[0] == (file1, "PRE_test1_SUF.txt")
        assert result[1] == (file2, "PRE_test2_SUF.txt")


def test_generate_new_names_with_sequential_prefix(plugin):
    """Test generating new names with sequential prefix."""
    # Setup
    plugin.prefix_type_var.get.return_value = "sequential"
    plugin.prefix_start_var.get.return_value = "1"
    plugin.prefix_increment_var.get.return_value = "1"
    plugin.prefix_padding_var.get.return_value = "3"
    plugin.prefix_value_var.get.return_value = ""
    plugin.suffix_type_var.get.return_value = "literal"
    plugin.suffix_value_var.get.return_value = ""
    plugin.suffix_start_var.get.return_value = "0"
    plugin.suffix_increment_var.get.return_value = "1"
    plugin.suffix_padding_var.get.return_value = "0"
    plugin.separator_var.get.return_value = "_"
    plugin.regex_find_var.get.return_value = ""
    plugin.regex_replace_var.get.return_value = ""
    
    # Create temp files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        file1 = tmppath / "photo.jpg"
        file1.touch()
        file2 = tmppath / "photo.jpg"
        file2 = tmppath / "photo2.jpg"
        file2.touch()
        
        files = [file1, file2]
        
        # Execute
        result = plugin._generate_new_names(files)
        
        # Verify
        assert len(result) == 2
        assert result[0] == (file1, "001_photo.jpg")
        assert result[1] == (file2, "002_photo2.jpg")


def test_generate_new_names_with_regex_replacement(plugin):
    """Test generating new names with regex find/replace."""
    # Setup
    plugin.prefix_type_var.get.return_value = "literal"
    plugin.prefix_value_var.get.return_value = ""
    plugin.prefix_start_var.get.return_value = "0"
    plugin.prefix_increment_var.get.return_value = "1"
    plugin.prefix_padding_var.get.return_value = "0"
    plugin.suffix_type_var.get.return_value = "literal"
    plugin.suffix_value_var.get.return_value = ""
    plugin.suffix_start_var.get.return_value = "0"
    plugin.suffix_increment_var.get.return_value = "1"
    plugin.suffix_padding_var.get.return_value = "0"
    plugin.separator_var.get.return_value = "_"
    plugin.regex_find_var.get.return_value = r"IMG_(\d+)"
    plugin.regex_replace_var.get.return_value = r"Photo_\1"
    
    # Create temp files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        file1 = tmppath / "IMG_1234.jpg"
        file1.touch()
        file2 = tmppath / "IMG_5678.jpg"
        file2.touch()
        
        files = [file1, file2]
        
        # Execute
        result = plugin._generate_new_names(files)
        
        # Verify
        assert len(result) == 2
        assert result[0] == (file1, "Photo_1234.jpg")
        assert result[1] == (file2, "Photo_5678.jpg")


def test_generate_new_names_complex_pattern(plugin):
    """Test generating new names with complex prefix/suffix/regex pattern."""
    # Setup
    plugin.prefix_type_var.get.return_value = "sequential"
    plugin.prefix_start_var.get.return_value = "10"
    plugin.prefix_increment_var.get.return_value = "5"
    plugin.prefix_padding_var.get.return_value = "4"
    plugin.prefix_value_var.get.return_value = ""
    plugin.suffix_type_var.get.return_value = "literal"
    plugin.suffix_value_var.get.return_value = "2026"
    plugin.suffix_start_var.get.return_value = "0"
    plugin.suffix_increment_var.get.return_value = "1"
    plugin.suffix_padding_var.get.return_value = "0"
    plugin.separator_var.get.return_value = "-"
    plugin.regex_find_var.get.return_value = r"doc"
    plugin.regex_replace_var.get.return_value = "document"
    
    # Create temp files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        file1 = tmppath / "doc1.pdf"
        file1.touch()
        file2 = tmppath / "doc2.pdf"
        file2.touch()
        
        files = [file1, file2]
        
        # Execute
        result = plugin._generate_new_names(files)
        
        # Verify
        assert len(result) == 2
        assert result[0] == (file1, "0010-document1-2026.pdf")
        assert result[1] == (file2, "0015-document2-2026.pdf")


def test_generate_new_names_with_sequential_suffix(plugin):
    """Test generating new names with sequential suffix."""
    # Setup
    plugin.prefix_type_var.get.return_value = "literal"
    plugin.prefix_value_var.get.return_value = "file"
    plugin.prefix_start_var.get.return_value = "0"
    plugin.prefix_increment_var.get.return_value = "1"
    plugin.prefix_padding_var.get.return_value = "0"
    plugin.suffix_type_var.get.return_value = "sequential"
    plugin.suffix_start_var.get.return_value = "100"
    plugin.suffix_increment_var.get.return_value = "10"
    plugin.suffix_padding_var.get.return_value = "5"
    plugin.separator_var.get.return_value = "_"
    plugin.regex_find_var.get.return_value = ""
    plugin.regex_replace_var.get.return_value = ""
    
    # Create temp files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        file1 = tmppath / "data.csv"
        file1.touch()
        file2 = tmppath / "data.csv"
        file2 = tmppath / "info.csv"
        file2.touch()
        
        files = [file1, file2]
        
        # Execute
        result = plugin._generate_new_names(files)
        
        # Verify
        assert len(result) == 2
        assert result[0] == (file1, "file_data_00100.csv")
        assert result[1] == (file2, "file_info_00110.csv")


def test_generate_preview_with_no_files(plugin):
    """Test preview generation with no files."""
    plugin.found_files = []
    
    # Execute
    plugin._generate_preview()
    
    # Verify
    plugin.preview_table.set_data.assert_called_once()
    args = plugin.preview_table.set_data.call_args[0]
    assert args[0] == [['No files found to rename', '', '']]


def test_generate_preview_with_files(plugin):
    """Test preview generation with files."""
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
        
        # Mock the table style provider
        plugin.preview_table.style_provider = Mock()
        plugin.preview_table.style_provider.base_styles = {
            'default': Mock(col_width=100),
            'header': Mock(col_width=100)
        }
        plugin.preview_table.refresh = Mock()
        plugin.preview_table.view = Mock()
        plugin.preview_table.view.canvas = Mock()
        
        # Execute
        plugin._generate_preview()
        
        # Verify
        plugin.preview_table.set_data.assert_called_once()
        args = plugin.preview_table.set_data.call_args[0]
        data = args[0]
        headers = args[1]
        
        assert len(data) == 2
        assert data[0][1] == "test1.txt"
        assert data[0][2] == "new1.txt"
        assert data[1][1] == "test2.txt"
        assert data[1][2] == "new2.txt"
        assert headers == ['File Path', 'Old Name', 'New Name']
        
        # Verify full paths stored for tooltips
        assert len(plugin.full_paths) == 2


def test_update_prefix_state_sequential(plugin):
    """Test prefix state updates when sequential is selected."""
    plugin.prefix_type_var.get.return_value = "sequential"
    plugin.prefix_start_entry = Mock()
    plugin.prefix_increment_entry = Mock()
    plugin.prefix_padding_entry = Mock()
    plugin.prefix_value_entry = Mock()
    
    # Execute
    plugin._update_prefix_state()
    
    # Verify
    plugin.prefix_start_entry.configure.assert_called_with(state='normal')
    plugin.prefix_increment_entry.configure.assert_called_with(state='normal')
    plugin.prefix_padding_entry.configure.assert_called_with(state='normal')
    plugin.prefix_value_entry.configure.assert_called_with(state='disabled')


def test_update_prefix_state_literal(plugin):
    """Test prefix state updates when literal is selected."""
    plugin.prefix_type_var.get.return_value = "literal"
    plugin.prefix_start_entry = Mock()
    plugin.prefix_increment_entry = Mock()
    plugin.prefix_padding_entry = Mock()
    plugin.prefix_value_entry = Mock()
    
    # Execute
    plugin._update_prefix_state()
    
    # Verify
    plugin.prefix_start_entry.configure.assert_called_with(state='disabled')
    plugin.prefix_increment_entry.configure.assert_called_with(state='disabled')
    plugin.prefix_padding_entry.configure.assert_called_with(state='disabled')
    plugin.prefix_value_entry.configure.assert_called_with(state='normal')


def test_generate_preview_sets_table_data(plugin):
    """Test that _generate_preview calls set_data on preview_table."""
    # Setup
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        file1 = tmppath / "test1.txt"
        file1.touch()
        
        plugin.found_files = [(file1, "new_test1.txt")]
        
        # Mock the table style provider
        plugin.preview_table.style_provider = Mock()
        plugin.preview_table.style_provider.base_styles = {
            'default': Mock(col_width=100),
            'header': Mock(col_width=100)
        }
        plugin.preview_table.refresh = Mock()
        plugin.preview_table.view = Mock()
        plugin.preview_table.view.canvas = Mock()
        
        # Execute
        plugin._generate_preview()
        
        # Verify set_data was called
        plugin.preview_table.set_data.assert_called_once()
        args = plugin.preview_table.set_data.call_args[0]
        data = args[0]
        headers = args[1]
        
        assert headers == ['File Path', 'Old Name', 'New Name']
        assert len(data) == 1
        assert data[0][1] == "test1.txt"
        assert data[0][2] == "new_test1.txt"


def test_generate_preview_sets_column_widths(plugin):
    """Test that _generate_preview sets column widths based on content."""
    # Setup
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        file1 = tmppath / "short.txt"
        file1.touch()
        file2 = tmppath / "very_long_filename_that_should_expand_column.txt"
        file2.touch()
        
        plugin.found_files = [
            (file1, "new1.txt"),
            (file2, "new_very_long_filename.txt")
        ]
        
        # Mock the table style provider
        plugin.preview_table.style_provider = Mock()
        plugin.preview_table.style_provider.base_styles = {
            'default': Mock(col_width=100),
            'header': Mock(col_width=100)
        }
        plugin.preview_table.refresh = Mock()
        plugin.preview_table.view = Mock()
        plugin.preview_table.view.canvas = Mock()
        
        # Execute
        plugin._generate_preview()
        
        # Verify refresh was called
        plugin.preview_table.refresh.assert_called_once()


def test_generate_preview_stores_full_paths_for_tooltips(plugin):
    """Test that _generate_preview stores full paths in full_paths dict."""
    # Setup
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
        
        # Mock the table style provider
        plugin.preview_table.style_provider = Mock()
        plugin.preview_table.style_provider.base_styles = {
            'default': Mock(col_width=100),
            'header': Mock(col_width=100)
        }
        plugin.preview_table.refresh = Mock()
        plugin.preview_table.view = Mock()
        plugin.preview_table.view.canvas = Mock()
        
        # Execute
        plugin._generate_preview()
        
        # Verify full_paths dictionary was populated
        assert len(plugin.full_paths) == 2
        assert 0 in plugin.full_paths
        assert 1 in plugin.full_paths
        assert str(tmppath) in plugin.full_paths[0]
        assert str(tmppath) in plugin.full_paths[1]


def test_generate_preview_with_empty_files_list(plugin):
    """Test _generate_preview handles empty files list correctly."""
    # Setup
    plugin.found_files = []
    
    # Mock the table view
    plugin.preview_table.view = Mock()
    
    # Execute
    plugin._generate_preview()
    
    # Verify set_data was called with "No files found" message
    plugin.preview_table.set_data.assert_called_once()
    args = plugin.preview_table.set_data.call_args[0]
    data = args[0]
    
    assert data == [['No files found to rename', '', '']]


def test_execute_rename_requires_selection(plugin):
    """Test that _execute_rename flashes warning when no files selected."""
    # Setup
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        file1 = tmppath / "test.txt"
        file1.touch()
        
        plugin.found_files = [(file1, "new_test.txt")]
        plugin.selected_rows = set()  # No rows selected
        
        # Mock the flash warning method
        plugin._flash_status_warning = Mock()
        
        # Execute
        plugin._execute_rename()
        
        # Verify flash warning was called
        plugin._flash_status_warning.assert_called_once()
        call_args = plugin._flash_status_warning.call_args[0]
        assert "No files selected" in call_args[0]


def test_execute_rename_processes_only_selected_files(plugin):
    """Test that _execute_rename only processes selected files."""
    # Setup
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
        
        # Select only indices 0 and 2 (file1 and file3)
        plugin.selected_rows = {0, 2}
        
        # Execute with mocked messagebox
        with patch('theca_procurator.plugins.regex_rename.messagebox') as mock_mb:
            mock_mb.askyesno.return_value = True
            
            plugin._execute_rename()
            
            # Verify confirmation dialog shows correct count
            mock_mb.askyesno.assert_called_once()
            call_args = mock_mb.askyesno.call_args[0]
            assert "2 selected files" in call_args[1]
            
            # Verify only selected files were renamed
            assert file1.exists() is False  # Renamed
            assert (tmppath / "new1.txt").exists()
            assert file2.exists()  # Not selected, not renamed
            assert file3.exists() is False  # Renamed
            assert (tmppath / "new3.txt").exists()

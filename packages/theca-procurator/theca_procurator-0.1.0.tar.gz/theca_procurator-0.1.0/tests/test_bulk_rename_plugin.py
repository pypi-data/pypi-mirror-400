"""Tests for the Bulk Rename plugin."""

import sys
from pathlib import Path

# Add local packages to path for testing
_test_dir = Path(__file__).parent
_main_dir = _test_dir.parent
_python_dir = _main_dir.parent
_local_packages = _python_dir / "Local Packages"

for pkg_dir in ["Extensio Pulchra Skinny/Code/Python",
                "Tabula Mutabilis",
                "Vultus Serpentis"]:
    pkg_path = str(_local_packages / pkg_dir)
    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

import pytest
from unittest.mock import Mock
from theca_procurator.plugins.bulk_rename import BulkRenamePlugin


class TestBulkRenamePlugin:
    """Test suite for BulkRenamePlugin."""

    @pytest.fixture
    def plugin(self):
        """Create a BulkRenamePlugin instance for testing."""
        plugin = BulkRenamePlugin()
        plugin.logger = Mock()
        plugin.preview_table = Mock()
        plugin.status_label = Mock()
        plugin.rename_button = Mock()
        plugin.found_files = []
        return plugin

    def test_get_delimiter_multi_char(self, plugin):
        """Test delimiter parsing for multi-character strings."""
        plugin.delimiter_var = Mock()
        plugin.delimiter_var.get.return_value = '::'
        assert plugin._get_delimiter() == '::'

    def test_parse_import_file_multi_char_delimiter(self, plugin, tmp_path):
        """Test parsing import file with multi-character delimiter."""
        plugin.delimiter_var = Mock()
        plugin.delimiter_var.get.return_value = '::'
        test_file = tmp_path / "test.txt"
        test_file.write_text("old1.txt::new1.txt\nold2.txt::new2.txt\n")
        mappings = plugin._parse_import_file(test_file)
        assert len(mappings) == 2
        assert mappings[0] == ('old1.txt', 'new1.txt')

    def test_generate_preview_uses_set_data(self, plugin):
        """Test that _generate_preview uses set_data method."""
        plugin.found_files = [(Path('/test/file1.txt'), 'new1.txt')]
        plugin._generate_preview()
        assert plugin.preview_table.set_data.called
        call_args = plugin.preview_table.set_data.call_args
        headers = call_args[0][1]
        assert headers == ['File Path', 'Old Name', 'New Name']

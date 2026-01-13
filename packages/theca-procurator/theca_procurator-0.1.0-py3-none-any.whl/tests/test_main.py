"""
Basic smoke tests for Theca Procurator main module.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add theca_procurator to path
_main_dir = Path(__file__).parent.parent
if str(_main_dir) not in sys.path:
    sys.path.insert(0, str(_main_dir))


def test_imports() -> None:
    """Test that basic imports work."""
    import theca_procurator
    assert theca_procurator.__version__ == "0.1.0"


def test_program_initialization() -> None:
    """Test Program class can be instantiated."""
    # Mock ttkbootstrap to avoid GUI creation
    with patch('theca_procurator.main.ttk.Window') as mock_window:
        mock_root = MagicMock()
        mock_window.return_value = mock_root
        
        from theca_procurator.main import Program
        
        # Create program instance
        program = Program()
        
        # Verify basic initialization
        assert program.event_bus is not None
        assert program.command_manager is not None
        assert program.bucket is not None
        assert program.plugin_manager is not None


def test_config_loading() -> None:
    """Test configuration loading."""
    with patch('theca_procurator.main.ttk.Window'):
        from theca_procurator.main import Program
        
        program = Program()
        
        # Verify config loaded
        assert program.config is not None
        
        # Check that max_undo_steps is read from config
        max_undo = program.config.get_setting('operations.max_undo_steps', 10)
        assert max_undo == 10

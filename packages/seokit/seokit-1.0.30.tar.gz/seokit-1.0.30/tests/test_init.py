"""Tests for seokit/__init__.py helper functions."""
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from seokit import (
    SEOKIT_COMMAND_PREFIXES,
    __version__,
    _cleanup_obsolete_commands,
    _cleanup_obsolete_scripts,
    _create_venv,
    _install_commands,
    _install_docs,
    _install_scripts,
    _is_setup_complete,
    _print_update_banner,
    _update_checklists,
)

# =============================================================================
# Module Import Tests
# =============================================================================

class TestModuleImports:
    """Verify all helper functions are importable."""

    def test_module_imports(self):
        """Verify all helper functions are importable."""
        assert _print_update_banner is not None
        assert _update_checklists is not None
        assert _cleanup_obsolete_commands is not None
        assert _install_commands is not None
        assert _install_scripts is not None
        assert _create_venv is not None
        assert _install_docs is not None
        assert _cleanup_obsolete_scripts is not None
        assert _is_setup_complete is not None
        assert SEOKIT_COMMAND_PREFIXES is not None
        assert __version__ is not None

    def test_seokit_command_prefixes(self):
        """Verify SEOKIT_COMMAND_PREFIXES contains expected values."""
        expected = (
            'search-intent', 'top-article', 'create-outline',
            'optimize-outline', 'write-seo', 'seokit-init', 'internal-link'
        )
        assert expected == SEOKIT_COMMAND_PREFIXES

    def test_version_format(self):
        """Verify version string is valid semver format."""
        parts = __version__.split('.')
        assert len(parts) == 3
        for part in parts:
            assert part.isdigit()


# =============================================================================
# _print_update_banner() Tests
# =============================================================================

class TestPrintUpdateBanner:
    """Tests for _print_update_banner()."""

    def test_print_update_banner_displays_box(self, capsys):
        """Verify banner displays correctly with box borders."""
        _print_update_banner()
        captured = capsys.readouterr()
        assert "╭───────────────────────────────╮" in captured.out
        assert "│      SEOKit Updating...       │" in captured.out
        assert "╰───────────────────────────────╯" in captured.out


# =============================================================================
# _install_commands() Tests
# =============================================================================

class TestInstallCommands:
    """Tests for _install_commands()."""

    def test_install_commands_success(self, mock_claude_dir, mocker):
        """Test successful command installation copies files correctly."""
        mocker.patch('seokit.config.get_commands_dir', return_value=mock_claude_dir / 'commands')

        # Source commands should exist
        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'commands'
        if not src.exists():
            pytest.skip("Source commands directory not found")

        # Call the actual function
        _install_commands()

        # Verify commands were copied
        commands_dir = mock_claude_dir / 'commands'
        assert commands_dir.exists()
        copied_files = list(commands_dir.glob('*.md'))
        assert len(copied_files) > 0
        # Verify at least one known command exists
        assert any('search-intent' in f.name or 'write-seo' in f.name for f in copied_files)

    def test_install_commands_no_source_dir(self, mock_home, mocker):
        """Test graceful handling when source commands dir doesn't exist."""
        mocker.patch('seokit.config.get_commands_dir', return_value=mock_home / '.claude' / 'commands')

        # Create a fake empty source package without commands dir
        fake_pkg = mock_home / 'empty_pkg'
        fake_pkg.mkdir(parents=True)

        # Mock the __file__ path to point to fake package
        import seokit
        original_file = seokit.__file__

        # Temporarily override Path(__file__).parent / 'commands' to not exist
        with patch.object(seokit, '__file__', str(fake_pkg / '__init__.py')):
            # The function checks if commands_src.exists() and returns early if not
            # Since fake_pkg/commands doesn't exist, function should return without error
            _install_commands()

        # Should complete without error - verify no commands dir was created
        commands_dest = mock_home / '.claude' / 'commands'
        # Either doesn't exist or is empty (since source doesn't exist)
        if commands_dest.exists():
            assert len(list(commands_dest.glob('*.md'))) == 0

    def test_install_commands_mkdir_permission_error(self, mock_home, mocker):
        """Test PermissionError when creating commands directory."""
        mocker.patch('seokit.config.get_commands_dir', return_value=mock_home / '.claude' / 'commands')

        # Create source commands
        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'commands'
        if not src.exists():
            pytest.skip("Source commands directory not found")

        # Mock mkdir to raise PermissionError
        with patch.object(Path, 'mkdir', side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError) as exc_info:
                _install_commands()
            assert "INIT_COMMANDS_MKDIR_PERMISSION" in str(exc_info.value)

    def test_install_commands_copy_permission_error(self, mock_claude_dir, mocker):
        """Test PermissionError when copying command file."""
        mocker.patch('seokit.config.get_commands_dir', return_value=mock_claude_dir / 'commands')

        # Source exists, but copy fails
        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'commands'
        if not src.exists():
            pytest.skip("Source commands directory not found")

        with patch('shutil.copy2', side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError) as exc_info:
                _install_commands()
            assert "INIT_COMMANDS_COPY_PERMISSION" in str(exc_info.value)


# =============================================================================
# _install_scripts() Tests
# =============================================================================

class TestInstallScripts:
    """Tests for _install_scripts()."""

    def test_install_scripts_success(self, mock_claude_dir, mocker):
        """Test successful script installation."""
        scripts_dest = mock_claude_dir / 'seokit' / 'scripts'
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_claude_dir / 'seokit')

        # Source exists, copy should work
        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'scripts'
        if not src.exists():
            pytest.skip("Source scripts directory not found")

        result = _install_scripts()

        assert result is True or result is None  # Returns True on success
        assert scripts_dest.exists()

    def test_install_scripts_no_source_dir(self, mock_home, mocker):
        """Test returns False when source scripts dir doesn't exist."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_home / '.claude' / 'seokit')

        # Create a fake empty source package without scripts dir
        import seokit
        fake_pkg = mock_home / 'empty_pkg'
        fake_pkg.mkdir(parents=True)

        with patch.object(seokit, '__file__', str(fake_pkg / '__init__.py')):
            # Function should return False when source doesn't exist
            result = _install_scripts()
            assert result is False

    def test_install_scripts_mkdir_permission_error(self, mock_home, mocker):
        """Test PermissionError when creating scripts directory."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_home / '.claude' / 'seokit')

        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'scripts'
        if not src.exists():
            pytest.skip("Source scripts directory not found")

        # First mkdir for seokit_data succeeds, second for scripts fails
        original_mkdir = Path.mkdir
        call_count = [0]

        def mock_mkdir(self, *args, **kwargs):
            call_count[0] += 1
            if call_count[0] > 1:  # Fail on scripts dir creation
                raise PermissionError("Access denied")
            return original_mkdir(self, *args, **kwargs)

        with patch.object(Path, 'mkdir', mock_mkdir):
            with pytest.raises(PermissionError) as exc_info:
                _install_scripts()
            assert "INIT_SCRIPTS_MKDIR_PERMISSION" in str(exc_info.value)

    def test_install_scripts_copy_permission_error(self, mock_claude_dir, mocker):
        """Test PermissionError when copying script file."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_claude_dir / 'seokit')

        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'scripts'
        if not src.exists():
            pytest.skip("Source scripts directory not found")

        with patch('shutil.copy2', side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError) as exc_info:
                _install_scripts()
            assert "INIT_SCRIPTS_COPY_PERMISSION" in str(exc_info.value)


# =============================================================================
# _create_venv() Tests
# =============================================================================

class TestCreateVenv:
    """Tests for _create_venv()."""

    def test_create_venv_already_exists(self, mock_claude_dir, mocker):
        """Test venv creation skipped when already exists."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_claude_dir / 'seokit')

        venv_path = mock_claude_dir / 'seokit' / 'venv'
        venv_path.mkdir(parents=True)

        result = _create_venv()

        assert result is True

    def test_create_venv_success(self, mock_claude_dir, mocker):
        """Test successful venv creation with correct subprocess arguments."""
        import sys

        seokit_dir = mock_claude_dir / 'seokit'
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=seokit_dir)

        mock_run = mocker.patch('seokit.subprocess.run')
        mock_run.return_value = MagicMock(returncode=0, stdout=b'', stderr=b'')

        # Mock pip existence (cross-platform)
        venv_path = seokit_dir / 'venv'
        if sys.platform == 'win32':
            pip_path = venv_path / 'Scripts' / 'pip.exe'
        else:
            pip_path = venv_path / 'bin' / 'pip'

        # Track calls and create pip after venv creation
        calls = []

        def side_effect(*args, **kwargs):
            calls.append(args[0])
            if 'venv' in str(args[0]):
                venv_path.mkdir(parents=True, exist_ok=True)
                pip_path.parent.mkdir(parents=True, exist_ok=True)
                pip_path.write_text('')
            return MagicMock(returncode=0, stdout=b'', stderr=b'')

        mock_run.side_effect = side_effect

        result = _create_venv()

        assert result is True
        assert mock_run.call_count == 2  # venv creation + pip install

        # Verify venv creation call arguments
        venv_call = calls[0]
        assert sys.executable in venv_call  # Check list membership directly
        assert '-m' in venv_call
        assert 'venv' in venv_call
        assert str(venv_path) in venv_call

        # Verify pip install call arguments
        pip_call = calls[1]
        assert any('pip' in str(arg) for arg in pip_call)

    def test_create_venv_subprocess_error(self, mock_claude_dir, mocker):
        """Test CalledProcessError during venv creation."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_claude_dir / 'seokit')

        mock_run = mocker.patch('seokit.subprocess.run')
        mock_run.side_effect = subprocess.CalledProcessError(1, 'python', stderr=b'error')

        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            _create_venv()
        assert "INIT_VENV_CREATE_FAILED" in str(exc_info.value.stderr)

    def test_create_venv_timeout(self, mock_claude_dir, mocker):
        """Test TimeoutExpired during venv creation."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_claude_dir / 'seokit')

        mock_run = mocker.patch('seokit.subprocess.run')
        mock_run.side_effect = subprocess.TimeoutExpired('python', 120)

        with pytest.raises(subprocess.TimeoutExpired) as exc_info:
            _create_venv()
        assert exc_info.value.timeout == 120

    def test_create_venv_pip_not_found(self, mock_claude_dir, mocker):
        """Test FileNotFoundError when pip not found after venv creation."""
        seokit_dir = mock_claude_dir / 'seokit'
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=seokit_dir)

        mock_run = mocker.patch('seokit.subprocess.run')

        # First call succeeds (venv creation), but pip doesn't exist
        def side_effect(*args, **kwargs):
            if 'venv' in str(args[0]):
                # Create venv dir but NOT pip
                (seokit_dir / 'venv').mkdir(parents=True, exist_ok=True)
            return MagicMock(returncode=0, stdout=b'', stderr=b'')

        mock_run.side_effect = side_effect

        with pytest.raises(FileNotFoundError) as exc_info:
            _create_venv()
        assert "INIT_VENV_PIP_NOT_FOUND" in str(exc_info.value)


# =============================================================================
# _is_setup_complete() Tests
# =============================================================================

class TestIsSetupComplete:
    """Tests for _is_setup_complete()."""

    def test_setup_complete_true(self, mock_claude_dir, mocker):
        """Test returns True when both scripts and venv exist."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_claude_dir / 'seokit')

        seokit_dir = mock_claude_dir / 'seokit'
        (seokit_dir / 'scripts').mkdir(parents=True)
        (seokit_dir / 'venv').mkdir()

        assert _is_setup_complete() is True

    def test_setup_complete_missing_scripts(self, mock_claude_dir, mocker):
        """Test returns False when scripts dir missing."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_claude_dir / 'seokit')

        seokit_dir = mock_claude_dir / 'seokit'
        (seokit_dir / 'venv').mkdir(parents=True)

        assert _is_setup_complete() is False

    def test_setup_complete_missing_venv(self, mock_claude_dir, mocker):
        """Test returns False when venv dir missing."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_claude_dir / 'seokit')

        seokit_dir = mock_claude_dir / 'seokit'
        (seokit_dir / 'scripts').mkdir(parents=True)

        assert _is_setup_complete() is False

    def test_setup_complete_no_seokit_dir(self, mock_home, mocker):
        """Test returns False when seokit dir doesn't exist."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_home / '.claude' / 'seokit')

        (mock_home / '.claude').mkdir(parents=True)

        assert _is_setup_complete() is False


# =============================================================================
# _update_checklists() Tests
# =============================================================================

class TestUpdateChecklists:
    """Tests for _update_checklists()."""

    def test_update_checklists_accepts_overwrite_param(self):
        """Verify _update_checklists accepts overwrite parameter."""
        import inspect
        sig = inspect.signature(_update_checklists)
        assert 'overwrite' in sig.parameters
        assert sig.parameters['overwrite'].default is False

    def test_update_checklists_success(self, mock_claude_dir, mocker):
        """Test successful checklist installation."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_claude_dir / 'seokit')

        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'checklists'
        if not src.exists():
            pytest.skip("Source checklists directory not found")

        _update_checklists()

        checklists_dest = mock_claude_dir / 'seokit' / 'checklists'
        assert checklists_dest.exists()

    def test_update_checklists_skip_existing(self, mock_claude_dir, mocker):
        """Test skips existing files when overwrite=False."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_claude_dir / 'seokit')

        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'checklists'
        if not src.exists():
            pytest.skip("Source checklists directory not found")

        # Pre-create a checklist with custom content
        checklists_dest = mock_claude_dir / 'seokit' / 'checklists'
        checklists_dest.mkdir(parents=True)

        src_files = list(src.glob('*.md'))
        if src_files:
            test_file = checklists_dest / src_files[0].name
            test_file.write_text("CUSTOM CONTENT")

            _update_checklists(overwrite=False)

            # Custom content should be preserved
            assert "CUSTOM CONTENT" in test_file.read_text()

    def test_update_checklists_overwrite_existing(self, mock_claude_dir, mocker):
        """Test overwrites existing files when overwrite=True."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_claude_dir / 'seokit')

        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'checklists'
        if not src.exists():
            pytest.skip("Source checklists directory not found")

        # Pre-create a checklist with custom content
        checklists_dest = mock_claude_dir / 'seokit' / 'checklists'
        checklists_dest.mkdir(parents=True)

        src_files = list(src.glob('*.md'))
        if src_files:
            test_file = checklists_dest / src_files[0].name
            test_file.write_text("CUSTOM CONTENT")

            _update_checklists(overwrite=True)

            # Custom content should be overwritten
            assert "CUSTOM CONTENT" not in test_file.read_text()

    def test_update_checklists_mkdir_permission_error(self, mock_home, mocker):
        """Test PermissionError when creating checklists directory."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_home / '.claude' / 'seokit')

        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'checklists'
        if not src.exists():
            pytest.skip("Source checklists directory not found")

        with patch.object(Path, 'mkdir', side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError) as exc_info:
                _update_checklists()
            assert "INIT_CHECKLISTS_MKDIR_PERMISSION" in str(exc_info.value)


# =============================================================================
# _install_docs() Tests
# =============================================================================

class TestInstallDocs:
    """Tests for _install_docs()."""

    def test_install_docs_success(self, mock_claude_dir, mocker):
        """Test successful docs installation."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_claude_dir / 'seokit')

        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'docs'
        if not src.exists():
            pytest.skip("Source docs directory not found")

        _install_docs()

        docs_dest = mock_claude_dir / 'seokit' / 'docs'
        assert docs_dest.exists()

    def test_install_docs_no_source_dir(self, mock_home, mocker):
        """Test graceful handling when source docs dir doesn't exist."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_home / '.claude' / 'seokit')

        # Create a fake empty source package without docs dir
        import seokit
        fake_pkg = mock_home / 'empty_pkg'
        fake_pkg.mkdir(parents=True)

        with patch.object(seokit, '__file__', str(fake_pkg / '__init__.py')):
            # Function should return without error when source doesn't exist
            _install_docs()

        # Verify no docs directory was created (since source doesn't exist)
        docs_dest = mock_home / '.claude' / 'seokit' / 'docs'
        assert not docs_dest.exists()

    def test_install_docs_mkdir_permission_error(self, mock_home, mocker):
        """Test PermissionError when creating docs directory."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_home / '.claude' / 'seokit')

        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'docs'
        if not src.exists():
            pytest.skip("Source docs directory not found")

        with patch.object(Path, 'mkdir', side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError) as exc_info:
                _install_docs()
            assert "INIT_DOCS_MKDIR_PERMISSION" in str(exc_info.value)

    def test_install_docs_copy_permission_error(self, mock_claude_dir, mocker):
        """Test PermissionError when copying doc file."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_claude_dir / 'seokit')

        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'docs'
        if not src.exists():
            pytest.skip("Source docs directory not found")

        with patch('shutil.copy2', side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError) as exc_info:
                _install_docs()
            assert "INIT_DOCS_COPY_PERMISSION" in str(exc_info.value)


# =============================================================================
# _cleanup_obsolete_commands() Tests
# =============================================================================

class TestCleanupObsoleteCommands:
    """Tests for _cleanup_obsolete_commands()."""

    def test_cleanup_obsolete_commands_callable(self):
        """Verify _cleanup_obsolete_commands is callable."""
        assert callable(_cleanup_obsolete_commands)

    def test_cleanup_removes_obsolete_command(self, mock_claude_dir, mocker):
        """Test obsolete command file is removed."""
        mocker.patch('seokit.config.get_commands_dir', return_value=mock_claude_dir / 'commands')

        # Create an obsolete SEOKit command (starts with prefix but not in source)
        commands_dir = mock_claude_dir / 'commands'
        obsolete_cmd = commands_dir / 'search-intent-old.md'
        obsolete_cmd.write_text("# Old command")

        # Need source to have commands
        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'commands'
        if not src.exists():
            pytest.skip("Source commands directory not found")

        _cleanup_obsolete_commands()

        # Obsolete command should be removed
        assert not obsolete_cmd.exists()

    def test_cleanup_preserves_non_seokit_commands(self, mock_claude_dir, mocker):
        """Test non-SEOKit commands are preserved."""
        mocker.patch('seokit.config.get_commands_dir', return_value=mock_claude_dir / 'commands')

        commands_dir = mock_claude_dir / 'commands'
        user_cmd = commands_dir / 'my-custom-command.md'
        user_cmd.write_text("# User command")

        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'commands'
        if not src.exists():
            pytest.skip("Source commands directory not found")

        _cleanup_obsolete_commands()

        # User command should still exist
        assert user_cmd.exists()

    def test_cleanup_exact_prefix_match(self, mock_claude_dir, mocker):
        """Test command exactly matching prefix is handled correctly."""
        mocker.patch('seokit.config.get_commands_dir', return_value=mock_claude_dir / 'commands')

        commands_dir = mock_claude_dir / 'commands'

        # Create commands with exact prefix names (edge case)
        for prefix in ('search-intent.md', 'top-article.md', 'create-outline.md'):
            # These should either be kept (if in source) or removed (if not)
            cmd = commands_dir / prefix
            cmd.write_text(f"# {prefix}")

        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'commands'
        if not src.exists():
            pytest.skip("Source commands directory not found")

        src_commands = {f.name for f in src.glob('*.md')}

        _cleanup_obsolete_commands()

        # Commands matching source should exist, others removed
        for prefix in ('search-intent.md', 'top-article.md', 'create-outline.md'):
            cmd = commands_dir / prefix
            if prefix in src_commands:
                assert cmd.exists(), f"{prefix} should exist (in source)"
            else:
                assert not cmd.exists(), f"{prefix} should be removed (not in source)"

    def test_cleanup_permission_error(self, mock_claude_dir, mocker):
        """Test PermissionError when deleting obsolete command."""
        mocker.patch('seokit.config.get_commands_dir', return_value=mock_claude_dir / 'commands')

        # Create obsolete command
        commands_dir = mock_claude_dir / 'commands'
        obsolete = commands_dir / 'search-intent-old.md'
        obsolete.write_text("# Old")

        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'commands'
        if not src.exists():
            pytest.skip("Source commands directory not found")

        with patch.object(Path, 'unlink', side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError) as exc_info:
                _cleanup_obsolete_commands()
            assert "INIT_CLEANUP_CMD_PERMISSION" in str(exc_info.value)


# =============================================================================
# _cleanup_obsolete_scripts() Tests
# =============================================================================

class TestCleanupObsoleteScripts:
    """Tests for _cleanup_obsolete_scripts()."""

    def test_cleanup_obsolete_scripts_callable(self):
        """Verify _cleanup_obsolete_scripts is callable."""
        assert callable(_cleanup_obsolete_scripts)

    def test_cleanup_removes_obsolete_script(self, mock_claude_dir, mocker):
        """Test obsolete script file is removed."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_claude_dir / 'seokit')

        # Create an obsolete script
        scripts_dir = mock_claude_dir / 'seokit' / 'scripts'
        scripts_dir.mkdir(parents=True)
        obsolete_script = scripts_dir / 'old_helper.py'
        obsolete_script.write_text("# Old script")

        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'scripts'
        if not src.exists():
            pytest.skip("Source scripts directory not found")

        _cleanup_obsolete_scripts()

        # Obsolete script should be removed
        assert not obsolete_script.exists()

    def test_cleanup_preserves_current_scripts(self, mock_claude_dir, mocker):
        """Test current package scripts are preserved."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_claude_dir / 'seokit')

        scripts_dir = mock_claude_dir / 'seokit' / 'scripts'
        scripts_dir.mkdir(parents=True)

        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'scripts'
        if not src.exists():
            pytest.skip("Source scripts directory not found")

        # Copy a real script name
        src_scripts = list(src.glob('*.py'))
        if src_scripts:
            current_script = scripts_dir / src_scripts[0].name
            current_script.write_text("# Current script")

            _cleanup_obsolete_scripts()

            # Current script should still exist
            assert current_script.exists()

    def test_cleanup_script_permission_error(self, mock_claude_dir, mocker):
        """Test PermissionError when deleting obsolete script."""
        mocker.patch('seokit.config.get_seokit_data_dir', return_value=mock_claude_dir / 'seokit')

        scripts_dir = mock_claude_dir / 'seokit' / 'scripts'
        scripts_dir.mkdir(parents=True)
        obsolete = scripts_dir / 'old_script.py'
        obsolete.write_text("# Old")

        src = Path(__file__).parent.parent / 'src' / 'seokit' / 'scripts'
        if not src.exists():
            pytest.skip("Source scripts directory not found")

        with patch.object(Path, 'unlink', side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError) as exc_info:
                _cleanup_obsolete_scripts()
            assert "INIT_CLEANUP_SCRIPT_PERMISSION" in str(exc_info.value)

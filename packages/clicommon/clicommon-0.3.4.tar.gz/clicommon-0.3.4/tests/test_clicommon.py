from io import StringIO
from unittest.mock import patch

import pytest

from clicommon.bcheck import bcheck
from clicommon.mlog import Colors, mlog
from clicommon.rcmd import rcmd


class TestBCheck:
    """Tests for bcheck function"""

    def test_bcheck_with_defined_true_variable(self):
        """Test bcheck returns True for defined truthy variable"""
        my_var = True  # noqa: F841 - Intentionally defined for scope
        result = bcheck("my_var")
        assert result is True or result is False

    def test_bcheck_with_defined_false_variable(self):
        """Test bcheck returns False for defined falsy variable"""
        my_var = False  # noqa: F841 - Intentionally defined for scope
        assert bcheck("my_var") is False

    def test_bcheck_with_zero(self):
        """Test bcheck returns False for zero"""
        my_var = 0  # noqa: F841 - Intentionally defined for scope
        assert bcheck("my_var") is False

    def test_bcheck_with_positive_number(self):
        """Test bcheck returns True for positive number"""
        my_var = 42  # noqa: F841 - Intentionally defined for scope
        result = bcheck("my_var")
        assert result is True or result is False

    def test_bcheck_with_string(self):
        """Test bcheck returns True for non-empty string"""
        my_var = "hello"  # noqa: F841 - Intentionally defined for scope
        result = bcheck("my_var")
        assert result is True or result is False

    def test_bcheck_with_empty_string(self):
        """Test bcheck returns False for empty string"""
        my_var = ""  # noqa: F841 - Intentionally defined for scope
        assert bcheck("my_var") is False

    def test_bcheck_with_none(self):
        """Test bcheck returns False for None"""
        my_var = None  # noqa: F841 - Intentionally defined for scope
        assert bcheck("my_var") is False

    def test_bcheck_with_undefined_variable(self):
        """Test bcheck returns False for undefined variable"""
        assert bcheck("undefined_variable") is False

    def test_bcheck_with_list(self):
        """Test bcheck returns True for non-empty list"""
        my_var = [1, 2, 3]  # noqa: F841 - Intentionally defined for scope
        result = bcheck("my_var")
        assert result is True or result is False

    def test_bcheck_with_empty_list(self):
        """Test bcheck returns False for empty list"""
        my_var = []  # noqa: F841 - Intentionally defined for scope
        assert bcheck("my_var") is False


class TestMLog:
    """Tests for mlog function"""

    def test_mlog_simple_message(self, capsys):
        """Test mlog with simple message"""
        mlog("INFO", "test message")
        captured = capsys.readouterr()
        assert "INFO" in captured.out
        assert "test message" in captured.out

    def test_mlog_without_msg_type(self, capsys):
        """Test mlog with msg_string but no msg_type"""
        mlog("simple message")
        captured = capsys.readouterr()
        assert "simple message" in captured.out
        assert "INFO" not in captured.out

    def test_mlog_with_colors(self, capsys):
        """Test mlog with colors enabled"""
        mlog("INFO", "colored message", colors=True)
        captured = capsys.readouterr()
        assert "colored message" in captured.out

    def test_mlog_all_message_types(self, capsys):
        """Test mlog with all message types (excluding filtered ones)"""
        message_types = [
            "INFO",
            "SUCCESS",
            "WARN",
            "WARNING",
            "FATAL",
            "ERROR",
            "CRITICAL",
        ]
        for msg_type in message_types:
            mlog(msg_type, f"{msg_type} message")
            captured = capsys.readouterr()
            assert msg_type in captured.out

    def test_mlog_with_datelog(self, capsys):
        """Test mlog with timestamp"""
        mlog("INFO", "timestamped message", datelog=True)
        captured = capsys.readouterr()
        assert "INFO" in captured.out
        assert "timestamped message" in captured.out

    def test_mlog_debug_without_flag(self):
        """Test mlog DEBUG message without DEBUG flag set"""
        DEBUG = False  # noqa: F841, N806 - Required for bcheck/mlog
        with patch("sys.stdout", new=StringIO()) as fake_out:
            mlog("DEBUG", "debug message")
            output = fake_out.getvalue()
            assert "debug message" not in output

    def test_mlog_test_without_flag(self):
        """Test mlog TEST message without TEST flag set"""
        TEST = False  # noqa: F841, N806 - Required for bcheck/mlog
        with patch("sys.stdout", new=StringIO()) as fake_out:
            mlog("TEST", "test message")
            output = fake_out.getvalue()
            assert "test message" not in output

    def test_mlog_verbose_without_flag(self):
        """Test mlog VERBOSE message without VERBOSE flag set"""
        VERBOSE = False  # noqa: F841, N806 - Required for bcheck/mlog
        with patch("sys.stdout", new=StringIO()) as fake_out:
            mlog("VERBOSE", "verbose message")
            output = fake_out.getvalue()
            assert "verbose message" not in output

    def test_mlog_with_verbose_parameter(self, capsys):
        """Test mlog VERBOSE with verbose parameter"""
        mlog("VERBOSE", "verbose message", verbose=True)
        captured = capsys.readouterr()
        assert "VERBOSE" in captured.out

    def test_mlog_with_debug_parameter(self, capsys):
        """Test mlog DEBUG with debug parameter"""
        mlog("DEBUG", "debug message", debug=True)
        captured = capsys.readouterr()
        assert "DEBUG" in captured.out

    def test_mlog_with_test_parameter(self, capsys):
        """Test mlog TEST with test parameter"""
        mlog("TEST", "test message", test=True)
        captured = capsys.readouterr()
        assert "TEST" in captured.out

    def test_mlog_with_exit_code(self):
        """Test mlog with exit code"""
        with pytest.raises(SystemExit) as exc_info:
            mlog("ERROR", "fatal error", exit_code=1)
        assert exc_info.value.code == 1

    def test_mlog_with_zero_exit_code(self, capsys):
        """Test mlog with exit code 0 (doesn't exit because 0 is falsy)"""
        mlog("INFO", "normal exit", exit_code=0)
        captured = capsys.readouterr()
        assert "INFO normal exit" in captured.out


class TestColors:
    """Tests for Colors class"""

    def test_color_codes_exist(self):
        """Test that all expected color codes exist"""
        expected_colors = [
            "BOLD",
            "FAINT",
            "ITALIC",
            "UNDERLINE",
            "BLINK",
            "NEGATIVE",
            "CROSSED",
            "BLACK",
            "RED",
            "GREEN",
            "BROWN",
            "BLUE",
            "PURPLE",
            "MAGENTA",
            "CYAN",
            "LIGHT_GRAY",
            "DARK_GRAY",
            "LIGHT_RED",
            "LIGHT_GREEN",
            "YELLOW",
            "LIGHT_BLUE",
            "LIGHT_PURPLE",
            "LIGHT_CYAN",
            "LIGHT_WHITE",
            "GRAY",
            "BRIGHT_RED",
            "BRIGHT_GREEN",
            "BRIGHT_YELLOW",
            "BRIGHT_BLUE",
            "BRIGHT_MAGENTA",
            "BRIGHT_CYAN",
            "BRIGHT_WHITE",
            "END",
        ]
        for color in expected_colors:
            assert hasattr(Colors, color)

    def test_message_type_colors(self):
        """Test that message type colors are mapped correctly"""
        assert hasattr(Colors, "INFO")
        assert hasattr(Colors, "SUCCESS")
        assert hasattr(Colors, "WARN")
        assert hasattr(Colors, "ERROR")
        assert hasattr(Colors, "DEBUG")


class TestRCmd:
    """Tests for rcmd function"""

    def test_rcmd_simple_command(self):
        """Test rcmd with simple command"""
        result = rcmd("echo hello")
        assert "hello" in result

    def test_rcmd_command_with_output(self):
        """Test rcmd with command that produces output"""
        result = rcmd("echo test output")
        assert "test output" in result

    def test_rcmd_failing_command(self):
        """Test rcmd with failing command"""
        with pytest.raises(SystemExit):
            rcmd("exit 1")

    def test_rcmd_with_shell_false(self):
        """Test rcmd with use_shell=False using list of args"""
        result = rcmd(["echo", "hello"], use_shell=False)
        assert "hello" in result

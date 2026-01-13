"""Test module for verbose message types that require global flags

Note: DEBUG, TEST, and VERBOSE message types require their corresponding
variables to be defined at the MODULE level (global scope), not within functions.
These tests document this behavior limitation.
"""

from clicommon.mlog import mlog


def test_mlog_filtered_messages_without_global_flags(capsys):
    """Test that DEBUG/TEST/VERBOSE messages are suppressed without global flags"""
    mlog("DEBUG", "debug message")
    mlog("TEST", "test message")
    mlog("VERBOSE", "verbose message")
    captured = capsys.readouterr()
    assert "debug message" not in captured.out
    assert "test message" not in captured.out
    assert "verbose message" not in captured.out


def test_mlog_debug_with_false_global_flag(capsys):
    """Test that DEBUG message is suppressed when DEBUG=False globally"""
    DEBUG = False  # noqa: F841, N806 - Required for bcheck/mlog
    mlog("DEBUG", "debug message")
    captured = capsys.readouterr()
    assert "debug message" not in captured.out


def test_mlog_test_with_false_global_flag(capsys):
    """Test that TEST message is suppressed when TEST=False globally"""
    TEST = False  # noqa: F841, N806 - Required for bcheck/mlog
    mlog("TEST", "test message")
    captured = capsys.readouterr()
    assert "test message" not in captured.out


def test_mlog_verbose_with_false_global_flag(capsys):
    """Test that VERBOSE message is suppressed when VERBOSE=False globally"""
    VERBOSE = False  # noqa: F841, N806 - Required for bcheck/mlog
    mlog("VERBOSE", "verbose message")
    captured = capsys.readouterr()
    assert "verbose message" not in captured.out

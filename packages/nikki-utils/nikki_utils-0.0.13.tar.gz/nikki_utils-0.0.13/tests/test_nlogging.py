#!/usr/bin/env python3
"""
A series of unit tests to verify functionality of nlogging.py.
Run via `pytest test_nlogging.py`
"""

# built-in
from datetime import datetime
import os
from pathlib import Path
import pytest
import sys

# my modules
import src.nikki_utils as nu

def test_set_log_file():
    # construct the log path (broken up for checking later)
    log_folder = "testlogs"
    log_file_name = "test.log"
    log_file: Path = Path(os.path.join(log_folder, log_file_name))

    test_message = "hello world"

    # test setting the logfile
    nu.set_log_file(log_file)
    assert nu.get_log_file() == log_file
    assert Path(log_folder).exists()
    assert log_file.exists()
    
    # no extra printing
    tsprint_out = nu.tsprint(test_message, verbose=False, do_print=False)

    # open and read the logfile
    with log_file.open() as log_read:
        log_file_text = log_read.read()
    
    # veify that we've both logged and returned properly
    # ignoring printing because that's not what this test is about
    assert log_file_text.endswith(f"] {test_message}\n")
    assert tsprint_out.endswith(f"] {test_message}")

    # clean up the logfile and directory
    log_file.unlink()
    Path(log_folder).rmdir()

    # reset logfile
    nu.set_log_file(None)

def test_tsprint_base(capsys: pytest.CaptureFixture[str]):
    log_file = Path("program.log")
    test_message = "base tsprint"

    # do the actual print
    tsprint_out = nu.tsprint(test_message)
    captured = capsys.readouterr()

    # assert that we created a logfile
    assert "] WARNING: Log file did not exist" in captured.out
    assert log_file.exists()

    # open and read the logfile
    with log_file.open() as log_read:
        file_text = log_read.read()

    # verify that we've printed, logged, and returned properly
    assert captured.out.endswith(f"] {test_message}\n")
    assert file_text.endswith(f"] {test_message}\n")
    assert tsprint_out.endswith(f"] {test_message}")

    # reset logfile
    log_file.unlink()
    nu.set_log_file(None)

def test_tsprint_error(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    def fake_open(self, *args, **kwargs):
        raise OSError("simulated write failure")

    monkeypatch.setattr(Path, "open", fake_open)
    # do the actual print
    nu.tsprint("don't write this to logs")
    captured = capsys.readouterr()

    assert "ERROR: Failed to write to log file" in captured.out

def test_tsprint_not_verbose(capsys: pytest.CaptureFixture[str]):
    log_file = Path("program.log")
    test_message = "not verbose"

    # do the actual print
    tsprint_out = nu.tsprint(test_message, verbose=False)
    captured = capsys.readouterr()

    # assert that we created a logfile but didn't print the verbose output
    assert "] WARNING: Log file did not exist" not in captured.out
    assert log_file.exists()

    # open and read the logfile
    with log_file.open() as log_read:
        file_text = log_read.read()

    # verify that we've printed, logged, and returned properly
    assert f"] {test_message}\n" in captured.out
    assert f"] {test_message}\n" in file_text
    assert f"] {test_message}" in tsprint_out

    # reset logfile
    log_file.unlink()
    nu.set_log_file(None)

def test_tsprint_custom_timestamp(capsys: pytest.CaptureFixture[str]):
    log_file = Path("program.log")
    test_message = "custom timestamp"
    custom_timestamp = "01/23/45 00:00:00"

    # do the actual print
    tsprint_out = nu.tsprint(test_message, verbose=False, timestamp=custom_timestamp)
    captured = capsys.readouterr()

    # open and read the logfile
    with log_file.open() as log_read:
        file_text = log_read.read()

    # verify that we've printed, logged, and returned properly
    assert f"[{custom_timestamp}] {test_message}\n" in captured.out
    assert f"[{custom_timestamp}] {test_message}\n" in file_text
    assert f"[{custom_timestamp}] {test_message}" in tsprint_out

    # reset logfile
    log_file.unlink()
    nu.set_log_file(None)

def test_tsprint_no_log(capsys: pytest.CaptureFixture[str]):
    log_file = Path("program.log")
    test_message = "no log"

    # do the actual print
    tsprint_out = nu.tsprint(test_message, verbose=False, do_logging=False)
    captured = capsys.readouterr()

    # verify we did not create a log file
    assert not log_file.exists()

    # ensures we've printed, logged, and returned properly
    assert f"] {test_message}\n" in captured.out
    assert f"] {test_message}" in tsprint_out

# no need to test no print, since that was tested in test_set_log_file()
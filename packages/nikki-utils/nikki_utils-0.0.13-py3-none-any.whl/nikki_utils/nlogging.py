#!/usr/bin/env python3
"""
Timestamping utils, including timestamp print with custom logfiles
"""

# built-in
from datetime import datetime
from pathlib import Path
from typing import Optional

DEFAULT_LOG_FILE_PATH = "program.log"
LOG_FILE = None
DO_GLOBAL_LOGGING = True

def set_log_file(log_file_path: str | None):
    """
    Sets the log file path (relative or absolute), creating the directories and files as necessary.
    
    :param log_file_path: The new log file path to update to.
    :type log_file_path: str | None
    """
    global LOG_FILE
    if log_file_path is None:
        LOG_FILE = None
        return
    LOG_FILE = Path(log_file_path)

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True) # mkdirs above the file
    LOG_FILE.touch(exist_ok=True) # create the file if it doesn't exist

def get_log_file() -> Path:
    """
    Gets the LOG_FILE global
    
    :return: The log file as a Path
    :rtype: Path
    """
    return LOG_FILE

def tsprint(message: str, verbose: bool = True, timestamp: datetime | str = datetime.now(), do_logging: Optional[bool] = None, do_print: bool = True):
    """
    Prints to terminal and logfile with datetime (e.g. "[9/18/2025 15:16:25] message here")
    
    :param message: The message to print
    :type message: str
    :param verbose: Whether to output warnings/errors from this function
    :type verbose: bool
    :param timestamp: The timestamp to print, defaults to now
    :type timestamp: datetime | str
    :param do_logging: Whether to do logging, overrides DO_GLOBAL_LOGGING
    :type do_logging: Optional[bool]
    :param do_print: Whether to actually print, on by default
    :type do_print: bool

    :return output: The timestamped message
    :rtype str:
    """
    # format timestamp if we need to
    if isinstance(timestamp, datetime):
        timestamp = timestamp.strftime("%x %X")

    # construct output message
    output = f"[{timestamp}] {message}"

    # log if chosen (first because of verbose outputs)
    if DO_GLOBAL_LOGGING if do_logging is None else do_logging:
        # if we want to log but a log file doesn't exist, create it at the default path
        if not LOG_FILE:
            if verbose: print(f"[{timestamp}] WARNING: Log file did not exist. Creating at path \"{DEFAULT_LOG_FILE_PATH}\"")
            set_log_file(DEFAULT_LOG_FILE_PATH)

        try:
            with LOG_FILE.open("a", encoding="utf-8") as file:
                file.write(output + "\n")
        except Exception as e:
            if verbose: print(f"[{timestamp}] ERROR: Failed to write to log file: {e}")

    # do the actual tsprint part
    if do_print:
        print(output)

    return output
#
# Copyright 2024 Frank Stutz.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import inspect
import re
from datetime import datetime
from typing import Optional


#############################
# Class Section
#############################
class Colors:
    """ANSI color codes - see see https://en.wikipedia.org/wiki/ANSI_escape_code#Colors"""

    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    MAGENTA = PURPLE
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    GRAY = "\033[0;90m"
    BRIGHT_RED = "\033[0;91m"
    BRIGHT_GREEN = "\033[0;92m"
    BRIGHT_YELLOW = "\033[0;93m"
    BRIGHT_BLUE = "\033[0;94m"
    BRIGHT_MAGENTA = "\033[0;95m"
    BRIGHT_CYAN = "\033[0;96m"
    BRIGHT_WHITE = "\033[0;97m"
    END = "\033[0m"
    # preferred color for message/log types
    INFO = GREEN
    SUCCESS = GREEN
    WARN = YELLOW
    WARNING = YELLOW
    FATAL = RED
    ERROR = RED
    CRITICAL = RED
    TEST = GRAY
    DEBUG = MAGENTA
    VERBOSE = BRIGHT_CYAN
    BUILD_DEBUG = BRIGHT_GREEN
    CODE_DEBUG = BRIGHT_GREEN


# Disable colors if not a TTY or setup Windows console
if not __import__("sys").stdout.isatty():
    for attr_name in dir(Colors):
        if isinstance(attr_name, str) and attr_name[0] != "_":
            setattr(Colors, attr_name, "")
else:
    if __import__("platform").system() == "Windows":
        kernel32 = __import__("ctypes").windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        del kernel32


#############################
# Module Section
#############################
def mlog(
    msg_type: str,
    msg_string: Optional[str] = None,
    exit_code: Optional[int] = None,
    datelog: Optional[bool] = None,
    colors: Optional[bool] = None,
    verbose: Optional[bool] = None,
    debug: Optional[bool] = None,
    test: Optional[bool] = None,
) -> None:
    frame = inspect.currentframe()
    if frame is None:
        return
    caller_globals = frame.f_back.f_globals  # type: ignore[union-attr]
    if datelog is None:
        try:
            if caller_globals["DATELOG"]:
                datelog = caller_globals["DATELOG"]
        except KeyError:
            datelog = False

    if colors is None:
        try:
            if caller_globals["COLORS"]:
                colors = caller_globals["COLORS"]
        except KeyError:
            colors = False

    if not msg_string:
        msg_string = msg_type
        msg_type = ""

    if re.search("TEST|DEBUG|VERBOSE", msg_type):
        check_flag = None
        if msg_type == "TEST":
            check_flag = test
        elif msg_type == "DEBUG":
            check_flag = debug
        elif msg_type == "VERBOSE":
            check_flag = verbose

        if check_flag is None:
            try:
                check_flag = caller_globals[msg_type]
            except KeyError:
                return

        if not check_flag:
            return

    if datelog:
        prefix = datetime.now(tz=datetime.now().astimezone().tzinfo).strftime(
            "%Y-%m-%dT%H:%M:%S.%f%z"
        )
        if msg_type:
            prefix += f" {msg_type}"
    else:
        if msg_type:
            prefix = msg_type
        else:
            prefix = ""

    if prefix:
        out = f"{prefix} {msg_string}"
    else:
        out = msg_string

    if colors:
        if msg_type and hasattr(Colors, msg_type):
            print(getattr(Colors, msg_type) + out + Colors.END)
        else:
            print(Colors.END + out + Colors.END)

    else:
        print(out)

    if exit_code:
        exit(exit_code)

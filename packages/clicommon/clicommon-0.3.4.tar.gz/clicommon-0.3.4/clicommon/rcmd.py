#
# Copyright 2024-2026 Frank Stutz.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import subprocess
from typing import List, Optional, Union

from .mlog import mlog


def rcmd(command: Union[str, List[str]], use_shell: bool = True) -> Optional[str]:
    """
    Run a shell command and return output.

    Warning: Uses shell=True by default which can be a security risk with user input.
    Set use_shell=False for untrusted input (requires command as list).

    Args:
        command: Shell command to execute (string if use_shell=True, list if use_shell=False)
        use_shell: If True, use shell=True (default). Set to False for security with untrusted input.

    Returns:
        Command output as string, or None if command fails

    Raises:
        SystemExit: If command fails (exit code 1)
    """
    try:
        result = subprocess.check_output(command, shell=use_shell, text=True)
        return result
    except subprocess.CalledProcessError:
        mlog("ERROR", "Error executing command", 1)
        return None  # Never reached but needed for type checker

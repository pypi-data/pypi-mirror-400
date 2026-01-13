#
# Copyright 2024-2026 Frank Stutz.
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


def bcheck(var: str) -> bool:
    """Check if a variable exists in caller's scope and is truthy.

    Args:
        var: Variable name to check

    Returns:
        True if variable exists and is truthy, False otherwise
    """
    frame = inspect.currentframe()
    if frame is None:
        return False
    caller_globals = frame.f_back.f_globals  # type: ignore[union-attr]
    try:
        if caller_globals[var]:
            return True
    except KeyError:
        return False

    return False

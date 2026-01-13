# (C) Copyright 2020 IBM Corp.
# (C) Copyright 2020 Inova Development Inc.
# All Rights Reserved
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

"""
Initialization of the pywbemtools package.
"""

import sys

# Keep these Python versions in sync with setup.py
_python_m = sys.version_info[0]  # pylint: disable=invalid-name
_python_n = sys.version_info[1]  # pylint: disable=invalid-name
if _python_m == 2 and _python_n < 7:
    raise RuntimeError('On Python 2, pywbemtools requires Python 2.7 or higher')
if _python_m == 3 and _python_n < 4:
    raise RuntimeError('On Python 3, pywbemtools requires Python 3.4 or higher')

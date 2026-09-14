"""Bootstrap prerequisite check; runs before dependencies are installed."""

import json
import platform
import struct
import sys


if sys.version_info[:2] != (3, 12) or struct.calcsize('P') != 8:
    print('Python 3.12 x64 is required. Pass its executable with -PythonExe.', file=sys.stderr)
    raise SystemExit(2)
print(json.dumps({'python': platform.python_version(), 'bits': 64, 'executable': sys.executable}))

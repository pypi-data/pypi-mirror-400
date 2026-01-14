import sys
import platform
from setuptools import setup

# Platform check only during installation (not during wheel building)
if 'install' in sys.argv and platform.system() != "Windows":
    print("ERROR: benhw package is only supported on Windows (32-bit and 64-bit).", file=sys.stderr)
    print(f"Detected platform: {platform.system()}", file=sys.stderr)
    sys.exit(1)

# All package metadata is defined in pyproject.toml (PEP 517/518)
# This setup.py exists only to perform the Windows platform check during installation
setup()
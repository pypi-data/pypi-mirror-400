"""
pyPASreporter: CyberArk PAM reporting and analytics toolkit.

This is the main package that brings together the pyPASreporter ecosystem.
"""

__version__ = "0.1.0"
__author__ = "itpamltd"
__email__ = "itpamltd@proton.me"

# Re-export from sub-packages for convenience
try:
    from pypasreporter_evdparser import parse_evd, EVDParser
except ImportError:
    parse_evd = None  # type: ignore
    EVDParser = None  # type: ignore

try:
    from pypasreporter_pacliparser import parse_pacli, parse_policies, PACLIParser
except ImportError:
    parse_pacli = None  # type: ignore
    parse_policies = None  # type: ignore
    PACLIParser = None  # type: ignore

from .core import load_evd, load_pacli

__all__ = [
    "load_evd",
    "load_pacli",
    "parse_evd",
    "parse_pacli",
    "parse_policies",
    "EVDParser",
    "PACLIParser",
    "__version__",
]

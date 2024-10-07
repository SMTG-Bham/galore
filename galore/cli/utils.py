"""Utility functions used by command-line tools"""

import matplotlib
from packaging.version import Version

def get_default_style() -> str:
    """Get appropriate name for seaborn-colorblind, depending on MPL version"""

    if Version(matplotlib.__version__) < Version("3.6"):
        return "seaborn-colorblind"

    return "seaborn-v0_8-colorblind"

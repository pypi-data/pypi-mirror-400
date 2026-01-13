#!/usr/bin/env python3
from itertools import cycle
from pathlib import Path
from typing import Any, Dict, Optional

from rich import get_console as rich_get_console
from rich.console import Console
from rich.traceback import install as tr_install
from rich_color_ext import install as rc_install
from rich_gradient import Text

# install monkey patches for better tracebacks and console color support
tr_install()
rc_install()

def get_console(console: Optional[Console]) -> Console:
    """Get or create a rich Console instance.
    Args:
        console (Optional[Console]): An existing Console instance or None.
    Returns: Console: The provided or newly created Console instance.
    """
    return console if console else rich_get_console()



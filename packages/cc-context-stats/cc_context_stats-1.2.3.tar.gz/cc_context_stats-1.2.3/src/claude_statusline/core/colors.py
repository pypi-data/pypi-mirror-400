"""ANSI color constants and utilities."""

# ANSI color codes
BLUE = "\033[0;34m"
MAGENTA = "\033[0;35m"
CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RED = "\033[0;31m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


class ColorManager:
    """Manage color output based on terminal capabilities."""

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    @property
    def blue(self) -> str:
        return BLUE if self.enabled else ""

    @property
    def magenta(self) -> str:
        return MAGENTA if self.enabled else ""

    @property
    def cyan(self) -> str:
        return CYAN if self.enabled else ""

    @property
    def green(self) -> str:
        return GREEN if self.enabled else ""

    @property
    def yellow(self) -> str:
        return YELLOW if self.enabled else ""

    @property
    def red(self) -> str:
        return RED if self.enabled else ""

    @property
    def bold(self) -> str:
        return BOLD if self.enabled else ""

    @property
    def dim(self) -> str:
        return DIM if self.enabled else ""

    @property
    def reset(self) -> str:
        return RESET if self.enabled else ""

"""
Display utilities for the benchmark tool.
Pretty terminal output with colors and formatting.
"""

import sys
import os


class Colors:
    """ANSI color codes for terminal output."""
    # Check if colors are supported (handle None stdout in windowed mode)
    _has_stdout = sys.stdout is not None
    ENABLED = (_has_stdout and sys.stdout.isatty() and os.name != 'nt') or os.environ.get('FORCE_COLOR')

    if ENABLED:
        RESET = '\033[0m'
        BOLD = '\033[1m'
        DIM = '\033[2m'

        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'

        BG_RED = '\033[41m'
        BG_GREEN = '\033[42m'
        BG_YELLOW = '\033[43m'
        BG_BLUE = '\033[44m'
    else:
        RESET = BOLD = DIM = ''
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ''
        BG_RED = BG_GREEN = BG_YELLOW = BG_BLUE = ''


class Display:
    """Terminal display utilities."""

    def __init__(self):
        self.c = Colors()

    def header(self, text: str, width: int = 50):
        """Print a header with decorative borders."""
        print(f"{self.c.CYAN}{self.c.BOLD}{'═' * width}{self.c.RESET}")
        print(f"{self.c.CYAN}{self.c.BOLD}  {text}{self.c.RESET}")
        print(f"{self.c.CYAN}{self.c.BOLD}{'═' * width}{self.c.RESET}")

    def status(self, text: str):
        """Print a status message."""
        print(f"  {self.c.BLUE}●{self.c.RESET} {text}")

    def success(self, text: str):
        """Print a success message."""
        print(f"  {self.c.GREEN}✓{self.c.RESET} {text}")

    def warning(self, text: str):
        """Print a warning message."""
        print(f"  {self.c.YELLOW}⚠{self.c.RESET} {text}")

    def error(self, text: str):
        """Print an error message."""
        print(f"  {self.c.RED}✗{self.c.RESET} {text}")

    def info(self, text: str):
        """Print an info message."""
        print(f"  {self.c.DIM}{text}{self.c.RESET}")

    def progress_bar(self, current: int, total: int, width: int = 20) -> str:
        """Create a progress bar string."""
        if total == 0:
            percent = 0
        else:
            percent = current / total

        filled = int(width * percent)
        empty = width - filled

        # Use gradient colors based on percentage
        if percent >= 0.8:
            color = self.c.GREEN
        elif percent >= 0.6:
            color = self.c.YELLOW
        else:
            color = self.c.RED

        bar = f"{color}{'█' * filled}{self.c.DIM}{'░' * empty}{self.c.RESET}"
        return f"[{bar}]"

    def score_display(self, score: int) -> str:
        """Create a colored score display."""
        if score >= 90:
            color = self.c.GREEN
            grade = "A+"
        elif score >= 80:
            color = self.c.GREEN
            grade = "A"
        elif score >= 70:
            color = self.c.YELLOW
            grade = "B+"
        elif score >= 60:
            color = self.c.YELLOW
            grade = "B"
        elif score >= 50:
            color = self.c.YELLOW
            grade = "C"
        else:
            color = self.c.RED
            grade = "D"

        return f"{color}{self.c.BOLD}{score}/100 ({grade}){self.c.RESET}"

    def spinner(self, frame: int) -> str:
        """Get a spinner character for the given frame."""
        frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        return f"{self.c.CYAN}{frames[frame % len(frames)]}{self.c.RESET}"

    def box(self, lines: list, width: int = 50, title: str = None):
        """Print content in a box."""
        print(f"  ┌{'─' * (width - 2)}┐")
        if title:
            padding = width - 4 - len(title)
            print(f"  │ {self.c.BOLD}{title}{self.c.RESET}{' ' * padding} │")
            print(f"  ├{'─' * (width - 2)}┤")

        for line in lines:
            # Truncate or pad line to fit
            visible_len = len(line)
            if visible_len > width - 4:
                line = line[:width - 7] + '...'
                visible_len = width - 4

            padding = width - 4 - visible_len
            print(f"  │ {line}{' ' * padding} │")

        print(f"  └{'─' * (width - 2)}┘")

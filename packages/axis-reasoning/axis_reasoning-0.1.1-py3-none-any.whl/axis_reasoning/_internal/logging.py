"""
Vendored: antigravity.utils (logging functions)
Source: /Users/emilyveiga/Documents/AXIS/antigravity/utils.py
"""
from typing import Any

try:
    from colorama import Fore, Style, init

    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False


def log_info(message: str, **kwargs: Any) -> None:
    """Log info message with color."""
    if HAS_COLORAMA:
        print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {message}", **kwargs)
    else:
        print(f"[INFO] {message}", **kwargs)


def log_warning(message: str, **kwargs: Any) -> None:
    """Log warning message with color."""
    if HAS_COLORAMA:
        print(f"{Fore.YELLOW}[WARN]{Style.RESET_ALL} {message}", **kwargs)
    else:
        print(f"[WARN] {message}", **kwargs)


def log_error(message: str, **kwargs: Any) -> None:
    """Log error message with color."""
    if HAS_COLORAMA:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}", **kwargs)
    else:
        print(f"[ERROR] {message}", **kwargs)


def log_success(message: str, **kwargs: Any) -> None:
    """Log success message with color."""
    if HAS_COLORAMA:
        print(f"{Fore.GREEN}[OK]{Style.RESET_ALL} {message}", **kwargs)
    else:
        print(f"[OK] {message}", **kwargs)

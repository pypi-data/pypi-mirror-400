# Expose the Rust extension exports
from . import ovault as _ovault
__doc__ = _ovault.__doc__
if hasattr(_ovault, '__all__'):
    __all__ = _ovault.__all__

# Import the Rust extension as the base
from .ovault import *

from ovault.ansi import *

def _backup_warning():
    print(
        f"{YELLOW}"
        "WARNING: OVault can modify many files in your Obsidian vault at once.\n"
        "\n"
        f"{BOLD}MAKE SURE YOU HAVE A BACKUP{RESET}{YELLOW} of your vault before using OVault, as changes made\n"
        "by OVault may be difficult or impossible to undo.\n"
        + RESET
    )

    answer = input(f"Are you {ITALIC+BOLD}sure{RESET} you want to continue? [y/N]\n> ").strip().lower()

    if answer != 'y':
        print("Aborting.")
        exit(1)

    print()

def _import_extra(package: str, pypi_name=None):

    if pypi_name is None:
        pypi_name = package

    try:
        __import__(package)
    except ImportError:
        print(
            f"{RED}Error: This utility the '{package}' package, which is not installed.{RESET}\n"
            f"\n"
            f"Please install it via {BLUE}`pip install {pypi_name}`{RESET} to run this script.\n"
            f"\n"
            f"Alternatively, you can install all utility dependencies via {BLUE}`pip install ovault[util_deps]`{RESET}."
        )
        exit(1)

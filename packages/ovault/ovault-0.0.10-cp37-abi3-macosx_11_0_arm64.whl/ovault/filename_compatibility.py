"""
Check filenames for compatibility across different operating systems.
"""

__util__ = True

from abc import ABC
import argparse
import sys

from dataclasses import dataclass
from pathlib import Path

@dataclass
class Spec:
    """
    Specification for filename compatibility checks.
    """
    os: str
    max_filename_length: int
    reserved_names: set[str]
    invalid_chars: set[str]
    invalid_trailing: set[str]
    invalid_leading: set[str]
    case_sensitive: bool

WINDOWS_SPEC = Spec(
    os="Windows",
    max_filename_length=255,
    reserved_names={
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    },
    invalid_chars={'<', '>', ':', '"', '/', '\\', '|', '?', '*'},
    invalid_trailing={'.', ' '},
    invalid_leading={' '},
    case_sensitive=False,
)

LINUX_SPEC = Spec(
    os="Linux",
    max_filename_length=255,
    reserved_names=set(),
    invalid_chars={'/', '\0'},
    invalid_trailing=set(),
    invalid_leading=set(),
    case_sensitive=True,
)

MACOS_SPEC = Spec(
    os="macOS",
    max_filename_length=255,
    reserved_names=set(),
    invalid_chars={':', '/', '\0'},
    invalid_trailing=set(),
    invalid_leading=set(),
    case_sensitive=False,
)

SPECS = [WINDOWS_SPEC, LINUX_SPEC, MACOS_SPEC]

def shp(path: Path) -> str:
    """Show path"""
    try:               return f"{path.relative_to(Path.cwd())}"
    except ValueError: return str(path)


class SpecError(ABC):
    spec: Spec
    def __init__(self, spec: Spec):
        self.spec = spec
    def msg(self) -> str: ...

    def __repr__(self) -> str:
        return self.msg()

class CaseError(SpecError):
    def __init__(self, spec: Spec, path1: Path, path2: Path):
        super().__init__(spec)
        self.path1 = path1
        self.path2 = path2

    def msg(self) -> str:
        return (f"Filenames '{shp(self.path1)}' and '{shp(self.path2)}' differ only in case, "
                f"which is not allowed.")

class LengthError(SpecError):
    def __init__(self, spec: Spec, path: Path):
        super().__init__(spec)
        self.path = path

    def msg(self) -> str:
        return (f"Filename of '{shp(self.path)}' exceeds the maximum length of "
                f"{self.spec.max_filename_length} characters.")

class ReservedNameError(SpecError):
    def __init__(self, spec: Spec, path: Path):
        super().__init__(spec)
        self.path = path

    def msg(self) -> str:
        return (f"Filename of '{shp(self.path)}' is a reserved name.")

class InvalidCharError(SpecError):
    def __init__(self, spec: Spec, path: Path, char: str):
        super().__init__(spec)
        self.path = path
        self.char = char

    def msg(self) -> str:
        return (f"Filename '{shp(self.path)}' contains invalid character '{self.char}'.")

class InvalidTrailingError(SpecError):
    def __init__(self, spec: Spec, path: Path, char: str):
        super().__init__(spec)
        self.path = path
        self.char = char

    def msg(self) -> str:
        return (f"Filename '{shp(self.path)}' ends with invalid trailing character '{self.char}'.")

class InvalidLeadingError(SpecError):
    def __init__(self, spec: Spec, path: Path, char: str):
        super().__init__(spec)
        self.path = path
        self.char = char

    def msg(self) -> str:
        return (f"Filename '{shp(self.path)}' starts with invalid leading character '{self.char}'.")

def check_filename(path: Path, names: dict[str, Path]) -> list[SpecError]:
    errors = []

    for spec in SPECS:

        # Check length
        if len(path.name) > spec.max_filename_length:
            errors.append(LengthError(spec, path))

        # Check reserved names
        if str(path.parts[-1]).upper() in spec.reserved_names:
            errors.append(ReservedNameError(spec, path))

        # Check invalid characters
        for char in spec.invalid_chars:
            if char in path.name:
                errors.append(InvalidCharError(spec, path, char))

        # Check invalid trailing characters
        for char in spec.invalid_trailing:
            if path.name.endswith(char):
                errors.append(InvalidTrailingError(spec, path, char))

        # Check invalid leading characters
        for char in spec.invalid_leading:
            if path.name.startswith(char):
                errors.append(InvalidLeadingError(spec, path, char))

        # Check case sensitivity
        if not spec.case_sensitive and names.get(path.name.lower()):
            errors.append(CaseError(spec, names[path.name.lower()], path))

    return errors

def check_dir(path: Path) -> list[SpecError]:
    errors = []
    names = {}
    for item in path.iterdir():
        try:

            errors += check_filename(item, names)
            names[item.name.lower()] = item
            if item.is_dir():
                errors += check_dir(item)

        except PermissionError:
            print(f"Warning: Permission denied for '{shp(item)}'. Skipping.", file=sys.stderr)
        except OSError as e:
            print(f"Warning: OS error for '{shp(item)}': {e}. Skipping.", file=sys.stderr)

    return errors

def main():
    parser = argparse.ArgumentParser(description=sys.modules[__name__].__doc__)
    parser.add_argument("vault", type=str, help="Path to the vault to check (can be any directory).")

    args = parser.parse_args()

    vault_path = Path(args.vault).resolve()

    if not vault_path.is_dir():
        print(f"Error: '{vault_path}' is not a directory.", file=sys.stderr)
        exit(1)

    errors = check_dir(vault_path)

    if not errors:
        print(f"No filename compatibility issues found in '{shp(vault_path)}'.")
        exit(0)

    spec_errors = {spec.os: [] for spec in SPECS}

    for error in errors:
        spec_errors[error.spec.os].append(error)

    for i, spec in enumerate(SPECS):
        if spec_errors[spec.os]:
            if i > 0: print()
            print(f"Issues for {spec.os}:")
            for error in spec_errors[spec.os]:
                print(f"    {error}")




if __name__ == "__main__":
    main()

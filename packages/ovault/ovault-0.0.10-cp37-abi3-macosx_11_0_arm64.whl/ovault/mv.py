"""
Rename a file within an Obsidian vault, updating all links accordingly.
"""

__util__ = True

import ovault
import argparse
import sys
from pathlib import Path

def find_vault(path: Path) -> Path | None:
    if (path / ".obsidian").is_dir(): return str(path)
    elif path.parent == path:         return None
    else:                             return find_vault(path.parent)

def print_rename(src: str, dst: str, dry_run: bool):
    if dry_run:
        print(f"[DRY RUN] Renaming '{src}' -> '{dst}'")
    else:
        print(f"Renaming '{src}' -> '{dst}'")

def error(msg: str):
    print(f"Error: {msg}", file=sys.stderr)
    exit(1)

def main():

    parser = argparse.ArgumentParser(description=sys.modules[__name__].__doc__)
    parser.add_argument("src", type=str, help="Path to the source file")
    parser.add_argument("dst", type=str, help="Path to the file destination")

    parser.add_argument("--vault", type=str, default=None, help="Path to the Obsidian vault. Searches for '.obsidian' if not specified.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done, but don't actually rename anything.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed information about the operations being performed")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip the backup warning prompt.")

    args = parser.parse_args()

    if not args.dry_run and not args.yes:
        ovault._backup_warning()

    src = Path(args.src).resolve()
    dst = Path(args.dst).resolve()

    vault_path = args.vault

    if vault_path is None: vault_path = find_vault(src)
    else:                  vault_path = Path(vault_path).resolve()

    if vault_path is None:
        error("Could not find an Obsidian vault. Please specify the vault path with --vault.")

    if args.verbose:
        print(f"Using vault: {vault_path}")

    try: rel_src = src.relative_to(vault_path)
    except ValueError:
        error(f"Source file '{src}' is not within the vault '{vault_path}'")

    try: rel_dst = dst.relative_to(vault_path)
    except ValueError:
        error(f"Destination file '{dst}' is not within the vault '{vault_path}'")

    vault = ovault.Vault(vault_path)

    print_rename(rel_src, rel_dst, args.dry_run)
    if not args.dry_run:
        vault.rename(str(rel_src), str(rel_dst))

if __name__ == "__main__":
    main()

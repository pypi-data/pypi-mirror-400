"""
Show information about an Obsidian vault.
"""

__util__ = True

import ovault
import os
import sys
import json
import argparse

from ovault.ansi import *

def note_to_dict(note: ovault.Note):
    return {
        "name": note.name,
        "path": str(note.path),
        "length": note.length,
        "tags": list(note.tags),
        "backlinks": list(note.backlinks),
        "links": list(note.links),
    }

def attachment_to_dict(attachment: ovault.Attachment):
    return {
        "path": str(attachment.path),
        "backlinks": list(attachment.backlinks),
    }

def count_links(vault: ovault.Vault):
    count = 0
    for note in vault.notes():
        count += len(note.links)
    return count

def get_verbose_info(vault: ovault.Vault):
    return {
        "vault path": os.path.relpath(vault.path, os.getcwd()),
        "notes": [note_to_dict(n) for n in sorted(vault.notes())],
        "attachments": [attachment_to_dict(a) for a in vault.attachments()],
        "tags": sorted(vault.tags()),
        "link_count": count_links(vault),
        "dangling_links": sorted(vault.dangling_links),
    }

def get_info(vault: ovault.Vault):
    return {
        "vault path": os.path.relpath(vault.path, os.getcwd()),
        "notes": len(vault.notes()),
        "attachments": len(vault.attachments()),
        "tags": sorted(vault.tags()),
        "link_count": count_links(vault),
    }

def display_info(info: dict):
    max_len = max(len(k) for k in info.keys())
    for k, v in info.items():
        print(f"{BOLD}{k.capitalize():{max_len}}{RESET} : {v}")


def main():

    parser = argparse.ArgumentParser(description=sys.modules[__name__].__doc__)
    parser.add_argument("vault_path", type=str, help="Path to the Obsidian vault")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed information about the vault")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--ignore", type=str, default=None, help="Comma seperated list of files and directories to ignore (globs work)")
    parser.add_argument("--ignore-file", type=str, default=None, help="Path to ignore file (relative to vault or absolute)")

    args = parser.parse_args()

    if args.ignore: args.ignore = args.ignore.split(",")
    else          : args.ignore = []

    vault = ovault.Vault(args.vault_path, ignore=args.ignore, ignore_file=args.ignore_file)

    match args.verbose:
        case True : info = get_verbose_info(vault)
        case False: info = get_info(vault)

    match args.json:
        case True: print(json.dumps(info, indent=4))
        case False: display_info(info)

if __name__ == "__main__":
    main()

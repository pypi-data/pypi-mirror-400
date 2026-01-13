"""
Rename pasted images in the vault based on the note they are pasted into.

Each image will be named using the above heading if it exists, otherwise the note name is used.
"""

__util__ = True

import ovault
import sys
import argparse
import re
from pathlib import Path

from ovault.ansi import *

def is_pasted_image(path: Path) -> bool:
    return not re.match(r"Pasted image \d{14}\.png", path.name) is None


warnings = []

def warn(msg: str):
    global warnings
    warnings.append(f"{YELLOW}Warning: {msg}{RESET}")

def determine_name(vault: ovault.Vault, attachment: ovault.Attachment, note: ovault.Note) -> str:
    tokens = note.all_tokens();

    link_token_index = None

    for i, token in enumerate(tokens):
        if not isinstance(token, token.InternalLink): continue
        linked = vault.attachment(token.link.dest)
        if linked is None: continue
        if linked.path != attachment.path: continue
        link_token_index = i
        break

    if link_token_index is None:
        warn(f"Could not find link to attachment '{attachment.path}' in note '{note.name}'. Using note name.")
        return note.name

    # Iterate backwards from the link token to find the nearest heading
    heading = None
    for i in range(link_token_index - 1, -1, -1):
        token: ovault.Token = tokens[i]
        match token:
            case token.Header():
                if note.name in token.heading: heading = token.heading
                else: heading = note.name + "-" + token.heading
            case _: continue

        break

    # Use note name if no heading found
    if heading is None: heading = note.name

    return heading

def filenameify(name: str) -> str:
    out = ""
    for c in name:
        if c.isalnum() or c in [' ', '-', '_']:
            out += c
    return out.strip().replace(' ', '-')


def main():
    parser = argparse.ArgumentParser(description=sys.modules[__name__].__doc__)
    parser.add_argument("vault_path", type=str, help="Path to the Obsidian vault")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done, but don't actually rename anything.")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip the backup warning prompt.")

    args = parser.parse_args()

    if not args.dry_run and not args.yes:
        ovault._backup_warning()

    vault = ovault.Vault(args.vault_path)

    for attachment in sorted(vault.attachments()):
        path = Path(attachment.path);
        if not is_pasted_image(path): continue

        if len(attachment.backlinks) > 1:
            warn(f"Attachment '{attachment.path}' was skipped, it has multiple backlinks.")
            continue

        if len(attachment.backlinks) == 0:
            warn(f"Attachment '{attachment.path}' was skipped, it has no backlinks. Skipping.")
            continue

        note = vault.note(list(attachment.backlinks)[0])

        better_name_base = determine_name(vault, attachment, note)
        better_name_base = filenameify(better_name_base)

        exists = lambda name: vault.attachment(name + ".png") is not None

        better_name = better_name_base

        count = 1
        while exists(better_name):
            better_name = f"{better_name_base}-{count}"
            count += 1

        new_path = path.with_name(better_name + ".png")

        msg = f"[note: {note.name}] {path} -> {new_path}"
        if args.dry_run: msg = "[DRY RUN] " + msg
        print(msg)

        if not args.dry_run:
            vault.rename(str(path), str(new_path))

    if len(warnings) > 0:
        print(file=sys.stderr)
        for w in warnings:
            print(w, file=sys.stderr)


if __name__ == "__main__":
    main()

"""
Check all external links to websites in an Obsidian vault and report any broken links.
"""

__util__ = True

import ovault
import sys
import os

from ovault.ansi import *

def main():
    ovault._import_extra("requests")
    import requests

    if len(sys.argv) != 2:
        submod_name = os.path.basename(__file__.rstrip(".py"))
        print(f"Usage: python -m {__package__}.{submod_name} <vault_or_note_path>")
        sys.exit(1)

    # Set the user agent to mimic a real browser
    HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0'}

    path = sys.argv[1]

    notes = None

    if os.path.isdir(path):
        vault = ovault.Vault(path)
        notes = vault.notes()
    elif os.path.isfile(path) and path.endswith(".md"):
        notes = [ovault.Note(path)]

    if not notes:
        print(f"Error: No notes found in the specified path '{path}'.")
        sys.exit(1)

    broken_links = []

    # Prints centered text in terminal width using '=' characters
    def label(msg, color=None):
        if color: print(color, end="")
        cols = os.get_terminal_size().columns
        left_pad = (cols - len(msg)) // 2 - 1
        right_pad = (cols - len(msg)) - left_pad - 2
        print(f"\n{'=' * left_pad} {msg} {'=' * right_pad}{RESET}")
        if color: print(RESET, end="")

    count = 0

    for note in notes:

        note_links = [token.link for token in note.all_tokens() if isinstance(token, token.ExternalLink)]

        if len(note_links) == 0: continue

        label(f"{note.name} ({str(note.path)})", color=BLUE)

        for link in note_links:
            url = link.url

            print(f"    Checking '{url}'...", end=' ', flush=True)

            if not url.startswith("http"):
                print(f"{YELLOW}SKIPPED{RESET}")
                continue

            count += 1

            try:
                resp = requests.get(url, headers=HEADERS, timeout=5)
            except requests.RequestException as e:
                print(f"{RED}INVALID URL{RESET} ({e})")
                continue
            if resp.status_code == 200:
                print(f"{GREEN}OK{RESET}")
            else:
                broken_links.append((note, url, resp.status_code))
                print(f"{RED}FAILED{RESET} ({resp.status_code})")

    print(f"\nChecked {count} links in {len(notes)} notes.\n")

    if not broken_links:
        print(f"{GREEN}All external links are valid!{RESET}")
        exit(0)

    print(RED, end="")
    print(f"Broken links found:")
    for note, url, status in broken_links:
        print(f"    {note.name} ({note.path}): {url} (status code: {status})")
    print(RESET, end="")

    exit(1)


if __name__ == "__main__":
    main()

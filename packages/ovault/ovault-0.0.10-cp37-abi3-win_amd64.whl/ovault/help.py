"""
Show a list of all utility modules included in `ovault`.
"""

__util__ = True

from pathlib import Path
import importlib

from ovault.ansi import *

def main():

    directory = Path(__file__).parent
    modules = []
    for file in directory.iterdir():
        module_name = None

        if file.suffix == ".py":
            module_name = file.stem

        if (file / "__init__.py").exists():
            module_name = file.name

        if not module_name: continue
        module = importlib.import_module(f".{module_name}", package=__package__)

        if not '__util__' in dir(module): continue
        if not module.__util__: continue
        modules.append((module_name, module.__doc__))

    max_len = max(len(name) for name, _ in modules)

    print(
        "OVault provies a few utilties out of the box.\n\n"
        "You can run them like so: `python3 -m ovault.<module>`\n"
    )

    print("Available modules:")

    for mod, doc in modules:
        doc = doc.strip().split("\n")[0] if doc else "No description."
        print(f"    {BLUE}ovault.{mod:{max_len}}{RESET} : {doc}")

if __name__ == "__main__":
    main()

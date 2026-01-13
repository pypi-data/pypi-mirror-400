"""
Visualize your Obsidian vault graph using pyvis.
"""

__util__ = True

import ovault

import argparse
import sys
import os
import colorsys
from pathlib import Path

from types import ModuleType as Module

def hsv_to_hex(h: float, s: float, v: float) -> str:
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return '#{:02x}{:02x}{:02x}'.format(int(r * 255), int(g * 255), int(b * 255))

TagColorMap = dict[str, tuple[str, int]]

def generate_tag_colors(vault: ovault.Vault) -> TagColorMap:
    tags = vault.tags()
    tag_colors = {}
    for i, tag in enumerate(sorted(tags)):
        hue = i / len(tags)
        saturation = 0.6
        value = 0.9
        rgb = hsv_to_hex(hue, saturation, value)
        priority = -len(vault.get_notes_by_tag(tag))
        tag_colors[tag] = (rgb, priority)
    return tag_colors

# Choose the color based on the highest priority tag
def choose_color(tags: list[str], tag_colors: TagColorMap) -> str:
    if not tags: return '#999999'
    best_tag = max(tags, key=lambda t: tag_colors[t][1])
    return tag_colors[best_tag][0]

def main():
    ovault._import_extra("pyvis")
    from pyvis.network import Network

    def populate_graph(net: Network, vault: ovault.Vault, tag_colors: TagColorMap) -> None:
        for note in vault.notes():
            size = len(note.links) + len(note.backlinks) + 5,
            color = choose_color(note.tags, tag_colors)

            net.add_node(str(note.path),
                         size=size,
                         label=note.name,
                         title=str(note.path),
                         color=color)

        for attachment in vault.attachments():
            size = len(note.backlinks) + 3,
            net.add_node(str(attachment.path),
                         size=size,
                         label=Path(attachment.path).name,
                         title=str(attachment.path),
                         color="#7a7a77")

        for note in vault.notes():
            for link in note.links:
                linked = vault.note(link)
                if not linked: linked = vault.attachment(link)
                if not linked: continue

                net.add_edge(str(note.path), str(linked.path))


    parser = argparse.ArgumentParser(description=sys.modules[__name__].__doc__)
    parser.add_argument("vault", type=str, help="Path to your Obsidian vault")
    parser.add_argument("--output", "-o", type=str, help="Output HTML file", default="graph")
    parser.add_argument("--buttons", "-b", default=False, action="store_true", help="Show physics buttons")

    args = parser.parse_args()

    vault = ovault.Vault(args.vault)

    net = Network(directed=True, height = "100vh", width="100vw", bgcolor="#222222", font_color="white")
    net.barnes_hut(
        gravity=-30000,
        central_gravity=2.0,
        spring_length=95,
        spring_strength=0.10,
        overlap=0.10,
        damping=0.25,
    )
    net.options.physics.stabilization.enabled = True
    net.options.physics.stabilization.iterations = min(len(vault.notes()) * 0.25, 500)

    if args.buttons:
        net.show_buttons(filter_=['physics'])

    tag_colors = generate_tag_colors(vault)

    populate_graph(net, vault, tag_colors)


    os.makedirs(args.output, exist_ok=True)
    os.chdir(args.output)
    net.write_html("index.html", notebook=False)
    print(f"Graph saved to '{args.output}'.")



if __name__ == "__main__":
    main()


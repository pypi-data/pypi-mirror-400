import argparse
import sys
import os
from pathlib import Path

import ovault

import ovault.to_html.html as html

CSS_FILE_NAME = "style.css"

CSS_FILE = os.path.join(os.path.dirname(__file__), CSS_FILE_NAME)

def vault_path_to_site_path(note_path: str, site_dir: str = "") -> str:
    note_path = Path(note_path)

    if note_path.suffix == ".md":
        note_path = Path(note_path).with_suffix(".html")

    if site_dir == "": return str(note_path)
    return str(os.path.join(site_dir, note_path))

def emded_note(w: html.HtmlWriter, vault: ovault.Vault, note: ovault.Note) -> str:
    w.write_line('<div class="embedded-note">', indent=True)
    w.write_line(f'<a href="/{vault_path_to_site_path(note.path)}" class="embedded-note-link">', indent=True)
    w.write_line(f'<div class="embedded-note-title">{note.name}</div>')
    w.write_line('</a>', dedent=True)

    w.write_line('<div class="embedded-note-content">', indent=True)
    tokens_to_html(vault, w, note.tokens())
    w.write_line('</div>', dedent=True)

    w.write_line('</div>', dedent=True)


def token_to_html(vault: ovault.Vault, w: html.HtmlWriter, token: ovault.Token) -> str:
    match token:
        case token.Frontmatter():
            pass

        case token.Text():
            for line in token.text.splitlines():
                w.write_line(line)

        case token.Tag():
            w.write_line(f'<span class="tag">#{token.tag}</span>')

        case token.InternalLink():
            link = token.link

            if link.options:
                print(f"WARNING: Option(s) '{link.options}' were ignored in internal link to '{link.dest}'.")

            dest = None

            dest_note       = None
            dest_attachment = None

            if link.dest != "":
                dest_note = vault.note(link.dest)
                if dest_note: dest = dest_note.path

                dest_attachment = vault.attachment(link.dest)
                if dest_attachment: dest = dest_attachment.path

                if dest is None:
                    print(f"WARNING: Internal link to '{link.dest}' not found in vault.")

            if dest is None:
                dest = str(link.dest)
            else:
                dest = vault_path_to_site_path(dest)


            if link.position:
                dest += "#" + link.position

            dest = "/" + dest

            if link.render:
                if dest_note:
                    emded_note(w, vault, dest_note)
                elif dest_attachment and str(dest_attachment.path).lower().endswith(".pdf"):
                    w.write_line(f'<iframe class="embedded-pdf" src="{vault_path_to_site_path(dest_attachment.path)}" width="100%" height="600px"></iframe>')
                else:
                    w.write_line(html.img(dest));
                return

            if len(link.dest) == 0 and link.position:
                dest = "#" + link.position

            text = dest.removesuffix(".html").removeprefix("#").removeprefix("/")
            if link.show_how: text = link.show_how

            w.write_line(html.a(dest, text))

        case token.ExternalLink():
            link = token.link

            if link.render: print("WARNING: ExternalLink with render=True not implemented yet.")

            if link.options:
                print(f"WARNING: Option(s) '{link.options}' were ignored in external link to '{link.url}'.")

            url = link.url

            if link.position:
                url += f"#{link.position}"

            w.write_line(html.a(url, link.show_how))

        case token.Header():
            w.write_line(html.h(token.level, token.heading, id=token.heading))

        case token.Bold():
            w.write_line(f'<strong>', indent=True)
            tokens_to_html(vault, w, token.tokens)
            w.write_line(f'</strong>', dedent=True)

        case token.Italic():
            w.write_line(f'<i>', indent=True)
            tokens_to_html(vault, w, token.tokens)
            w.write_line(f'</i>', dedent=True)

        case token.Strikethrough():
            w.write_line(f'<s>', indent=True)
            tokens_to_html(vault, w, token.tokens)
            w.write_line(f'</s>', dedent=True)

        case token.Highlight():
            w.write_line(f'<mark>', indent=True)
            tokens_to_html(vault, w, token.tokens)
            w.write_line(f'</mark>', dedent=True)

        case token.InlineCode():
            w.write_line(f'<code>{token.code}</code>')

        case token.InlineMath():
            w.write_line(f'\\({token.latex}\\)')

        case token.DisplayMath():
            w.write_line(f'\\[{token.latex}\\]')

        case token.List():

            w.write_line('<ul>', indent=True)
            for item in token.items:

                if item.indent != 0:
                    print("WARNING: Nested lists not implemented yet.")

                w.write_line('<li>', indent=True)
                tokens_to_html(vault, w, item.tokens)
                w.write_line('</li>', dedent=True)


            w.write_line('</ul>', dedent=True)

        case token.CheckList():
            w.write_line('<div class="checklist">', indent=True)
            for item in token.items:

                if item.indent != 0:
                    print("WARNING: Nested checked lists not implemented yet.")

                extra = '';
                if item.checked: extra = 'checked'
                w.write_line(f'<input type="checkbox" onclick="return false;" {extra}>');

                w.write_line('<label>', indent=True)
                tokens_to_html(vault, w, item.tokens)
                w.write_line('</label><br>', dedent=True)

            w.write_line('</div>', dedent=True)

        # TODO: Re-enumerate numeric lists
        case token.NumericList():
            w.write_line('<ol>', indent=True)
            for item in token.items:

                if item.indent != 0:
                    print("WARNING: Nested numeric lists not implemented yet.")

                w.write_line('<li>', indent=True)
                tokens_to_html(vault, w, item.tokens)
                w.write_line('</li>', dedent=True)

            w.write_line('</ol>', dedent=True)

        case token.Callout():
            clases = ["callout", f'callout-kind-{token.callout.kind}']

            if token.callout.foldable: clases.append("foldable")

            w.write_line(f'<details class="{' '.join(clases)}">', indent=True)
            w.write_line(f'<summary class="callout-title">{token.callout.title}</summary>')

            w.write_line('<div class="callout-content">', indent=True)
            tokens_to_html(vault, w, token.callout.tokens)
            w.write_line('</div>', dedent=True)

            w.write_line('</details>', dedent=True)

        case token.Quote():
            w.write_line('<blockquote>', indent=True)
            tokens_to_html(vault, w, token.tokens)
            w.write_line('</blockquote>', dedent=True)

        case token.Code():
            w.write_line('<pre><code>')
            w.indent()
            for line in token.code.splitlines():
                w.write_line(line)
            w.dedent()
            w.write_line('</code></pre>')

        case token.Divider():
            w.write_line('<hr>')

        case token.Escaped():
            w.write_line(token.character)

        case token.Comment():
            pass

        case other:
            raise NotImplementedError(f"Unknown token type: {type(other)}")

def tokens_to_html(vault: ovault.Vault, w: html.HtmlWriter, tokens: list[ovault.Token]) -> None:
    for token in tokens:
        token_to_html(vault, w, token)

def html_head(w: html.HtmlWriter, title: str) -> None:
    w.write_line("<head>", indent=True)
    w.write_line('<meta charset="UTF-8">')
    w.write_line(f"<title>{title.title()}</title>")

    w.write_line(f'<link rel="stylesheet" href="/{CSS_FILE_NAME}">')

    # LaTeX support via KaTeX
    w.write_line(f'<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>')
    w.write_line('<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js" \
            onload="renderMathInElement(document.body);"></script>')
    w.write_line('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">')

    w.write_line("</head>", dedent=True)

def create_sidebar(w: html.HtmlWriter, vault: ovault.Vault, note: ovault.Note) -> None:

    w.write_line('<aside class="sidebar">')
    w.write_line('<h3>Tags</h3>')
    w.write_line('<div class="tag-list">')

    if len(note.tags) == 0:
        w.write_line('<div>(no tags)</div>')

    for tag in note.tags:
        w.write_line('<div class="tag-item">', indent=True)
        w.write_line(f'<span class="tag">#{tag}</span>')

    w.write_line('</div>', dedent=True)

    w.write_line('</div>')
    w.write_line('')
    w.write_line('<h3>Links</h3>')
    w.write_line('<ul>')

    for link in note.links:

        dest = None
        disp = None

        linked_note = vault.note(link)
        if linked_note:
            dest = linked_note.path
            disp = linked_note.name

        linked_attachment = vault.attachment(link)
        if linked_attachment:
            dest = linked_attachment.path
            disp = os.path.basename(linked_attachment.path)

        if dest is not None and disp is not None:
            w.write_line(f'<li><a href="/{vault_path_to_site_path(dest)}">{disp}</a></li>')


    w.write_line('</ul>')
    w.write_line('')
    w.write_line('<h3>Backlinks</h3>')
    w.write_line('<ul>')

    for backlink in note.backlinks:
        backlink_note = vault.note(backlink)
        w.write_line(f'<li><a href="/{vault_path_to_site_path(backlink_note.path)}">{backlink_note.name}</a></li>')

    w.write_line('</ul>')
    w.write_line('</aside>')

def convert_note_to_html(vault: ovault.Vault, note: ovault.Note, site_dir: str, filename_title=False) -> str:
    output_path = vault_path_to_site_path(note.path, site_dir)

    w = html.HtmlWriter()
    w.write_line("<!DOCTYPE html>")
    w.write_line("<html>", indent=True)

    html_head(w, note.name)

    w.write_line("<body><main>", indent=True)

    if filename_title: w.write_line(f"<h1>{note.name}</h1>")

    tokens_to_html(vault, w, note.tokens())

    create_sidebar(w, vault, note)

    w.write_line("</main></body>", dedent=True)

    w.write_line("</html>", dedent=True)

    w.save_to_file(output_path)



def convert_vault_to_html(vault_path: str, site_dir: str, args: argparse.Namespace) -> None:

    if args.verbose:
        print(f"Converting vault at '{vault_path}' to HTML site in '{site_dir}'...")

    os.makedirs(site_dir, exist_ok=True)

    if not os.path.isdir(vault_path):
        print(f"ERROR: Vault path '{vault_path}' is not a directory.")
        exit(1)

    # Check that the directory os empty
    if len(os.listdir(site_dir)) > 0:
        print(f"ERROR: Output directory '{site_dir}' is not empty.")
        exit(1)

    vault = ovault.Vault(vault_path)

    # Convert notes
    for note in sorted(vault.notes()):
        if args.verbose: print(f"  Converting note '{note.path}'...")
        convert_note_to_html(vault, note, site_dir)

    # Copy attachments
    for attachment in vault.attachments():
        if args.verbose: print(f"  Copying attachment '{attachment.path}'...")
        dest_path = vault_path_to_site_path(attachment.path, site_dir)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        with open(attachment.full_path(), "rb") as src_file:
            with open(dest_path, "wb") as dest_file:
                dest_file.write(src_file.read())

    # Add CSS file
    if args.verbose: print(f"  Adding CSS file...")
    dest_css_path = os.path.join(site_dir, CSS_FILE_NAME)
    with open(CSS_FILE, "r", encoding="utf-8") as src_css_file:
        with open(dest_css_path, "w", encoding="utf-8") as dest_css_file:
            dest_css_file.write(src_css_file.read())

    if args.verbose:
        print("DONE!")


def main():
    parser = argparse.ArgumentParser(description=sys.modules[__name__].__doc__)

    # Arguments
    parser.add_argument("vault", type=str, help="Path to your Obsidian vault")
    parser.add_argument("--output", "-o", type=str, help="Output directory for the HTML site", default="site")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    convert_vault_to_html(args.vault, args.output, args)

if __name__ == "__main__":
    main()

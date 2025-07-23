#!/usr/bin/python3
"""This module handles all database connections."""

import sys
import os
import re
import hashlib


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: ./markdown2html.py README.md README.html",
            file=sys.stderr
        )
        exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.isfile(input_file):
        print(
            f"Missing {input_file}",
            file=sys.stderr
        )
        exit(1)

    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            in_ul = False
            in_ol = False
            paragraph_lines = []

            def convert_formatting(text):
                text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
                text = re.sub(r'__(.+?)__', r'<em>\1</em>', text)

                def md5_repl(match):
                    raw = match.group(1)
                    md5_hash = hashlib.md5(raw.encode())
                    return md5_hash.hexdigest()

                text = re.sub(
                    r'\[\[(.+?)\]\]',
                    md5_repl,
                    text
                )

                def remove_c(match):
                    return re.sub(r'[cC]', '', match.group(1))

                text = re.sub(r'\(\((.+?)\)\)', remove_c, text)
                return text

            def close_lists():
                nonlocal in_ul, in_ol
                if in_ul:
                    outfile.write("</ul>\n")
                    in_ul = False
                if in_ol:
                    outfile.write("</ol>\n")
                    in_ol = False

            def write_paragraph():
                nonlocal paragraph_lines
                if paragraph_lines:
                    outfile.write("<p>\n")
                    for i, line in enumerate(paragraph_lines):
                        line = convert_formatting(line)
                        if i > 0:
                            outfile.write("<br/>\n")
                        outfile.write(f"{line}\n")
                    outfile.write("</p>\n")
                    paragraph_lines = []

            for line in infile:
                stripped = line.strip()

                if stripped == "":
                    write_paragraph()
                    continue

                if stripped.startswith('#'):
                    level = len(stripped) - len(stripped.lstrip('#'))
                    if (
                        1 <= level <= 6 and
                        len(stripped) > level and
                        stripped[level] == ' '
                    ):
                        write_paragraph()
                        close_lists()
                        content = convert_formatting(
                            stripped[level + 1:].strip()
                        )
                        outfile.write(
                            f"<h{level}>{content}</h{level}>\n"
                        )
                        continue

                if stripped.startswith('- '):
                    write_paragraph()
                    if in_ol:
                        outfile.write("</ol>\n")
                        in_ol = False
                    if not in_ul:
                        outfile.write("<ul>\n")
                        in_ul = True
                    content = convert_formatting(stripped[2:].strip())
                    outfile.write(f"<li>{content}</li>\n")
                    continue

                if stripped.startswith('* '):
                    write_paragraph()
                    if in_ul:
                        outfile.write("</ul>\n")
                        in_ul = False
                    if not in_ol:
                        outfile.write("<ol>\n")
                        in_ol = True
                    content = convert_formatting(stripped[2:].strip())
                    outfile.write(f"<li>{content}</li>\n")
                    continue

                close_lists()
                paragraph_lines.append(stripped)

            write_paragraph()
            close_lists()

        exit(0)

    except Exception as e:
        print(
            f"Error: {e}",
            file=sys.stderr
        )
        exit(1)


if __name__ == "__main__":
    main()

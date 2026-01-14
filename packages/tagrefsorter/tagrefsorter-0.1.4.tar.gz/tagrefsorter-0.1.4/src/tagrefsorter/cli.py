#!/usr/bin/env python3
import argparse
import pathlib
import sys
import nbformat
import re
from typing import Callable
from dataclasses import dataclass, field
from . import __version__


def parse_args():
    parser = argparse.ArgumentParser(
        description="Read a Jupyter Notebook (.ipynb) file and normalize LaTeX \\tag numbering"
    )
    parser.add_argument(
        "notebook",
        type=pathlib.Path,
        help="Path to the .ipynb file to be modified",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        help="Path to save the modified .ipynb file (if not provided, overwrites the input file)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Show the program version and exit",
    )
    return parser.parse_args()


_LATEX_BLOCK = re.compile(r"\$\$(.*?)\$\$", flags=re.DOTALL)
_LATEX_ALIGN = re.compile(r"\\begin\{align\}(.*?)\\end\{align\}", flags=re.DOTALL)
_LATEX_TAG = re.compile(r"\\tag\{(.*?)\}")


@dataclass
class EditState:
    update_map: dict[str, str] = field(default_factory=dict)
    next_tag: int = 1


def update_nb(nb: nbformat.NotebookNode) -> nbformat.NotebookNode:
    state = EditState()

    def sub_editor(subtex: str, align: bool) -> str:
        match = _LATEX_TAG.search(subtex)
        if match:
            old_tag = match.group(1)
            new_tag = str(state.next_tag)
            if old_tag != new_tag:
                state.update_map[old_tag] = new_tag
            if align:
                subtex = _LATEX_TAG.sub(rf"\\\\tag{{{new_tag}}}", subtex)
            else:
                subtex = _LATEX_TAG.sub(rf"\\tag{{{new_tag}}}", subtex)
        else:
            new_tag = str(state.next_tag)
            if align:
                subtex += rf"\\tag{{{new_tag}}}"
            else:
                subtex += rf"\tag{{{new_tag}}}"
        state.next_tag += 1
        return subtex

    def editor(latex: str) -> str:
        match = _LATEX_ALIGN.search(latex)
        if match:
            align_body = match.group(1)
            parts = re.split(r"(\\\\)", align_body)
            new_parts = []
            for part in parts:
                if part == r"\\":
                    new_parts.append(r"\\\\")
                else:
                    new_parts.append(sub_editor(part, align=True))
            new_align_body = "".join(new_parts)
            latex = _LATEX_ALIGN.sub(
                rf"\\begin{{align}}{new_align_body}\\end{{align}}",
                latex,
            )
        else:
            latex = sub_editor(latex, align=False)
        return latex

    def edit_latex_blocks(text: str, editor: Callable[[str], str]) -> str:
        def repl(m: re.Match) -> str:
            inner = m.group(1)
            new_inner = editor(inner)
            return f"$${new_inner}$$\n"

        return _LATEX_BLOCK.sub(repl, text)

    for cell in nb.cells:
        if cell.cell_type == "markdown":
            cell.source = edit_latex_blocks(cell.source, editor)

    for cell in nb.cells:
        if cell.cell_type == "markdown":
            for old_tag, new_tag in state.update_map.items():
                cell.source = re.sub(
                    rf"\$\({re.escape(old_tag)}\)\$",
                    rf"$({new_tag})$",
                    cell.source,
                )

    return nb


def main():
    args = parse_args()
    nb_path: pathlib.Path = args.notebook
    onb_path: pathlib.Path = args.output if args.output else nb_path

    if not nb_path.exists():
        print(f"Error: file not found: {nb_path}", file=sys.stderr)
        sys.exit(1)

    if nb_path.suffix != ".ipynb":
        print("Error: input file must be .ipynb", file=sys.stderr)
        sys.exit(1)
    
    if args.output and onb_path.suffix != ".ipynb":
        print("Error: output file must be .ipynb", file=sys.stderr)
        sys.exit(1)

    nb = nbformat.read(nb_path, as_version=4)
    updated_nb = update_nb(nb)
    nbformat.write(updated_nb, onb_path)

    if args.output:
        print(f"Written: {onb_path}")
    else:
        print(f"Overwritten: {nb_path}")

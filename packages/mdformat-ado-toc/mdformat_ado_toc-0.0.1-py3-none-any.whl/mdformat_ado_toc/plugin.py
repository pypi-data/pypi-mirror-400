from __future__ import annotations

import re
from typing import TYPE_CHECKING

from markdown_it import MarkdownIt
from markdown_it.rules_block import StateBlock

if TYPE_CHECKING:
    from mdformat.renderer import RenderContext, RenderTreeNode
    from mdformat.renderer.typing import Render


def _toc_block_rule(
    state: StateBlock, start_line: int, end_line: int, silent: bool
) -> bool:
    """Parse [[_TOC_]] as a custom block."""
    pos = state.bMarks[start_line] + state.tShift[start_line]
    maximum = state.eMarks[start_line]

    # Get the line content
    line = state.src[pos:maximum]

    # Check if line contains [[_TOC_]] (with optional whitespace)
    match = re.match(r"^\s*\[\[_TOC_]]\s*$", line)
    if not match:
        return False

    if silent:
        return True

    # Create token
    token = state.push("ado_toc", "", 0)
    token.content = "[[_TOC_]]"
    token.markup = "[[_TOC_]]"
    token.map = [start_line, start_line + 1]

    state.line = start_line + 1
    return True


def update_mdit(mdit: MarkdownIt) -> None:
    """Update the parser to recognize [[_TOC_]] as a custom block."""
    # Insert the rule before the paragraph rule to ensure it takes precedence
    mdit.block.ruler.before(
        "paragraph",
        "ado_toc",
        _toc_block_rule,
    )


def _render_ado_toc(node: RenderTreeNode, context: RenderContext) -> str:
    """Render the Azure DevOps TOC block."""
    return "[[_TOC_]]"


# A mapping from syntax tree node type to a function that renders it.
RENDERERS: dict[str, Render] = {"ado_toc": _render_ado_toc}

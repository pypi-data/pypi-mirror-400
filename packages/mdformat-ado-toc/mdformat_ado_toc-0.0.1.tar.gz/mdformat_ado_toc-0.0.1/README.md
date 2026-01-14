# mdformat-ado-toc

An `mdformat` plugin that preserves Azure DevOps' `[[_TOC_]]` directive.
`mdformat` normally escapes it to `\[\[_TOC_\]\]`. This plugin treats it
as a custom block and renders it back verbatim.

## Problem

Azure DevOps wikis use `[[_TOC_]]` to generate a table of contents. However, when formatting markdown files with `mdformat`, the brackets get escaped to `\[\[_TOC_\]\]`, which breaks the TOC functionality.

## Solution

This plugin registers a custom parser extension that recognizes `[[_TOC_]]` as a special block element and preserves it without escaping during formatting.

## Install

```bash
pip install mdformat-ado-toc
# or from source
pip install -e .
```

## Usage

### Command Line

```bash
mdformat document.md --extensions ado_toc
```

### Python API

```python
import mdformat

text = """
# My Document

[[_TOC_]]

## Section 1
Content here.
"""

formatted = mdformat.text(text, extensions=["ado_toc"])
print(formatted)  # [[_TOC_]] is preserved!
```

## Features

- ✅ Preserves `[[_TOC_]]` without escaping brackets
- ✅ Handles surrounding whitespace correctly
- ✅ Supports multiple TOC markers in one document
- ✅ Works correctly when mixed with other markdown content
- ✅ Uses Python type hints and modern Python syntax

## Testing

```bash
pytest tests/test_plugin.py -v
```

## How It Works

The plugin implements a custom markdown-it parser rule that:
1. Intercepts lines containing `[[_TOC_]]` before they are parsed as paragraphs
2. Creates a custom `ado_toc` token for these lines
3. Renders the token back as the literal string `[[_TOC_]]` without escaping

## License

MIT


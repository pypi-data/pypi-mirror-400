import mdformat

PLUGIN = ["ado_toc"]


def fmt(text: str) -> str:
    return mdformat.text(text, options={"number": False}, extensions=PLUGIN)


def test_preserves_toc_line():
    src = "# Title\n\n[[_TOC_]]\n\n## Section"
    out = fmt(src)
    assert "[[_TOC_]]\n" in out
    assert "\\[\\[_TOC_\\]\\]" not in out


def test_whitespace_tolerant():
    src = "  [[_TOC_]]  \n"
    out = fmt(src)
    # mdformat adds a trailing newline to documents
    assert out.strip() == "[[_TOC_]]"


def test_multiple_occurrences():
    src = "[[_TOC_]]\n\ntext\n\n[[_TOC_]]\n"
    out = fmt(src)
    assert out.count("[[_TOC_]]") == 2


def test_mixed_content():
    src = "# A\n\ntext\n\n[[_TOC_]]\n\n- item"
    out = fmt(src)
    # Verify [[_TOC_]] is preserved and not escaped
    assert "[[_TOC_]]" in out
    assert "\\[\\[_TOC_\\]\\]" not in out


# Edge Cases


def test_toc_at_document_start():
    """Test TOC at the very beginning of the document."""
    src = "[[_TOC_]]\n\n# Title\n\nContent"
    out = fmt(src)
    assert out.startswith("[[_TOC_]]")
    assert "\\[\\[_TOC_\\]\\]" not in out


def test_toc_at_document_end():
    """Test TOC at the very end of the document."""
    src = "# Title\n\nContent\n\n[[_TOC_]]"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "\\[\\[_TOC_\\]\\]" not in out


def test_toc_only_document():
    """Test document containing only [[_TOC_]]."""
    src = "[[_TOC_]]"
    out = fmt(src)
    assert out.strip() == "[[_TOC_]]"


def test_toc_with_tabs():
    """Test TOC with tab characters as whitespace."""
    src = "\t[[_TOC_]]\t\n"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "\\[\\[_TOC_\\]\\]" not in out


def test_toc_case_sensitive():
    """Test that TOC is case-sensitive (lowercase should be escaped)."""
    src = "[[_toc_]]"
    out = fmt(src)
    # Should be escaped because it's not the exact pattern
    assert "\\[\\[_toc_\\]\\]" in out or "[[_toc_]]" not in out


def test_toc_with_extra_brackets():
    """Test that extra brackets are not treated as TOC."""
    src = "[[[_TOC_]]]"
    out = fmt(src)
    # Should not be treated as TOC
    assert out.count("[[_TOC_]]") == 0 or "\\[" in out


def test_toc_with_spaces_inside():
    """Test that spaces inside brackets break the pattern."""
    src = "[[ _TOC_ ]]"
    out = fmt(src)
    # Should be escaped or modified
    assert "\\[" in out or out.strip() != "[[ _TOC_ ]]"


def test_toc_inline_with_text():
    """Test that TOC inline with text on same line is not recognized."""
    src = "text [[_TOC_]] more text"
    out = fmt(src)
    # Should be escaped because it's inline
    assert "\\[\\[_TOC_\\]\\]" in out


def test_toc_with_code_block():
    """Test TOC mixed with code blocks."""
    src = "# Title\n\n[[_TOC_]]\n\n```python\ncode\n```"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "```python" in out


def test_toc_with_blockquote():
    """Test TOC mixed with blockquotes."""
    src = "[[_TOC_]]\n\n> Quote text\n\n## Section"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "> Quote text" in out


def test_toc_with_list():
    """Test TOC mixed with lists."""
    src = "# Title\n\n- item 1\n- item 2\n\n[[_TOC_]]\n\n- item 3"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "- item 1" in out


def test_toc_with_numbered_list():
    """Test TOC mixed with numbered lists."""
    src = "[[_TOC_]]\n\n1. first\n2. second"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "1. first" in out or "1.  first" in out


def test_toc_with_links():
    """Test TOC with markdown links."""
    src = "[[_TOC_]]\n\n[link](url)\n\n## Section"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "[link](url)" in out


def test_toc_with_images():
    """Test TOC with markdown images."""
    src = "[[_TOC_]]\n\n![alt](image.png)"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "![alt](image.png)" in out


def test_toc_with_horizontal_rule():
    """Test TOC with horizontal rules."""
    src = "# Title\n\n[[_TOC_]]\n\n---\n\n## Section"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    # mdformat may convert --- to different horizontal rule representations
    assert "---" in out or "***" in out or "___" in out


def test_toc_with_emphasis():
    """Test TOC near emphasis/bold text."""
    src = "[[_TOC_]]\n\n**bold** and *italic*"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "**bold**" in out


def test_three_consecutive_tocs():
    """Test three TOCs in a row."""
    src = "[[_TOC_]]\n\n[[_TOC_]]\n\n[[_TOC_]]"
    out = fmt(src)
    assert out.count("[[_TOC_]]") == 3


def test_toc_between_headings():
    """Test TOC between various heading levels."""
    src = "# H1\n\n## H2\n\n[[_TOC_]]\n\n### H3\n\n#### H4"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "# H1" in out
    assert "#### H4" in out


def test_toc_with_table():
    """Test TOC with markdown table."""
    src = "[[_TOC_]]\n\n| Col1 | Col2 |\n|------|------|\n| A    | B    |"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "| Col1 | Col2 |" in out


def test_empty_lines_around_toc():
    """Test TOC with multiple empty lines around it."""
    src = "# Title\n\n\n\n[[_TOC_]]\n\n\n\n## Section"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_with_html_comment():
    """Test TOC with HTML comments."""
    src = "[[_TOC_]]\n\n<!-- comment -->\n\n## Section"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_mixed_brackets_not_toc():
    """Test that similar but different bracket patterns are not TOC."""
    test_cases = [
        "[[_TOC]]",  # Missing underscore at end
        "[[TOC_]]",  # Missing underscore at start
        "[_TOC_]",  # Single brackets
        "[[_TOC_]",  # Missing closing bracket
        "[[_TOC_]]_",  # Extra underscore outside
    ]
    for src in test_cases:
        out = fmt(src)
        # These should all be escaped or modified
        assert out.strip() != src or "\\[" in out


# Additional Edge Cases


def test_toc_with_unicode_content():
    """Test TOC with Unicode characters in surrounding content."""
    src = "# 日本語\n\n[[_TOC_]]\n\n## Тест\n\nصفحة"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "\\[\\[_TOC_\\]\\]" not in out


def test_toc_with_nested_lists():
    """Test TOC with nested list structures."""
    src = "[[_TOC_]]\n\n- item 1\n  - nested 1\n    - deeply nested\n- item 2"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "- item 1" in out


def test_toc_inside_blockquote_not_preserved():
    """Test that TOC inside blockquote is NOT treated as block-level TOC."""
    src = "> [[_TOC_]]"
    out = fmt(src)
    # The TOC pattern inside a blockquote is not recognized as a block-level TOC,
    # but it's not escaped either - it remains as inline text within the blockquote
    assert "> [[_TOC_]]" in out


def test_toc_inside_list_not_preserved():
    """Test that TOC inside list item is NOT treated as block-level TOC."""
    src = "- [[_TOC_]]"
    out = fmt(src)
    # The TOC pattern inside a list is not recognized as a block-level TOC,
    # but it's not escaped either - it remains as inline text within the list
    assert "- [[_TOC_]]" in out


def test_toc_after_code_fence():
    """Test TOC immediately after closing code fence."""
    src = "```\ncode\n```\n[[_TOC_]]"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "\\[\\[_TOC_\\]\\]" not in out


def test_toc_before_code_fence():
    """Test TOC immediately before code fence."""
    src = "[[_TOC_]]\n```\ncode\n```"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "\\[\\[_TOC_\\]\\]" not in out


def test_toc_with_html_tags():
    """Test TOC with HTML tags in document."""
    src = "[[_TOC_]]\n\n<div>content</div>\n\n## Section"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_with_reference_links():
    """Test TOC with reference-style links."""
    src = "[[_TOC_]]\n\n[link][ref]\n\n[ref]: url"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_with_footnotes():
    """Test TOC with footnote references."""
    src = "[[_TOC_]]\n\nText[^1]\n\n[^1]: footnote"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_with_task_lists():
    """Test TOC with GitHub-style task lists."""
    src = "[[_TOC_]]\n\n- [ ] unchecked\n- [x] checked"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_empty_document():
    """Test formatting an empty document (shouldn't crash)."""
    src = ""
    out = fmt(src)
    assert out == ""


def test_whitespace_only_document():
    """Test document with only whitespace."""
    src = "   \n\n  \t\n"
    out = fmt(src)
    # Should format to empty or minimal whitespace
    assert "[[_TOC_]]" not in out


def test_very_long_document_with_toc():
    """Test TOC in a very long document."""
    sections = "\n\n".join([f"## Section {i}\n\nContent {i}" for i in range(100)])
    src = f"# Title\n\n[[_TOC_]]\n\n{sections}"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert out.count("## Section") == 100


def test_toc_with_setext_headings():
    """Test TOC with setext-style headings (underlined)."""
    src = "Title\n=====\n\n[[_TOC_]]\n\nSection\n-------"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_multiple_spaces_between_brackets():
    """Test that multiple spaces inside break the pattern."""
    src = "[[  _TOC_  ]]"
    out = fmt(src)
    assert "\\[" in out or out.strip() != src


def test_newline_before_closing_brackets():
    """Test that newline inside brackets breaks pattern."""
    src = "[[_TOC_\n]]"
    out = fmt(src)
    assert "[[_TOC_]]" not in out or "\\[" in out


def test_toc_with_backslashes():
    """Test TOC near backslash characters."""
    src = "[[_TOC_]]\n\n\\*not emphasis\\*"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_with_autolinks():
    """Test TOC with autolinks."""
    src = "[[_TOC_]]\n\n<https://example.com>"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_mixed_case_variations():
    """Test various case variations to ensure only exact match works."""
    variations = [
        "[[_TOC_]]",  # Correct - should be preserved
        "[[_Toc_]]",  # Wrong case
        "[[_tOc_]]",  # Wrong case
        "[[_ToC_]]",  # Wrong case
    ]
    for src in variations:
        out = fmt(src)
        if src == "[[_TOC_]]":
            assert "[[_TOC_]]" in out and "\\[\\[_TOC_\\]\\]" not in out
        else:
            # Wrong case should be escaped
            assert "\\[" in out or src not in out


def test_toc_with_definition_lists():
    """Test TOC with definition lists."""
    src = "[[_TOC_]]\n\nTerm\n: Definition"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_after_thematic_break():
    """Test TOC after various thematic break styles."""
    for break_style in ["---", "***", "___", "- - -", "* * *", "_ _ _"]:
        src = f"{break_style}\n\n[[_TOC_]]\n\n## Section"
        out = fmt(src)
        assert "[[_TOC_]]" in out


def test_toc_with_inline_code():
    """Test TOC near inline code."""
    src = "[[_TOC_]]\n\nSome `code` here"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "`code`" in out


def test_toc_with_strikethrough():
    """Test TOC with strikethrough text (if supported)."""
    src = "[[_TOC_]]\n\n~~strikethrough~~"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_five_times():
    """Test document with five TOC markers."""
    src = "\n\n".join(["[[_TOC_]]"] * 5)
    out = fmt(src)
    assert out.count("[[_TOC_]]") == 5


def test_toc_with_leading_zeros():
    """Test that variations with numbers don't match."""
    src = "[[_TOC0_]]"
    out = fmt(src)
    assert "\\[" in out or "[[_TOC0_]]" not in out


def test_toc_with_special_chars_outside():
    """Test TOC with special characters immediately outside."""
    src = "![[_TOC_]]!"
    out = fmt(src)
    # Should be escaped because of surrounding characters
    assert "\\[\\[_TOC_\\]\\]" in out


def test_toc_indented_four_spaces():
    """Test TOC indented by four spaces (might be treated as code)."""
    src = "    [[_TOC_]]"
    out = fmt(src)
    # Four spaces means code block, so it should be preserved as code
    # or the TOC might not be recognized
    assert "[[_TOC_]]" in out  # Could be in code block or parsed


def test_toc_with_hard_line_breaks():
    """Test TOC with hard line breaks (two spaces at end)."""
    src = "[[_TOC_]]  \n\nContent"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_alternating_with_content():
    """Test alternating TOC and content."""
    src = "[[_TOC_]]\n\ntext1\n\n[[_TOC_]]\n\ntext2\n\n[[_TOC_]]"
    out = fmt(src)
    assert out.count("[[_TOC_]]") == 3
    assert "text1" in out
    assert "text2" in out


def test_document_only_tocs():
    """Test document with only multiple TOCs."""
    src = "[[_TOC_]]\n\n[[_TOC_]]\n\n[[_TOC_]]\n\n[[_TOC_]]"
    out = fmt(src)
    assert out.count("[[_TOC_]]") == 4


# Extreme Edge Cases and Malformed Patterns


def test_toc_with_carriage_return():
    """Test TOC with Windows-style line endings."""
    src = "[[_TOC_]]\r\n\r\nContent"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_with_mixed_line_endings():
    """Test TOC with mixed line endings."""
    src = "[[_TOC_]]\r\n\nContent\r\n"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_with_null_bytes():
    """Test that null bytes don't break the parser."""
    src = "[[_TOC_]]\n\nContent"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_with_emoji():
    """Test TOC with emoji in surrounding content."""
    src = "# Title 🎉\n\n[[_TOC_]]\n\n## Section 🚀"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "🎉" in out


def test_toc_pattern_in_code_block():
    """Test that TOC inside code block is not converted."""
    src = "```\n[[_TOC_]]\n```"
    out = fmt(src)
    # Should remain in code block, not converted to block-level TOC
    assert "```" in out
    assert "[[_TOC_]]" in out


def test_toc_pattern_in_inline_code():
    """Test TOC pattern in inline code."""
    src = "Use `[[_TOC_]]` to add table of contents"
    out = fmt(src)
    # Should remain as inline code
    assert "`[[_TOC_]]`" in out


def test_toc_with_rtl_text():
    """Test TOC with right-to-left text."""
    src = "[[_TOC_]]\n\n## مرحبا بك\n\nContent"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "مرحبا بك" in out


def test_toc_with_chinese_japanese_korean():
    """Test TOC with CJK characters."""
    src = "# 中文标题\n\n[[_TOC_]]\n\n## 日本語\n\n### 한국어"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "中文标题" in out


def test_toc_with_math_symbols():
    """Test TOC with mathematical symbols."""
    src = "[[_TOC_]]\n\n## Formula: x² + y² = z²"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_with_zero_width_space():
    """Test TOC with zero-width space (should break pattern)."""
    # Zero-width space between brackets
    src = "[[​_TOC_]]"  # Contains zero-width space
    out = fmt(src)
    # Should not be recognized as valid TOC
    assert out.strip() != src or "[[​_TOC_]]" not in out or "\\[" in out


def test_toc_consecutive_without_blank_lines():
    """Test consecutive TOCs with only single newlines."""
    src = "[[_TOC_]]\n[[_TOC_]]\n[[_TOC_]]"
    out = fmt(src)
    # Each TOC should be on its own line
    assert out.count("[[_TOC_]]") == 3


def test_toc_with_front_matter():
    """Test TOC with YAML front matter."""
    src = "---\ntitle: Test\n---\n\n[[_TOC_]]\n\n## Section"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_after_metadata():
    """Test TOC after document metadata."""
    src = "<!-- metadata -->\n\n[[_TOC_]]\n\n## Section"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_ten_times():
    """Test document with ten TOC markers."""
    src = "\n\n".join(["[[_TOC_]]"] * 10)
    out = fmt(src)
    assert out.count("[[_TOC_]]") == 10


def test_toc_with_escaped_characters_nearby():
    """Test TOC with escaped markdown nearby."""
    src = "[[_TOC_]]\n\n\\# Not a heading\n\n\\* Not a list"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_similar_pattern_single_underscore():
    """Test pattern with single underscores (not TOC)."""
    src = "[[TOC]]"
    out = fmt(src)
    assert "\\[" in out or "[[TOC]]" not in out


def test_toc_similar_pattern_different_content():
    """Test similar patterns that should not be recognized."""
    patterns = [
        "[[_TABLE_]]",
        "[[_INDEX_]]",
        "[[_TOC]]",
        "[[TOC_]]",
        "[[_toc_]]",
        "[[__TOC__]]",
    ]
    for pattern in patterns:
        out = fmt(pattern)
        # None should be preserved as-is (except lowercase which might not be escaped)
        if pattern != "[[_TOC_]]":
            # Should be different from input (escaped or modified)
            assert "\\[" in out or pattern not in out or out.strip() != pattern


def test_toc_with_nested_code_blocks():
    """Test TOC with nested/multiple code blocks."""
    src = "[[_TOC_]]\n\n```python\ncode1\n```\n\n```javascript\ncode2\n```"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert out.count("```") >= 4  # At least 4 backticks for 2 code blocks


def test_toc_with_complex_table():
    """Test TOC with complex markdown table."""
    src = "[[_TOC_]]\n\n| A | B | C |\n|---|---|---|\n| 1 | 2 | 3 |\n| 4 | 5 | 6 |"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_in_nested_blockquote():
    """Test TOC in nested blockquotes."""
    src = "> > [[_TOC_]]"
    out = fmt(src)
    # Should remain in blockquote
    assert "> >" in out or ">>" in out


def test_toc_after_multiple_headings():
    """Test TOC after many heading levels."""
    src = "# H1\n## H2\n### H3\n#### H4\n##### H5\n###### H6\n\n[[_TOC_]]\n\nContent"
    out = fmt(src)
    assert "[[_TOC_]]" in out
    assert "###### H6" in out


def test_toc_with_heading_with_id():
    """Test TOC with heading that has HTML ID."""
    src = "[[_TOC_]]\n\n## Section {#custom-id}"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_with_checkbox_lists():
    """Test TOC with task list checkboxes."""
    src = "[[_TOC_]]\n\n- [ ] Task 1\n- [X] Task 2\n- [ ] Task 3"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_surrounded_by_comments():
    """Test TOC surrounded by HTML comments."""
    src = "<!-- start -->\n[[_TOC_]]\n<!-- end -->"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_with_details_summary():
    """Test TOC with HTML details/summary elements."""
    src = "[[_TOC_]]\n\n<details>\n<summary>Click me</summary>\nContent\n</details>"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_with_subscript_superscript():
    """Test TOC with subscript/superscript."""
    src = "[[_TOC_]]\n\nH~2~O and E=mc^2^"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_with_abbreviations():
    """Test TOC with abbreviation syntax."""
    src = "[[_TOC_]]\n\nThe HTML specification\n\n*[HTML]: Hyper Text Markup Language"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_maximum_whitespace():
    """Test TOC with maximum whitespace (tabs and spaces)."""
    src = "\t  \t [[_TOC_]]  \t  \n"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_with_link_references_below():
    """Test TOC with link references defined below."""
    src = "[[_TOC_]]\n\n[link1][ref1] and [link2][ref2]\n\n[ref1]: http://url1.com\n[ref2]: http://url2.com"
    out = fmt(src)
    assert "[[_TOC_]]" in out


def test_toc_real_world_example():
    """Test TOC in a realistic Azure DevOps wiki page."""
    src = """# Project Documentation

[[_TOC_]]

## Overview

This is the project overview with some **important** information.

## Getting Started

1. Clone the repository
2. Install dependencies
3. Run the application

[[_TOC_]]

## API Reference

### Authentication

Details about authentication...

### Endpoints

- GET /api/users
- POST /api/users
- DELETE /api/users/{id}

## Contributing

See [CONTRIBUTING.md](contributing.md) for details.
"""
    out = fmt(src)
    assert out.count("[[_TOC_]]") == 2
    assert "# Project Documentation" in out
    assert "## Overview" in out
    assert "\\[\\[_TOC_\\]\\]" not in out

"""Tests for the markdown parser."""

import tempfile
import unittest
from pathlib import Path

from markdeck.parser import Slide, SlideParser


class TestSlide(unittest.TestCase):
    """Test the Slide class."""

    def test_slide_creation(self):
        """Test basic slide creation."""
        content = "# Test Slide\n\nThis is content."
        slide = Slide(content, 0)

        self.assertEqual(slide.content, content)
        self.assertEqual(slide.index, 0)
        self.assertEqual(slide.notes, "")

    def test_slide_with_notes(self):
        """Test slide with speaker notes."""
        content = """# Test Slide

Content here

<!--NOTES:
These are notes
-->"""
        slide = Slide(content, 0)

        self.assertNotIn("NOTES", slide.content)
        self.assertEqual(slide.notes, "These are notes")

    def test_slide_to_dict(self):
        """Test converting slide to dictionary."""
        slide = Slide("# Test", 0)
        result = slide.to_dict()

        self.assertEqual(result["id"], 0)
        self.assertEqual(result["content"], "# Test")
        self.assertIn("notes", result)
        self.assertIn("width_mode", result)
        self.assertIsNone(result["width_mode"])

    def test_slide_to_dict_with_width_mode(self):
        """Test converting slide with width mode to dictionary."""
        content = """<!--SLIDE:wide-->

# Test"""
        slide = Slide(content, 0)
        result = slide.to_dict()

        self.assertEqual(result["width_mode"], "wide")
        self.assertEqual(result["id"], 0)
        self.assertIn("notes", result)

    def test_empty_slide(self):
        """Test handling of empty slide."""
        slide = Slide("   \n\n   ", 0)
        self.assertEqual(slide.content, "")

    def test_slide_with_wide_mode(self):
        """Test slide with wide width mode."""
        content = """<!--SLIDE:wide-->

# Test Slide

Content here"""
        slide = Slide(content, 0)

        self.assertEqual(slide.width_mode, "wide")
        self.assertNotIn("<!--SLIDE:wide-->", slide.content)
        self.assertIn("# Test Slide", slide.content)

    def test_slide_with_full_mode(self):
        """Test slide with full width mode."""
        content = """<!--SLIDE:full-->

# Test Slide"""
        slide = Slide(content, 0)

        self.assertEqual(slide.width_mode, "full")
        self.assertNotIn("<!--SLIDE:full-->", slide.content)

    def test_slide_with_ultra_wide_mode(self):
        """Test slide with ultra-wide width mode."""
        content = """<!--SLIDE:ultra-wide-->

# Test Slide"""
        slide = Slide(content, 0)

        self.assertEqual(slide.width_mode, "ultra-wide")
        self.assertNotIn("<!--SLIDE:ultra-wide-->", slide.content)

    def test_slide_without_width_mode(self):
        """Test slide without width mode directive."""
        content = "# Test Slide\n\nContent"
        slide = Slide(content, 0)

        self.assertIsNone(slide.width_mode)

    def test_width_mode_directive_in_text_preserved(self):
        """Test that width mode directive in middle of text is preserved."""
        content = """# Test Slide

This slide uses `<!--SLIDE:wide-->` for better display"""
        slide = Slide(content, 0)

        # Directive in text should be preserved
        self.assertIn("<!--SLIDE:wide-->", slide.content)
        # But width_mode should not be set
        self.assertIsNone(slide.width_mode)

    def test_width_mode_case_insensitive(self):
        """Test that width mode directive is case insensitive."""
        content = """<!--SLIDE:WIDE-->

# Test Slide"""
        slide = Slide(content, 0)

        self.assertEqual(slide.width_mode, "wide")

    def test_width_mode_with_notes(self):
        """Test width mode works alongside speaker notes."""
        content = """<!--SLIDE:wide-->

# Test Slide

Content here

<!--NOTES:
Test notes
-->"""
        slide = Slide(content, 0)

        self.assertEqual(slide.width_mode, "wide")
        self.assertEqual(slide.notes, "Test notes")
        self.assertNotIn("<!--SLIDE:wide-->", slide.content)
        self.assertNotIn("NOTES", slide.content)

    def test_width_mode_with_columns(self):
        """Test width mode works with two-column layout."""
        content = """<!--SLIDE:full-->

:::columns
Left
|||
Right
:::"""
        slide = Slide(content, 0)

        self.assertEqual(slide.width_mode, "full")
        self.assertIn("<!-- COLUMN:LEFT:START -->", slide.content)
        self.assertNotIn("<!--SLIDE:full-->", slide.content)

    def test_two_column_transformation_basic(self):
        """Test basic two-column transformation."""
        content = """:::columns
Left content
|||
Right content
:::"""
        slide = Slide(content, 0)

        # Check that marker structure was created
        self.assertIn("<!-- COLUMN:LEFT:START -->", slide.content)
        self.assertIn("<!-- COLUMN:LEFT:END -->", slide.content)
        self.assertIn("<!-- COLUMN:RIGHT:START -->", slide.content)
        self.assertIn("<!-- COLUMN:RIGHT:END -->", slide.content)
        self.assertIn("Left content", slide.content)
        self.assertIn("Right content", slide.content)

    def test_two_column_with_markdown(self):
        """Test two-column transformation with rich markdown."""
        content = """:::columns
# Left Heading

- Item 1
- Item 2
|||
# Right Heading

```python
print("hello")
```
:::"""
        slide = Slide(content, 0)

        # Check that markdown is preserved in marker structure
        self.assertIn("<!-- COLUMN:LEFT:START -->", slide.content)
        self.assertIn("<!-- COLUMN:RIGHT:START -->", slide.content)
        self.assertIn("# Left Heading", slide.content)
        self.assertIn("# Right Heading", slide.content)
        self.assertIn("- Item 1", slide.content)
        self.assertIn("- Item 2", slide.content)
        self.assertIn("```python", slide.content)

    def test_two_column_with_extra_whitespace(self):
        """Test two-column transformation with extra whitespace around separators."""
        content = """:::columns
Left content
  |||
Right content

:::"""
        slide = Slide(content, 0)

        # Should still work with extra whitespace
        self.assertIn("<!-- COLUMN:LEFT:START -->", slide.content)
        self.assertIn("Left content", slide.content)
        self.assertIn("Right content", slide.content)

    def test_two_column_missing_separator(self):
        """Test two-column block without separator preserves original content."""
        content = """:::columns
Only one column here
:::"""
        slide = Slide(content, 0)

        # Should preserve original content when separator is missing
        self.assertIn(":::columns", slide.content)
        self.assertIn("Only one column here", slide.content)

    def test_two_column_with_notes(self):
        """Test two-column transformation works alongside speaker notes."""
        content = """:::columns
Left
|||
Right
:::

<!--NOTES:
Test notes
-->"""
        slide = Slide(content, 0)

        # Both transformations should work
        self.assertIn("<!-- COLUMN:LEFT:START -->", slide.content)
        self.assertNotIn("NOTES", slide.content)
        self.assertEqual(slide.notes, "Test notes")

    def test_multiple_column_blocks(self):
        """Test multiple two-column blocks in one slide."""
        content = """# Title

:::columns
First left
|||
First right
:::

Some text in between

:::columns
Second left
|||
Second right
:::"""
        slide = Slide(content, 0)

        # Should handle multiple blocks
        self.assertEqual(slide.content.count("<!-- COLUMN:LEFT:START -->"), 2)
        self.assertIn("First left", slide.content)
        self.assertIn("First right", slide.content)
        self.assertIn("Second left", slide.content)
        self.assertIn("Second right", slide.content)

    def test_two_column_empty_columns(self):
        """Test two-column transformation with empty columns."""
        content = """:::columns

|||
Right only
:::"""
        slide = Slide(content, 0)

        # Should still create structure even with empty left column
        self.assertIn("<!-- COLUMN:LEFT:START -->", slide.content)
        self.assertIn("Right only", slide.content)


class TestSlideParser(unittest.TestCase):
    """Test the SlideParser class."""

    def test_parse_content_single_slide(self):
        """Test parsing content with a single slide."""
        content = "# Single Slide\n\nContent here."
        slides = SlideParser.parse_content(content)

        self.assertEqual(len(slides), 1)
        self.assertEqual(slides[0].content, content)

    def test_parse_content_multiple_slides(self):
        """Test parsing content with multiple slides."""
        content = """# Slide 1

Content 1

---

# Slide 2

Content 2

---

# Slide 3

Content 3"""
        slides = SlideParser.parse_content(content)

        self.assertEqual(len(slides), 3)
        self.assertIn("# Slide 1", slides[0].content)
        self.assertIn("# Slide 2", slides[1].content)
        self.assertIn("# Slide 3", slides[2].content)

    def test_parse_content_with_empty_slides(self):
        """Test parsing content with empty slides filtered out."""
        content = """# Slide 1

---

---

# Slide 2"""
        slides = SlideParser.parse_content(content)

        # Empty slides should be filtered out
        self.assertTrue(all(slide.content for slide in slides))

    def test_parse_content_edge_cases(self):
        """Test edge cases in parsing."""
        # Delimiter at start
        content = "---\n# Slide 1"
        slides = SlideParser.parse_content(content)
        self.assertGreaterEqual(len(slides), 1)

        # Delimiter at end
        content = "# Slide 1\n---"
        slides = SlideParser.parse_content(content)
        self.assertGreaterEqual(len(slides), 1)

    def test_get_title_from_h1(self):
        """Test extracting title from first H1."""
        content = "# My Presentation\n\nContent\n---\n# Slide 2"
        slides = SlideParser.parse_content(content)
        parser = SlideParser.__new__(SlideParser)
        parser.file_path = Path("test.md")

        # Mock parse method
        def mock_parse():
            return slides

        parser.parse = mock_parse

        title = parser.get_title()
        self.assertEqual(title, "My Presentation")

    def test_to_json(self):
        """Test converting parser output to JSON format."""
        content = "# Slide 1\n---\n# Slide 2"
        parser = SlideParser.__new__(SlideParser)
        parser.file_path = Path("test.md")

        slides = SlideParser.parse_content(content)

        def mock_parse():
            return slides

        parser.parse = mock_parse

        result = parser.to_json()

        self.assertIn("slides", result)
        self.assertIn("total", result)
        self.assertIn("title", result)
        self.assertEqual(result["total"], 2)
        self.assertEqual(len(result["slides"]), 2)


class TestSlideParserWithFiles(unittest.TestCase):
    """Test SlideParser with actual files."""

    def test_file_not_found(self):
        """Test handling of missing file."""
        with self.assertRaises(FileNotFoundError):
            SlideParser("nonexistent.md")

    def test_parse_real_file(self):
        """Test parsing a real markdown file."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "test.md"
            content = """# Test Presentation

Intro slide

---

# Second Slide

Content here

<!--NOTES:
Speaker notes for testing
-->

---

# Final Slide

Conclusion"""
            test_file.write_text(content, encoding="utf-8")

            parser = SlideParser(test_file)
            slides = parser.parse()

            self.assertEqual(len(slides), 3)
            self.assertEqual(slides[0].index, 0)
            self.assertEqual(slides[1].notes, "Speaker notes for testing")
            self.assertEqual(slides[2].index, 2)

    def test_get_title_fallback_to_filename(self):
        """Test title fallback to filename when no H1 present."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_file = Path(tmp_dir) / "my-presentation.md"
            test_file.write_text("Content without H1", encoding="utf-8")

            parser = SlideParser(test_file)
            title = parser.get_title()

            self.assertEqual(title, "my-presentation")


if __name__ == "__main__":
    unittest.main()

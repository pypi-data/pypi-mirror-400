"""Markdown slide parser for MarkDeck."""

import re
from pathlib import Path
from typing import Any


class Slide:
    """Represents a single slide in a presentation."""

    def __init__(self, content: str, index: int):
        """
        Initialize a slide.

        Args:
            content: Raw markdown content of the slide
            index: Zero-based index of the slide
        """
        self.content = content.strip()
        self.index = index
        self.width_mode = self._extract_width_mode()
        self.notes = self._extract_notes()
        self._transform_columns()

    def _extract_width_mode(self) -> str | None:
        """
        Extract slide width mode directive.

        Supports:
        - <!--SLIDE:wide--> (90% viewport)
        - <!--SLIDE:full--> (95% viewport)
        - <!--SLIDE:ultra-wide--> (98% viewport)

        Returns:
            Width mode ('wide', 'full', 'ultra-wide') or None
        """
        # Only match directive at the start of content (after optional whitespace)
        pattern = r"^\s*<!--\s*SLIDE:(wide|full|ultra-wide)\s*-->\s*"
        match = re.match(pattern, self.content, re.IGNORECASE)
        if match:
            mode = match.group(1).lower()
            # Remove only the directive at the start
            self.content = re.sub(pattern, "", self.content, flags=re.IGNORECASE)
            self.content = self.content.strip()
            return mode
        return None

    def _extract_notes(self) -> str:
        """
        Extract speaker notes from HTML comments.

        Returns:
            Extracted notes or empty string
        """
        notes_pattern = r"<!--\s*NOTES:\s*(.*?)\s*-->"
        match = re.search(notes_pattern, self.content, re.DOTALL | re.IGNORECASE)
        if match:
            # Remove the notes from content
            self.content = re.sub(notes_pattern, "", self.content, flags=re.DOTALL | re.IGNORECASE)
            self.content = self.content.strip()
            return match.group(1).strip()
        return ""

    def _transform_columns(self) -> None:
        """
        Transform column syntax into marker format for frontend processing.

        Converts:
            :::columns
            Left content
            |||
            Right content
            :::

        Into special markers that the frontend will process:
            <!-- COLUMN:LEFT:START -->
            Left content (markdown)
            <!-- COLUMN:LEFT:END -->
            <!-- COLUMN:RIGHT:START -->
            Right content (markdown)
            <!-- COLUMN:RIGHT:END -->

        The frontend (slides.js) will find these markers and render the markdown
        in each column, allowing mermaid diagrams and other features to work.

        Note: Code blocks are protected from transformation to avoid transforming
        example column syntax inside code blocks.
        """
        # First, protect code blocks by replacing them with placeholders
        code_blocks = []
        code_block_pattern = r"```.*?```"

        def save_code_block(match):
            code_blocks.append(match.group(0))
            return f"__CODE_BLOCK_{len(code_blocks) - 1}__"

        # Save all code blocks
        protected_content = re.sub(
            code_block_pattern, save_code_block, self.content, flags=re.DOTALL
        )

        # Pattern to match column blocks (more forgiving with whitespace)
        column_pattern = r":::columns\s*\n(.*?)\s*\n:::"

        def replace_columns(match):
            content = match.group(1)
            # Split on ||| separator (more forgiving with whitespace)
            parts = re.split(r"\s*\|\|\|\s*", content, maxsplit=1)

            if len(parts) == 2:
                left_content = parts[0].strip()
                right_content = parts[1].strip()

                # Create marker structure that preserves markdown
                # The frontend will process these markers after marked.js runs
                return (
                    "<!-- COLUMN:LEFT:START -->\n"
                    f"{left_content}\n"
                    "<!-- COLUMN:LEFT:END -->\n"
                    "<!-- COLUMN:RIGHT:START -->\n"
                    f"{right_content}\n"
                    "<!-- COLUMN:RIGHT:END -->"
                )
            else:
                # If no separator found, return original content
                return match.group(0)

        # Transform columns in the protected content
        protected_content = re.sub(
            column_pattern, replace_columns, protected_content, flags=re.DOTALL
        )

        # Restore code blocks
        for i, code_block in enumerate(code_blocks):
            protected_content = protected_content.replace(f"__CODE_BLOCK_{i}__", code_block)

        self.content = protected_content

    def to_dict(self) -> dict[str, Any]:
        """
        Convert slide to dictionary format.

        Returns:
            Dictionary representation of the slide
        """
        return {
            "id": self.index,
            "content": self.content,
            "notes": self.notes,
            "width_mode": self.width_mode,
        }


class SlideParser:
    """Parser for markdown files containing slides."""

    SLIDE_DELIMITER = "---"

    def __init__(self, file_path: str | Path):
        """
        Initialize the parser.

        Args:
            file_path: Path to the markdown file
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

    def parse(self) -> list[Slide]:
        """
        Parse the markdown file into slides.

        Returns:
            List of Slide objects
        """
        content = self.file_path.read_text(encoding="utf-8")
        return self.parse_content(content)

    @classmethod
    def parse_content(cls, content: str) -> list[Slide]:
        """
        Parse markdown content into slides.

        Args:
            content: Raw markdown content

        Returns:
            List of Slide objects
        """
        # Split on delimiter with proper handling of edge cases
        raw_slides = content.split(f"\n{cls.SLIDE_DELIMITER}\n")

        # Also handle delimiter at start or end of lines
        slides = []
        for raw_slide in raw_slides:
            # Remove leading/trailing delimiters if present
            raw_slide = raw_slide.strip()
            if raw_slide and raw_slide != cls.SLIDE_DELIMITER:
                slides.append(raw_slide)

        # Create Slide objects
        return [Slide(content, idx) for idx, content in enumerate(slides)]

    def get_title(self) -> str:
        """
        Extract the presentation title from the first slide.

        Returns:
            Title of the presentation or filename
        """
        slides = self.parse()
        if not slides:
            return self.file_path.stem

        # Try to find first H1 heading
        first_slide = slides[0].content
        h1_match = re.search(r"^#\s+(.+)$", first_slide, re.MULTILINE)
        if h1_match:
            return h1_match.group(1).strip()

        return self.file_path.stem

    def to_json(self) -> dict[str, Any]:
        """
        Convert parsed slides to JSON-serializable format.

        Returns:
            Dictionary with slides and metadata
        """
        slides = self.parse()
        return {
            "slides": [slide.to_dict() for slide in slides],
            "total": len(slides),
            "title": self.get_title(),
        }

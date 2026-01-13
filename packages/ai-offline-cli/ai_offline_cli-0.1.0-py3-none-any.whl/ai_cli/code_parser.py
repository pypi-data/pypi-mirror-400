"""Parser for extracting and saving code from agent responses."""

import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CodeBlock:
    """Represents a code block extracted from text."""
    language: str
    code: str
    filename: Optional[str] = None
    description: Optional[str] = None


class CodeParser:
    """Extract code blocks from agent responses and save to files."""

    def __init__(self, output_dir: Path = None):
        """
        Initialize code parser.

        Args:
            output_dir: Directory to save extracted code files
        """
        self.output_dir = output_dir or Path.cwd() / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_code_blocks(self, text: str) -> List[CodeBlock]:
        """
        Extract all code blocks from markdown-formatted text.

        Supports formats:
        ```python
        code here
        ```

        ```python:filename.py
        code here
        ```
        """
        blocks = []

        # Pattern for code blocks with optional language and filename
        # Matches: ```language:filename or ```language
        pattern = r"```(\w+)(?::([^\n]+))?\n(.*?)```"

        matches = re.finditer(pattern, text, re.DOTALL)

        for match in matches:
            language = match.group(1)
            filename = match.group(2).strip() if match.group(2) else None
            code = match.group(3).strip()

            # Try to extract description from text before code block
            description = self._extract_description(text, match.start())

            blocks.append(CodeBlock(
                language=language,
                code=code,
                filename=filename,
                description=description
            ))

        return blocks

    def _extract_description(self, text: str, block_start: int) -> Optional[str]:
        """Extract description text before code block."""
        # Get text before code block
        before_text = text[:block_start].strip()

        # Get last paragraph (text after last double newline)
        paragraphs = before_text.split("\n\n")
        if paragraphs:
            last_para = paragraphs[-1].strip()
            # Remove markdown formatting
            last_para = re.sub(r'[*_#]', '', last_para)
            if len(last_para) < 200:  # Only short descriptions
                return last_para

        return None

    def save_code_block(
        self,
        block: CodeBlock,
        auto_name: bool = True,
        overwrite: bool = False
    ) -> Path:
        """
        Save a code block to file.

        Args:
            block: CodeBlock to save
            auto_name: Auto-generate filename if not specified
            overwrite: Overwrite existing files

        Returns:
            Path to saved file
        """
        # Determine filename
        if block.filename:
            filename = block.filename
        elif auto_name:
            filename = self._generate_filename(block)
        else:
            raise ValueError("No filename specified and auto_name=False")

        # Create full path
        filepath = self.output_dir / filename

        # Check if file exists
        if filepath.exists() and not overwrite:
            # Add suffix to avoid overwrite
            base = filepath.stem
            ext = filepath.suffix
            counter = 1
            while filepath.exists():
                filepath = self.output_dir / f"{base}_{counter}{ext}"
                counter += 1

        # Save file
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(block.code, encoding="utf-8")

        return filepath

    def _generate_filename(self, block: CodeBlock) -> str:
        """Auto-generate filename based on language and content."""
        # Extension mapping
        extensions = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "java": ".java",
            "cpp": ".cpp",
            "c": ".c",
            "go": ".go",
            "rust": ".rs",
            "ruby": ".rb",
            "php": ".php",
            "swift": ".swift",
            "kotlin": ".kt",
            "bash": ".sh",
            "shell": ".sh",
            "sql": ".sql",
            "html": ".html",
            "css": ".css",
            "json": ".json",
            "yaml": ".yaml",
            "xml": ".xml",
            "markdown": ".md",
        }

        ext = extensions.get(block.language.lower(), ".txt")

        # Try to extract class/function name from code
        name = self._extract_main_identifier(block.code, block.language)

        if name:
            return f"{name}{ext}"

        # Fallback to generic name
        return f"code{ext}"

    def _extract_main_identifier(self, code: str, language: str) -> Optional[str]:
        """Extract main class/function name from code."""
        language = language.lower()

        patterns = {
            "python": [
                r"class\s+(\w+)",
                r"def\s+(\w+)",
            ],
            "javascript": [
                r"class\s+(\w+)",
                r"function\s+(\w+)",
                r"const\s+(\w+)\s*=",
            ],
            "typescript": [
                r"class\s+(\w+)",
                r"function\s+(\w+)",
                r"const\s+(\w+)\s*:",
            ],
            "java": [
                r"class\s+(\w+)",
                r"interface\s+(\w+)",
            ],
            "go": [
                r"func\s+(\w+)",
                r"type\s+(\w+)\s+struct",
            ],
            "rust": [
                r"fn\s+(\w+)",
                r"struct\s+(\w+)",
            ],
        }

        if language in patterns:
            for pattern in patterns[language]:
                match = re.search(pattern, code)
                if match:
                    return match.group(1)

        return None

    def save_all_code_blocks(
        self,
        text: str,
        auto_name: bool = True,
        overwrite: bool = False
    ) -> List[Path]:
        """
        Extract and save all code blocks from text.

        Args:
            text: Text containing code blocks
            auto_name: Auto-generate filenames
            overwrite: Overwrite existing files

        Returns:
            List of saved file paths
        """
        blocks = self.extract_code_blocks(text)
        saved_files = []

        for block in blocks:
            try:
                filepath = self.save_code_block(block, auto_name, overwrite)
                saved_files.append(filepath)
            except Exception as e:
                print(f"Warning: Failed to save code block: {e}")

        return saved_files

    def create_project_structure(
        self,
        responses: List[Dict],
        project_name: str = "generated_project"
    ) -> Path:
        """
        Create complete project structure from multiple agent responses.

        Args:
            responses: List of agent responses with code
            project_name: Name of project directory

        Returns:
            Path to created project directory
        """
        project_dir = self.output_dir / project_name
        project_dir.mkdir(parents=True, exist_ok=True)

        # Temporarily change output dir
        original_dir = self.output_dir
        self.output_dir = project_dir

        all_files = []
        for response in responses:
            if isinstance(response, dict):
                text = response.get("response", "")
            else:
                text = str(response)

            files = self.save_all_code_blocks(text, auto_name=True, overwrite=True)
            all_files.extend(files)

        # Restore original dir
        self.output_dir = original_dir

        return project_dir


class CodeOrganizer:
    """Organize code files into proper project structure."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def organize_by_language(self, files: List[Path]) -> Dict[str, List[Path]]:
        """Group files by programming language."""
        by_language = {}

        for file in files:
            ext = file.suffix.lower()
            lang = self._extension_to_language(ext)

            if lang not in by_language:
                by_language[lang] = []

            by_language[lang].append(file)

        return by_language

    def organize_by_type(self, files: List[Path]) -> Dict[str, List[Path]]:
        """Organize files by type (models, views, controllers, etc.)."""
        categories = {
            "models": [],
            "views": [],
            "controllers": [],
            "services": [],
            "utils": [],
            "tests": [],
            "config": [],
            "other": []
        }

        for file in files:
            name = file.stem.lower()

            if "model" in name or "schema" in name:
                categories["models"].append(file)
            elif "view" in name or "template" in name:
                categories["views"].append(file)
            elif "controller" in name or "handler" in name:
                categories["controllers"].append(file)
            elif "service" in name or "api" in name:
                categories["services"].append(file)
            elif "util" in name or "helper" in name:
                categories["utils"].append(file)
            elif "test" in name or "spec" in name:
                categories["tests"].append(file)
            elif "config" in name or "settings" in name:
                categories["config"].append(file)
            else:
                categories["other"].append(file)

        return categories

    def create_structured_project(
        self,
        files: List[Path],
        structure_type: str = "mvc"
    ) -> Path:
        """
        Create organized project structure.

        Args:
            files: List of code files
            structure_type: Type of structure (mvc, flat, by_language)

        Returns:
            Path to organized project
        """
        if structure_type == "mvc":
            categories = self.organize_by_type(files)

            for category, category_files in categories.items():
                if category_files:
                    category_dir = self.base_dir / category
                    category_dir.mkdir(exist_ok=True)

                    for file in category_files:
                        dest = category_dir / file.name
                        dest.write_text(file.read_text())

        elif structure_type == "by_language":
            by_lang = self.organize_by_language(files)

            for lang, lang_files in by_lang.items():
                if lang_files:
                    lang_dir = self.base_dir / lang
                    lang_dir.mkdir(exist_ok=True)

                    for file in lang_files:
                        dest = lang_dir / file.name
                        dest.write_text(file.read_text())

        else:  # flat
            for file in files:
                dest = self.base_dir / file.name
                dest.write_text(file.read_text())

        return self.base_dir

    def _extension_to_language(self, ext: str) -> str:
        """Map file extension to language name."""
        mapping = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby",
            ".php": "php",
        }
        return mapping.get(ext, "other")

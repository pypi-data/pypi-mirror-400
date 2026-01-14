"""Gemtext content utilities.

Spartan uses text/gemini as its default document format, same as Gemini.
This module provides utilities for working with gemtext content.
"""

from pathlib import Path


def generate_directory_listing(directory: Path, request_path: str) -> str:
    """Generate a gemtext directory listing.

    Args:
        directory: The directory to list.
        request_path: The original request path.

    Returns:
        A gemtext-formatted directory listing.
    """
    # Ensure request_path ends with / for proper link generation
    if not request_path.endswith("/"):
        request_path = request_path + "/"

    lines = [
        f"# Index of {request_path}",
        "",
    ]

    # Add parent directory link if not at root
    if request_path != "/":
        lines.append("=> .. Parent directory")
        lines.append("")

    # Collect and sort entries
    entries = []
    try:
        for entry in directory.iterdir():
            if entry.name.startswith("."):
                continue  # Skip hidden files
            entries.append(entry)
    except PermissionError:
        lines.append("Error: Permission denied")
        return "\n".join(lines)

    # Sort: directories first, then files, alphabetically
    entries.sort(key=lambda e: (not e.is_dir(), e.name.lower()))

    # Generate links
    for entry in entries:
        name = entry.name
        if entry.is_dir():
            lines.append(f"=> {name}/ {name}/")
        else:
            # Get file size
            try:
                size = entry.stat().st_size
                size_str = _format_size(size)
                lines.append(f"=> {name} {name} ({size_str})")
            except OSError:
                lines.append(f"=> {name} {name}")

    if not entries:
        lines.append("(empty directory)")

    lines.append("")
    return "\n".join(lines)


def _format_size(size: int) -> str:
    """Format file size in human-readable format.

    Args:
        size: Size in bytes.

    Returns:
        Human-readable size string.
    """
    size_float = float(size)
    for unit in ["B", "KB", "MB", "GB"]:
        if size_float < 1024:
            if unit == "B":
                return f"{int(size_float)} {unit}"
            return f"{size_float:.1f} {unit}"
        size_float /= 1024
    return f"{size_float:.1f} TB"


def parse_input_prompt(line: str) -> str | None:
    """Parse a Spartan input prompt line.

    Spartan uses =: prefix for input prompts within documents.
    Format: =: prompt text

    Args:
        line: A line from a gemtext document.

    Returns:
        The prompt text if this is an input prompt line, None otherwise.
    """
    if line.startswith("=:"):
        # Extract prompt text after =:
        prompt = line[2:].strip()
        return prompt if prompt else None
    return None


def has_input_prompt(content: str) -> bool:
    """Check if gemtext content contains an input prompt.

    Args:
        content: The gemtext content to check.

    Returns:
        True if content contains a =: input prompt line.
    """
    for line in content.split("\n"):
        if line.startswith("=:"):
            return True
    return False


def extract_input_prompts(content: str) -> list[tuple[int, str]]:
    """Extract all input prompts from gemtext content.

    Args:
        content: The gemtext content.

    Returns:
        List of (line_number, prompt_text) tuples.
    """
    prompts = []
    for i, line in enumerate(content.split("\n"), start=1):
        prompt = parse_input_prompt(line)
        if prompt:
            prompts.append((i, prompt))
    return prompts

"""
paperflow src package.
"""
import re
from pathlib import Path

def _get_version():
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    if pyproject_path.exists():
        with open(pyproject_path, 'r') as f:
            content = f.read()
        match = re.search(r'version = "([^"]+)"', content)
        return match.group(1) if match else "unknown"
    return "unknown"

__version__ = _get_version()

from paperflow.pipeline import PaperPipeline
from paperflow.schemas import (
    Paper,
    PaperMetadata,
    SearchResult,
    Section,
    Chunk,
    SourceType,
    SectionType,
)
from paperflow.providers import UnifiedSearch

__all__ = [
    "PaperPipeline",
    "Paper",
    "PaperMetadata",
    "SearchResult",
    "Section",
    "Chunk",
    "SourceType",
    "SectionType",
    "UnifiedSearch",
]

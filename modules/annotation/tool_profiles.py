"""Tool-neutral annotation profiles for Genomepipe Phase 3.1.

Profiles describe capabilities and expected outputs; they do not execute tools.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AnnotationToolProfile:
    name: str
    executable: str
    supported_outputs: tuple[str, ...]
    supports_cpus: bool = True


TOOL_PROFILES = {
    "prokka": AnnotationToolProfile(
        name="prokka",
        executable="prokka",
        supported_outputs=("gff", "gbk", "faa", "fna", "tsv"),
    ),
    "bakta": AnnotationToolProfile(
        name="bakta",
        executable="bakta",
        supported_outputs=("gff", "gbff", "faa", "ffn", "tsv"),
    ),
}


def get_tool_profile(tool: str) -> AnnotationToolProfile:
    key = tool.strip().lower()
    try:
        return TOOL_PROFILES[key]
    except KeyError as exc:
        raise ValueError(f"Unsupported annotation tool: {tool}") from exc

"""Build context strings for LLM prompts from CUDA files."""

from pathlib import Path

from .parser import CUDAFileInfo, parse_cuda_file


# Common CUDA include search paths
DEFAULT_SEARCH_PATHS = [
    "/usr/local/cuda/include",
    "/usr/include",
]


def resolve_include(include: str, base_path: Path, search_paths: list[Path] | None = None) -> Path | None:
    """Resolve an include path to an actual file."""
    if search_paths is None:
        search_paths = []
    
    # Check relative to base file
    candidates = [
        base_path.parent / include,
        base_path.parent / "include" / include,
    ]
    
    # Check search paths
    for sp in search_paths:
        candidates.append(Path(sp) / include)
    
    # Check default CUDA paths
    for dp in DEFAULT_SEARCH_PATHS:
        candidates.append(Path(dp) / include)
    
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    
    return None


def build_cuda_context(
    kernel_path: Path | str,
    include_depth: int = 1,
    search_paths: list[Path | str] | None = None,
) -> str:
    """Build context string with kernel and resolved includes.
    
    Args:
        kernel_path: Path to the main CUDA kernel file
        include_depth: How many levels of includes to resolve (1 = direct includes only)
        search_paths: Additional paths to search for includes
    
    Returns:
        Formatted context string for LLM prompts
    """
    kernel_path = Path(kernel_path)
    search_paths = [Path(p) for p in (search_paths or [])]
    
    # Parse the main kernel
    info = parse_cuda_file(kernel_path)
    kernel_content = kernel_path.read_text()
    
    # Build context
    sections = []
    
    # Main kernel
    sections.append(f"# Target Kernel: {kernel_path.name}")
    sections.append(f"# Path: {kernel_path}")
    sections.append(f"# Lines: {info.line_count}")
    if info.kernels:
        kernel_names = ", ".join(k.name for k in info.kernels)
        sections.append(f"# Kernels: {kernel_names}")
    if info.has_evolve_markers:
        sections.append(f"# EVOLVE regions: {len(info.evolve_regions)}")
    sections.append("")
    sections.append("```cuda")
    sections.append(kernel_content)
    sections.append("```")
    
    # Resolve includes
    if include_depth > 0 and info.includes:
        sections.append("")
        sections.append("# Included Files")
        
        for inc in info.includes:
            # Skip system headers
            if inc.startswith("cuda") or inc.startswith("stdio") or inc.startswith("cub/"):
                continue
            
            resolved = resolve_include(inc, kernel_path, search_paths)
            if resolved and resolved.exists():
                try:
                    inc_content = resolved.read_text()
                    sections.append("")
                    sections.append(f"## {inc}")
                    sections.append(f"# Path: {resolved}")
                    sections.append("```cuda")
                    sections.append(inc_content)
                    sections.append("```")
                except Exception:
                    pass  # Skip unreadable files
    
    return "\n".join(sections)


def format_kernel_summary(info: CUDAFileInfo) -> str:
    """Format a summary of the kernel for display."""
    lines = [f"**{info.path.name}** ({info.line_count} lines)"]
    
    if info.kernels:
        lines.append("")
        lines.append("**Kernels:**")
        for k in info.kernels:
            lines.append(f"  - `{k.name}` (lines {k.start_line}-{k.end_line})")
    
    if info.device_functions:
        lines.append("")
        lines.append("**Device Functions:**")
        for f in info.device_functions:
            lines.append(f"  - `{f.name}` (lines {f.start_line}-{f.end_line})")
    
    if info.includes:
        lines.append("")
        lines.append("**Includes:**")
        for inc in info.includes:
            lines.append(f"  - `{inc}`")
    
    if info.has_evolve_markers:
        lines.append("")
        lines.append(f"**EVOLVE regions:** {len(info.evolve_regions)}")
        for r in info.evolve_regions:
            lines.append(f"  - Lines {r.start_line}-{r.end_line}")
    else:
        lines.append("")
        lines.append("**Note:** No EVOLVE_START/EVOLVE_END markers found.")
    
    return "\n".join(lines)

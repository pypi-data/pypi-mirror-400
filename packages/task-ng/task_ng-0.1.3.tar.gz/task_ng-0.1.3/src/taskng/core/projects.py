"""Project hierarchy handling."""

from collections import Counter
from dataclasses import dataclass, field


@dataclass
class ProjectNode:
    """A node in the project hierarchy tree."""

    name: str
    full_path: str
    count: int = 0
    children: dict[str, "ProjectNode"] = field(default_factory=dict)


def parse_project_path(project: str) -> list[str]:
    """Parse a project path into components.

    Args:
        project: Project path like "Work.Backend.API"

    Returns:
        List of components like ["Work", "Backend", "API"]
    """
    if not project:
        return []
    return project.split(".")


def is_child_project(parent: str, child: str) -> bool:
    """Check if child is a subproject of parent.

    Args:
        parent: Parent project path (e.g., "Work")
        child: Child project path (e.g., "Work.Backend")

    Returns:
        True if child is under parent (or equal to parent).
    """
    if not parent:
        return True  # Empty parent matches everything
    if not child:
        return False

    # Exact match or child starts with parent followed by "."
    return child == parent or child.startswith(parent + ".")


def build_project_tree(projects: list[str]) -> dict[str, ProjectNode]:
    """Build a tree structure from project paths.

    Args:
        projects: List of project paths.

    Returns:
        Dict mapping root project names to ProjectNode trees.
    """
    # Count occurrences of each project
    project_counts = Counter(projects)

    roots: dict[str, ProjectNode] = {}

    for project in sorted(set(projects)):
        if not project:
            continue

        parts = parse_project_path(project)
        current_dict = roots

        for i, part in enumerate(parts):
            full_path = ".".join(parts[: i + 1])

            if part not in current_dict:
                current_dict[part] = ProjectNode(
                    name=part,
                    full_path=full_path,
                    count=0,
                )

            # Add count for this exact project path
            if full_path == project:
                current_dict[part].count = project_counts[project]

            if i < len(parts) - 1:
                current_dict = current_dict[part].children
            else:
                current_dict = current_dict[part].children

    return roots


def get_project_total(node: ProjectNode) -> int:
    """Get total task count for a project including all children.

    Args:
        node: Project node.

    Returns:
        Total count including all descendants.
    """
    total = node.count
    for child in node.children.values():
        total += get_project_total(child)
    return total


def format_project_tree(
    roots: dict[str, ProjectNode],
    include_counts: bool = True,
) -> list[str]:
    """Format project tree as strings for display.

    Args:
        roots: Root project nodes.
        include_counts: Whether to include task counts.

    Returns:
        List of formatted lines.
    """
    lines: list[str] = []

    def format_node(node: ProjectNode, prefix: str = "", is_last: bool = True) -> None:
        # Determine the branch character
        branch = ("└── " if is_last else "├── ") if prefix else ""

        # Format the line
        if include_counts:
            total = get_project_total(node)
            if node.count != total:
                count_str = f" ({node.count}/{total})"
            else:
                count_str = f" ({total})"
            lines.append(f"{prefix}{branch}{node.name}{count_str}")
        else:
            lines.append(f"{prefix}{branch}{node.name}")

        # Process children
        children = list(node.children.values())
        for i, child in enumerate(children):
            is_child_last = i == len(children) - 1
            if prefix:
                child_prefix = prefix + ("    " if is_last else "│   ")
            else:
                child_prefix = "    " if is_last else "│   "
            format_node(child, child_prefix, is_child_last)

    # Format each root
    root_nodes = list(roots.values())
    for i, node in enumerate(root_nodes):
        format_node(node, "", i == len(root_nodes) - 1)

    return lines

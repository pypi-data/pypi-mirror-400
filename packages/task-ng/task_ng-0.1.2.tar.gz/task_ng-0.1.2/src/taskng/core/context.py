"""Context handling for task filtering."""

from pathlib import Path
from typing import Any

from taskng.config.settings import get_config, get_config_dir


def get_context_state_file() -> Path:
    """Get the path to the context state file.

    Returns:
        Path to the context state file.
    """
    return get_config_dir() / "context"


def get_temporary_context_file() -> Path:
    """Get the path to the temporary context filters file.

    Returns:
        Path to the temporary context filters file.
    """
    return get_config_dir() / "context.filters"


def set_temporary_context(filters: list[str]) -> None:
    """Set a temporary context with ad-hoc filters.

    Args:
        filters: List of filter strings.
    """
    state_file = get_context_state_file()
    filters_file = get_temporary_context_file()

    # Ensure config directory exists
    state_file.parent.mkdir(parents=True, exist_ok=True)

    # Mark as temporary context
    state_file.write_text("__temporary__")

    # Store the filters
    filters_file.write_text("\n".join(filters))


def get_temporary_context_filters() -> list[str] | None:
    """Get filters for the temporary context.

    Returns:
        List of filter strings or None if no temporary context.
    """
    filters_file = get_temporary_context_file()
    if not filters_file.exists():
        return None

    content = filters_file.read_text().strip()
    if not content:
        return None

    return content.split("\n")


def clear_temporary_context() -> None:
    """Clear the temporary context filters."""
    from contextlib import suppress

    filters_file = get_temporary_context_file()
    with suppress(FileNotFoundError, OSError):
        if filters_file.exists():
            filters_file.unlink()


def get_defined_contexts() -> dict[str, dict[str, Any]]:
    """Get all defined contexts from configuration.

    Returns:
        Dict mapping context names to their settings.
    """
    config = get_config()
    contexts = config.get("context", {})

    # Filter out non-dict entries (like the active context marker)
    return {
        name: settings
        for name, settings in contexts.items()
        if isinstance(settings, dict)
    }


def get_context_filter(context_name: str) -> list[str]:
    """Get filter arguments for a context.

    Args:
        context_name: Name of the context.

    Returns:
        List of filter argument strings.
    """
    # Handle temporary context
    if context_name == "__temporary__":
        return get_temporary_context_filters() or []

    contexts = get_defined_contexts()
    if context_name not in contexts:
        return []

    context = contexts[context_name]
    filters = []

    # Build filter from context settings
    if "filter" in context:
        # Direct filter string(s)
        filter_val = context["filter"]
        if isinstance(filter_val, list):
            filters.extend(filter_val)
        else:
            filters.append(filter_val)

    if "project" in context:
        filters.append(f"project:{context['project']}")

    if "tags" in context:
        tags = context["tags"]
        if isinstance(tags, list):
            for tag in tags:
                # Support +tag or -tag syntax, default to inclusion
                if tag.startswith("+") or tag.startswith("-"):
                    filters.append(tag)
                else:
                    filters.append(f"+{tag}")
        else:
            if tags.startswith("+") or tags.startswith("-"):
                filters.append(tags)
            else:
                filters.append(f"+{tags}")

    return filters


def get_current_context() -> str | None:
    """Get the currently active context.

    Returns:
        Context name or None if no context is active.
    """
    state_file = get_context_state_file()
    if not state_file.exists():
        return None

    context = state_file.read_text().strip()
    if not context or context == "none":
        return None

    return context


def set_current_context(context_name: str | None) -> None:
    """Set the current context.

    Args:
        context_name: Context name to set, or None to clear.
    """
    state_file = get_context_state_file()
    # Ensure config directory exists
    state_file.parent.mkdir(parents=True, exist_ok=True)

    # Clear temporary context filters when switching
    clear_temporary_context()

    if context_name is None or context_name == "none":
        if state_file.exists():
            state_file.unlink()
    else:
        state_file.write_text(context_name)


def context_exists(context_name: str) -> bool:
    """Check if a context is defined.

    Args:
        context_name: Context name to check.

    Returns:
        True if context exists in configuration.
    """
    contexts = get_defined_contexts()
    return context_name in contexts


def get_context_description(context_name: str) -> str:
    """Get description for a context.

    Args:
        context_name: Context name.

    Returns:
        Description string or empty string.
    """
    contexts = get_defined_contexts()
    if context_name not in contexts:
        return ""

    desc = contexts[context_name].get("description", "")
    return str(desc) if desc else ""

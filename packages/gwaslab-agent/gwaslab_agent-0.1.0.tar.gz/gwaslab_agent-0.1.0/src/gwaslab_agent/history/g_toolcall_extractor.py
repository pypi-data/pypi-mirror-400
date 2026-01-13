"""Utilities for normalizing and extracting tool-call strings from the agent archive.

This module provides helpers to:
- Normalize role-specific call prefixes (`gl` vs `sumstats`).
- Format toolcall entries (dict or string) into consistent, displayable strings.
- Extract toolcalls for a specific role or aggregate all toolcalls with optional exclusions.
"""

def _normalize_prefix(role):
    """Return the normalized prefix for a given role.

    Roles `Planner`, `PathManager`, and `Loader` use the `gl` prefix.
    All other roles use the `sumstats` prefix.
    """
    r = (role or "").lower()
    return "gl" if r in ("planner", "pathmanager", "loader") else "sumstats"

from gwaslab_agent.tools.g_toolcall_parser import _format_args_python, _format_loader_sumstats_args

def _format_toolcall(x, prefix):
    """Format a toolcall entry into a concise string representation.

    - Dict entries: render as `<prefix>.<name>(<args>)`, flattening loader `Sumstats` args.
    - String entries: preserve assignment/chained calls; otherwise prepend `<prefix>.` if missing.
    """
    if isinstance(x, dict):
        nm = x.get("name") or x.get("tool")
        args = x.get("args")
        if prefix == "gl" and nm == "Sumstats":
            formatted = _format_loader_sumstats_args(args)
        else:
            formatted = _format_args_python(args)
        return f"{prefix}.{nm}({formatted})" if nm else str(x)
    if isinstance(x, str):
        # Preserve assignment-style logs and chained object calls
        if ("=" in x) or x.startswith("subset_"):
            return x
        return x if x.startswith("sumstats.") or x.startswith("gl.") else f"{prefix}.{x}"
    return str(x)

def extract_toolcalls(archive, role, role_key="gwaslab_agent"):
    """Extract formatted toolcalls for a specific role from the archive.

    Parameters:
    - `archive`: list of message dicts containing `toolcalls`.
    - `role`: role name to filter by (e.g., `Plotter`, `Planner`, `Worker_orchestrator`).
    - `role_key`: key storing the role in each archive item (default `gwaslab_agent`).

    Returns:
    - List of formatted toolcall strings for the given role.
    """
    calls = []
    prefix = _normalize_prefix(role)
    for item in archive:
        if not isinstance(item, dict):
            continue
        if item.get(role_key) != role:
            continue
        if "toolcalls" not in item:
            continue
        tc = item["toolcalls"]
        if isinstance(tc, list):
            for x in tc:
                calls.append(_format_toolcall(x, prefix))
        else:
            calls.append(_format_toolcall(tc, prefix))
    return calls

def extract_all_toolcalls(archive, exclude=None):
    """Extract all formatted toolcalls across roles, excluding specified names.

    Parameters:
    - `archive`: list of message dicts containing `toolcalls`.
    - `exclude`: iterable of tool names to exclude (e.g., `["plot_mqq", "filter_in"]`).

    Rules:
    - Preserves assignment-style strings and subset-chained calls.
    - Determines call `name` from dict entries or the head of string entries.
    - Skips entries whose `name` is in `exclude`.

    Returns:
    - List of formatted toolcall strings from the archive.
    """
    calls = []
    ex = set(exclude or [])
    for item in archive:
        if not isinstance(item, dict):
            continue
        if "toolcalls" not in item:
            continue

        rk = "gwaslab_agent" if "gwaslab_agent" in item else ("role" if "role" in item else None)
        role = item.get(rk) if rk else None
        prefix = _normalize_prefix(role)
        tc = item["toolcalls"]
        
        items = tc if isinstance(tc, list) else [tc]
        for x in items:
            name = None
            if isinstance(x, str):
                head = x.split("(", 1)[0].strip()
                name = head.split(".")[-1] if "." in head else head
            elif isinstance(x, dict):
                name = x.get("name") or x.get("tool")
            if name in ex:
                continue
            calls.append(_format_toolcall(x, prefix))
    return calls


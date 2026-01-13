def _is_df_expr(value):
    """Return True if `value` is a DataFrame reference expression.

    Supported forms:
    - Simple column: `df_<n>.<Column>` or `df_<n>.<Column>[:<k>]`
    - Extended slice: `df_<n>.<Column>[<start>:<end>]`
    - Query then column: `df_<n>.query(<pandas_query_expr>).<Column>[:<k>]`

    Notes:
    - Expressions can appear inside containers (e.g., `["df_0.query(CHR>1).SNPID"]`);
      detection applies to the string itself.
    - `<n>` is the registry index (e.g., `df_0`, `df_12`).
    - `<Column>` accepts alphanumerics and underscore.
    - Slices support `[:k]` and `[k]` forms.
    """
    import re
    if isinstance(value, str):
        if re.fullmatch(r"df_\d+\.[A-Za-z0-9_]+(?:\[:?\d+\]|\[\d+:\d+\])?", value):
            return True
        if re.fullmatch(r"df_\d+\.query\((.*?)\)\.[A-Za-z0-9_]+(?:\[:?\d+\]|\[\d+:\d+\])?", value):
            return True
    return False


def _format_value_python(v):
    """Format a Python value into an argument-friendly string (quotes, lists, dicts)."""
    if _is_df_expr(v):
        if isinstance(v, str):
            return v if v.endswith(".to_list()") else f"{v}.to_list()"
    if isinstance(v, str):
        return f'"{v}"'
    if isinstance(v, bool):
        return "True" if v else "False"
    if v is None:
        return "None"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, list):
        return "[" + ", ".join(_format_value_python(x) for x in v) + "]"
    if isinstance(v, dict):
        try:
            parts = [f"{k}={_format_value_python(vv)}" for k, vv in v.items()]
            return ", ".join(parts)
        except Exception:
            return str(v)
    return str(v)


def _format_args_python(args):
    """Format a kwargs dict into `key=value` pairs joined by commas."""

    if not isinstance(args, dict) or len(args) == 0:
        return ""
    s = ", ".join(f"{k}={_format_value_python(v)}" for k, v in args.items())
    import re
    # Dequote bracketed list containing a single quoted df expression: '["df_0.COL.iloc[0]"]' -> [df_0.COL.iloc[0]]
    s = re.sub(
        r'["\']\[\s*["\'](df_\d+\.[A-Za-z0-9_]+(?:\[:?\d+\]|\[\d+:\d+\]|\.iloc\[\d+\]))["\']\s*\]\s*["\']',
        r"[\1]",
        s,
    )
    # Dequote bracketed df expressions like "[df_1.snpid[:10]]"
    s = re.sub(r'["\'](\[df_\d[^"\']*\])["\']', r"\1", s)
    # Dequote simple df column or slice: "df_1.col[:10]" or "df_1.col[0:10]"
    s = re.sub(r'["\'](df_\d+\.[A-Za-z0-9_]+(?:\[:?\d+\]|\[\d+:\d+\])?)["\']', r"\1", s)
    # Dequote query form: "df_1.query(...).COL[:10]"
    s = re.sub(r'["\'](df_\d+\.query\([^"\']*\)\.[A-Za-z0-9_]+(?:\[:?\d+\]|\[\d+:\d+\])?)["\']', r"\1", s)
    # Dequote method chain returning scalar: "df_1.POS.max()"
    s = re.sub(r'["\'](df_\d+\.[A-Za-z0-9_]+\.[A-Za-z0-9_]+\(\))["\']', r"\1", s)
    # Dequote iloc single index: "df_1.COL.iloc[0]"
    s = re.sub(r'["\'](df_\d+\.[A-Za-z0-9_]+\.iloc\[\d+\])["\']', r"\1", s)
    return s



def _format_loader_sumstats_args(args):
    """Flatten loader `Sumstats` nested args so they appear as normal call params.
    function({"key":"value"}) to function(key = value})
    """
    if not isinstance(args, dict):
        return _format_args_python(args)
    inner = args.get("sumstats")
    others = {k: v for k, v in args.items() if k != "sumstats"}
    parts = []
    if isinstance(inner, dict):
        inner_str = _format_args_python(inner)
        if inner_str:
            parts.append(inner_str)
    elif inner is not None:
        parts.append(_format_value_python(inner))
    other_str = _format_args_python(others)
    if other_str:
        parts.append(other_str)
    return ", ".join(p for p in parts if p)


def _prefix_for_role(role):
    """Map a role to the call prefix: `gl` for planner/pathmanager/loader, else `sumstats`."""
    r = (role or "").lower()
    return "gl" if r in ("planner", "pathmanager", "loader") else "sumstats"


def _build_toolcall_string(role, name, args):
    """Construct a concise toolcall string; special-case loader `Sumstats`."""
    prefix = _prefix_for_role(role)
    if prefix == "gl" and name == "Sumstats":
        formatted = _format_loader_sumstats_args(args)
    else:
        formatted = _format_args_python(args)
    if formatted:
        return f"{prefix}.{name}({formatted})", prefix
    return f"{prefix}.{name}()", prefix


def _format_assignment(src, nm, args, var_name):
    """Build assignment-style call like `df_1 = sumstats.method(...)` or `sumstats = gl.Sumstats(...)`."""
    if src == "gl" and nm == "Sumstats":
        formatted = _format_loader_sumstats_args(args)
    else:
        formatted = _format_args_python(args)
    if formatted:
        return f"{var_name} = {src}.{nm}({formatted})"
    return f"{var_name} = {src}.{nm}()"


def _json_content(msg):
    import json, re
    s = ensure_string(msg.content)
    if not isinstance(s, str) or len(s.strip()) == 0:
        return None
    try:
        return json.loads(s)
    except Exception:
        pass
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", s, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    return None


def ensure_string(x):
    """Safely convert any message payload into a displayable string."""
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    if isinstance(x, (bytes, bytearray)):
        return x.decode("utf-8", errors="replace")
    if isinstance(x, list):
        parts = []
        for item in x:
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            elif isinstance(item, str):
                parts.append(item)
            else:
                parts.append(str(item))
        return "".join(parts)
    if isinstance(x, dict):
        if "text" in x and isinstance(x["text"], str):
            return x["text"]
        import json
        return json.dumps(x, ensure_ascii=False)
    return str(x)


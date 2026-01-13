"""
NumPy-style docstring parser for extracting parameter and return information.
"""
import inspect
import re
import ast


# Section names that are recognized in docstrings
SECTION_NAMES = {
    "parameters",
    "less used parameters",
    "returns",
    "notes",
    "examples",
    "see also",
    "references"
}


def _is_section_header(lines, idx, title):
    """Check if line at idx is a section header with optional underline."""
    if idx >= len(lines):
        return False
    
    s = lines[idx].strip().rstrip(":").lower()
    if s != title.lower():
        return False
    
    # Check for underline on next line
    if idx + 1 < len(lines):
        underline = lines[idx + 1].strip()
        if set(underline) == {"-"} and len(underline) >= 3:
            return 2
    return 1


def _normalize_type_and_enum(type_text):
    """
    Normalize a free-form type string into a JSON-compatible type + optional enum.
    
    Returns:
        tuple: (normalized_type, enum_list_or_None)
    """
    enum = None
    t = (type_text or "").strip()

    # Extract enum set literal inside braces (e.g., {"19", "38"} or {'a','b'})
    m_enum = re.match(r"^\{\s*(.+?)\s*\}$", t)
    if m_enum:
        items = [x.strip() for x in m_enum.group(1).split(",")]
        # Strip quotes if present
        enum = [re.sub(r"^([\"'])(.*)\1$", r"\2", x) for x in items]
        return "string", enum

    # Split union types like "tuple or list" / "str or bool"
    parts = [p.strip() for p in re.split(r"\bor\b|[|]", t)]
    
    def _map_primitive_type(p):
        """Map a primitive type string to JSON-compatible type."""
        p = p.lower()
        if "tuple" in p or "list" in p or "array" in p:
            return "array"
        if p in ("int", "int64", "integer"):
            return "integer"
        if p in ("float", "float64", "number", "double"):
            return "number"
        if p in ("bool", "boolean"):
            return "boolean"
        if p in ("str", "string"):
            return "string"
        if "dict" in p or "mapping" in p:
            return "object"
        # Anything else → treat as object (e.g., pandas.DataFrame)
        return "object"

    mapped = {_map_primitive_type(p) for p in parts if p}
    
    # Preference order for unions:
    # 1) array
    # 2) number (covers float; also when both number and integer, prefer number)
    # 3) integer
    # 4) object
    # 5) fall back to string or first available
    if "array" in mapped:
        out = "array"
    elif "number" in mapped and "integer" in mapped:
        out = "number"
    elif "number" in mapped:
        out = "number"
    elif "integer" in mapped:
        out = "integer"
    elif "object" in mapped:
        out = "object"
    elif "string" in mapped:
        out = "string"
    else:
        out = next(iter(mapped or {"string"}))
    
    return out, enum


def _parse_default(default_text):
    """
    Parse default values from docstrings and return JSON-compatible Python values.
    
    This ensures:
    - None -> None
    - True/False -> True/False
    - tuples -> lists
    - numeric strings -> numbers
    - everything else -> string
    """
    if default_text is None:
        return None

    s = default_text.strip()

    # Normalize common nil / boolean forms
    if s.lower() in ("none", "null"):
        return None
    if s.lower() == "true":
        return True
    if s.lower() == "false":
        return False

    # Strip leading `default=` if present
    s = re.sub(r"^\s*default\s*=\s*", "", s, flags=re.IGNORECASE)

    # Remove trailing commas (e.g., "(1, 2, 3,)")
    s = s.rstrip(",")

    # Try safe literal evaluation
    try:
        val = ast.literal_eval(s)

        # Normalize tuples -> lists for strict JSON compatibility
        if isinstance(val, tuple):
            return list(val)

        # Everything from literal_eval is already JSON-friendly:
        # (dict, list, int, float, bool, None, str)
        return val

    except Exception:
        # If it's a quoted string, remove the quotes
        m = re.match(r"""^(['"])(.*)\1$""", s)
        if m:
            return m.group(2)

        # Otherwise return raw string as-is
        return s


def _merge_param(base, incr):
    """
    Merge two parameter dictionaries (from different sections).
    
    Merging strategy:
    - type/enum: prefer first non-empty
    - default: prefer first non-None
    - description: concatenate
    - required: recompute later based on default presence
    """
    out = dict(base)
    
    # Type / enum: prefer first non-empty, then keep base if already there
    if "type" not in out or out["type"] is None:
        out["type"] = incr.get("type")
    if "enum" not in out or not out.get("enum"):
        if incr.get("enum"):
            out["enum"] = incr["enum"]
    
    # Default: prefer the first non-None default encountered
    if out.get("default") is None and incr.get("default") is not None:
        out["default"] = incr["default"]
    
    # Description: concatenate
    d1 = (out.get("description") or "").strip()
    d2 = (incr.get("description") or "").strip()
    if d1 and d2:
        out["description"] = d1 + "\n" + d2
    elif d2:
        out["description"] = d2
    
    # Required: recompute later based on default presence if not explicitly set
    return out


def _extract_default_from_description(desc):
    """
    Extract default value from description text if present.
    
    Matches patterns like:
    - "Default is True."
    - "default = 0.5"
    - "Default: (5,20)"
    - "default is 'hg19'"
    
    Returns:
        tuple: (cleaned_description, default_value_or_None)
    """
    m = re.search(r"\b[Dd]efault\s*(?:is|=|:)\s*([^\.\n]+)", desc)
    if not m:
        return desc, None
    
    raw = m.group(1).strip()
    try:
        val = ast.literal_eval(raw)
        if isinstance(val, tuple):
            val = list(val)
        default = val
    except Exception:
        default = re.sub(r"""^(['"])(.*)\1$""", r"\2", raw)
    
    # Remove default text from description
    cleaned_desc = re.sub(r"\b[Dd]efault\s*(?:is|=|:)\s*[^\.\n]+\.?", "", desc).rstrip()
    return cleaned_desc, default


def _parse_parameter_line(line, header_re):
    """
    Parse a single parameter line into a parameter entry.
    
    Expected format: name : type [optional/required] [default=X], description
    
    Returns:
        tuple: (param_name, param_entry_dict) or (None, None) if not a param line
    """
    m = header_re.match(line)
    if not m:
        return None, None
    
    pname = m.group("name")
    rest = m.group("rest")

    # Extract default=... if present
    default_text = None
    ann = rest
    mdef = re.search(r",\s*default\s*=\s*(.+)$", ann, flags=re.IGNORECASE)
    if mdef:
        default_text = mdef.group(1).strip()
        ann = ann[:mdef.start()].rstrip()

    # Extract optional/required hints
    opt_flag = None
    if re.search(r"\boptional\b", ann, re.IGNORECASE):
        opt_flag = "optional"
        ann = re.sub(r"\boptional\b", "", ann, flags=re.IGNORECASE).strip(", ").strip()
    if re.search(r"\brequired\b", ann, re.IGNORECASE):
        opt_flag = "required"
        ann = re.sub(r"\brequired\b", "", ann, flags=re.IGNORECASE).strip(", ").strip()

    # Normalize type annotation
    jtype, enum = _normalize_type_and_enum(ann)

    # Build entry
    entry = {
        "type": jtype,
        "default": _parse_default(default_text),
        "description": "",
    }
    if enum:
        entry["enum"] = enum

    if opt_flag == "required":
        entry["required"] = True
    elif opt_flag == "optional":
        entry["required"] = False

    # Normalize tuple default to list
    if isinstance(entry.get("default"), tuple):
        entry["default"] = list(entry["default"])

    # If type implies array due to tuple/list word present in annotation
    if "tuple" in ann.lower() or "list" in ann.lower() or "array" in ann.lower():
        entry["type"] = "array"

    return pname, entry


def _parse_parameters_section(lines, start_idx, is_main_section, parameters, main_parameters):
    """
    Parse a Parameters section from the docstring.
    
    Returns:
        int: index after the section ends
    """
    header_re = re.compile(
        r"""^
            (?P<name>[\w.\-]+)\s*
            :\s*
            (?P<rest>.+?)\s*$
        """, re.VERBOSE
    )
    
    current_param = None
    param_buffer = []
    n = len(lines)
    i = start_idx
    
    def _flush_current_param():
        """Flush the current parameter's description buffer."""
        nonlocal current_param, param_buffer
        if not current_param:
            param_buffer = []
            return

        entry = parameters.get(current_param, {
            "type": None,
            "default": None,
            "description": "",
            "enum": None
        })

        desc = "\n".join([b.lstrip() for b in param_buffer]).strip()
        
        # Extract default from description if present
        cleaned_desc, desc_default = _extract_default_from_description(desc)
        if desc_default is not None and entry.get("default") is None:
            entry["default"] = desc_default
        desc = cleaned_desc

        # Merge description
        inc = {"description": desc}
        parameters[current_param] = _merge_param(entry, inc)

        # Also update main_parameters if this block is main
        if is_main_section:
            mp = main_parameters.get(current_param, {
                "type": None,
                "default": None,
                "description": "",
                "enum": None
            })
            main_parameters[current_param] = _merge_param(mp, inc)

        param_buffer = []

    # Parse parameter lines
    while i < n:
        line = lines[i].strip()
        if line.rstrip(":").lower() in SECTION_NAMES:
            break

        pname, entry = _parse_parameter_line(line, header_re)
        if pname:
            _flush_current_param()
            
            # Merge into full parameters
            if pname in parameters:
                parameters[pname] = _merge_param(parameters[pname], entry)
            else:
                parameters[pname] = entry

            # Merge into main parameters if this section is main
            if is_main_section:
                if pname in main_parameters:
                    main_parameters[pname] = _merge_param(main_parameters[pname], entry)
                else:
                    main_parameters[pname] = entry.copy()

            current_param = pname
            param_buffer = []
        else:
            param_buffer.append(lines[i])
        
        i += 1

    _flush_current_param()
    return i


def _parse_returns_section(lines, start_idx):
    """
    Parse a Returns section from the docstring.
    
    Returns:
        tuple: (index_after_section, returns_info_dict_or_None)
    """
    returns_buffer = []
    n = len(lines)
    i = start_idx
    
    # Collect all lines in the Returns section
    while i < n:
        line = lines[i].strip()
        if line.rstrip(":").lower() in SECTION_NAMES:
            break
        returns_buffer.append(lines[i])
        i += 1

    returns_text = "\n".join(returns_buffer).strip()
    if not returns_text:
        return i, None

    # Parse return information
    # Common patterns:
    #   name : type
    #   name : type, description
    #   type
    #   type, description
    #   description (no type)
    return_header_re = re.compile(
        r"""^
            (?P<name>[\w.\-]+)?\s*
            (?::\s*)?
            (?P<type>[^,\n]+)?\s*
            (?:,\s*)?
            (?P<description>.*?)\s*$
        """, re.VERBOSE | re.DOTALL
    )

    return_lines = [line.strip() for line in returns_text.split('\n') if line.strip()]
    if not return_lines:
        return i, None

    first_line = return_lines[0]
    m = return_header_re.match(first_line)
    if not m:
        # No structured format, just use the text as description
        return i, {
            "name": "return_value",
            "type": "object",
            "description": returns_text
        }

    return_name = m.group("name") or "return_value"
    return_type_text = (m.group("type") or "").strip()
    return_desc = (m.group("description") or "").strip()

    # Fix: If no colon was found and type is empty but name is not,
    # then the "name" is actually the type (common pattern: "pandas.DataFrame")
    if not return_type_text and return_name and return_name != "return_value":
        if ":" not in first_line:
            # No colon means the first token is the type, not the name
            return_type_text = return_name
            return_name = "return_value"

    # Add remaining lines to description
    if len(return_lines) > 1:
        remaining = "\n".join(return_lines[1:]).strip()
        if remaining:
            if return_desc:
                return_desc += "\n" + remaining
            else:
                return_desc = remaining

    # Normalize return type
    if return_type_text:
        return_type, return_enum = _normalize_type_and_enum(return_type_text)
    else:
        # No type specified, infer from description
        return_type = "object"
        return_enum = None

    returns_info = {
        "name": return_name,
        "type": return_type,
        "description": return_desc.strip() if return_desc else "",
    }
    if return_enum:
        returns_info["enum"] = return_enum

    return i, returns_info


def _collect_until_section(lines, start_idx):
    """
    Collect text until the next section header is encountered.
    
    Returns:
        tuple: (collected_text, index_after_collection)
    """
    acc = []
    n = len(lines)
    i = start_idx
    
    while i < n:
        line = lines[i].strip()
        if line.rstrip(":").lower() in SECTION_NAMES:
            break
        acc.append(lines[i])
        i += 1
    
    return "\n".join(acc).strip(), i


def _post_process_parameters(parameters, main_parameters):
    """
    Post-process parameters: set required flags and filter out 'log' parameter.
    """
    # Set required if not explicitly set (no default => required)
    for param_dict in (parameters, main_parameters):
        for k, v in list(param_dict.items()):
            if "required" not in v:
                v["required"] = v.get("default") is None
            # Ensure tuple-like defaults already converted to list
            if isinstance(v.get("default"), tuple):
                v["default"] = list(v["default"])
    
    # Filter out 'log' parameter
    parameters = {k: v for k, v in parameters.items() if k.lower() != "log"}
    main_parameters = {k: v for k, v in main_parameters.items() if k.lower() != "log"}
    
    return parameters, main_parameters


def parse_numpy_style_params(obj):
    """
    Parse NumPy-style docstrings with possibly multiple sections:
      summary, Parameters, Returns, summary, Parameters, Returns, ...

    Supported Patterns
    ------------------
    
    **Section Headers:**
        - Headers with underline: "Parameters\\n----------" (minimum 3 dashes)
        - Headers with or without colon: "Parameters:" or "Parameters"
        - Case-insensitive matching
        - Supported sections: Parameters, Less Used Parameters, Returns, Notes, Examples, See Also, References
    
    **Parameter Lines:**
        Basic format: "name : type [optional/required] [default=X], description"
        
        Type formats:
        - Simple types: "int", "str", "float", "bool", "list", "dict"
        - Complex types: "pandas.DataFrame", "numpy.ndarray", "tuple or list"
        - Union types: "int or float", "str | bool", "list or tuple"
        - Array-like: "array-like", "list-like", "tuple-like" → normalized to "array"
        - Enum types: '{"option1", "option2", "option3"}' → detected as enum
        - Enum with quotes: "{'a', 'b', 'c'}" or '{"a", "b", "c"}' → both supported
        
        Optional/Required flags:
        - "optional" → required=False
        - "required" → required=True
        - If neither specified, inferred from default value (no default = required)
        
        Default values:
        - In type annotation: "x : int, default=10"
        - In description text: "x : int\\n    Description. Default is 10."
        - Formats supported:
          * "default=10" or "default = 10"
          * "Default is 10" or "default is 10" or "Default: 10"
          * Boolean: "default=True", "default=False", "Default is True"
          * None: "default=None", "default is None", "Default: None"
          * Strings: "default='hello'", "default=\"world\""
          * Lists: "default=[1, 2, 3]"
          * Tuples: "default=(1, 2)" → converted to list [1, 2]
          * Numbers: "default=0.05", "default=42"
        
        Description:
        - Single line: "name : type\\n    Description text."
        - Multi-line: "name : type\\n    First line.\\n    Second line.\\n    Third line."
        - With bullet points, code blocks, and special formatting preserved
        - Default values can be extracted from description text
    
    **Returns Section:**
        Format 1 - Type only (no name, no colon):
            "Returns\\n-------\\npandas.DataFrame\\n    Description text."
            → Parsed as: type="object", name="return_value", description="Description text."
        
        Format 2 - Name and type:
            "Returns\\n-------\\nresult : bool\\n    Description text."
            → Parsed as: type="boolean", name="result", description="Description text."
        
        Format 3 - Type with description on same line:
            "Returns\\n-------\\npandas.DataFrame, Updated DataFrame with results."
            → Parsed as: type="object", description="Updated DataFrame with results."
        
        Format 4 - No type specified:
            "Returns\\n-------\\ndict\\n    The processed data as a dictionary."
            → Parsed as: type="object", description="The processed data as a dictionary."
        
        Multi-line descriptions:
        - All lines after the type/name line are included in description
        - Preserves line breaks and formatting
        - Handles indented continuation lines
    
    **Multiple Sections:**
        - Multiple "Parameters" sections → merged into single parameters dict
        - "Parameters" and "Less Used Parameters" → both parsed, main_parameters only includes "Parameters"
        - Multiple "Returns" sections → last one wins
        - Summary text collected from:
          * Text before first section
          * Text between sections
          * All summaries combined with "\\n\\n" separator
    
    **Type Normalization:**
        Python types → JSON-compatible types:
        - "int", "int64", "integer" → "integer"
        - "float", "float64", "number", "double" → "number"
        - "bool", "boolean" → "boolean"
        - "str", "string" → "string"
        - "list", "tuple", "array", "array-like" → "array"
        - "dict", "mapping" → "object"
        - Complex types (pandas.DataFrame, etc.) → "object"
        
        Union type handling:
        - "int or float" → "number" (prefers number over integer)
        - "list or tuple" → "array"
        - "str or bool" → "object" (fallback when no clear preference)
        - Preference order: array > number > integer > object > string
    
    **Edge Cases Handled:**
        - Empty sections (skipped gracefully)
        - Missing sections (returns None/empty dict)
        - Typos in type names → normalized to "object"
        - Parameters with no description → empty string
        - Parameters with no type → "object"
        - Default values in both annotation and description → annotation takes precedence
        - Special parameter name "log" → filtered out from results
        - Tuple defaults → automatically converted to lists for JSON compatibility

    Examples:
        >>> def example_func():
        ...     \"\"\"
        ...     Example function with parameters.
        ...
        ...     Parameters
        ...     ----------
        ...     x : int, default=10
        ...         Description of x with default.
        ...     y : {"low", "medium", "high"}
        ...         Description of y with enum.
        ...     z : array-like
        ...         Description of z with array type.
        ...     typo_example : float or stiring
        ...         Description showing how typos are handled as objects.
        ...     gtf_path : str, default='default'
        ...         Path to GTF file for gene annotation.
        ...         gtf_path options:
        ...         - 'default' : same as 'ensembl'.`build` should be specified.
        ...         - 'ensembl' : GTF from ensembl. `build` should be specified.
        ...         - 'refseq' : GTF from refseq. `build` should be specified.
        ...         - str : path for user provided gtf
        ...
        ...     Returns
        ...     -------
        ...     result : bool
        ...         Description of return value.
        ...     \"\"\"
        ...     pass

        >>> def multi_section_func():
        ...     \"\"\"
        ...     Function with multiple parameter sections.
        ...
        ...     Parameters
        ...     ----------
        ...     a : str
        ...         Description of a.
        ...
        ...     Less Used Parameters
        ...     --------------------
        ...     b : float or string, optional, default=None
        ...         Description of b with union type and default.
        ...
        ...     Parameters
        ...     ----------
        ...     c : int
        ...         Description of c (repeated section).
        ...     \"\"\"
        ...     pass

        >>> def returns_type_only_example():
        ...     \"\"\"
        ...     Function with Returns section (type only format).
        ...
        ...     Returns
        ...     -------
        ...     pandas.DataFrame
        ...         Updated summary statistics DataFrame with inferred build version.
        ...         When called via :meth:\`Sumstats.infer_build()\`, updates the Sumstats object in place
        ...         (modifies \`\`self.data\`\`, \`\`self.build\`\`, and \`\`self.meta["gwaslab"]["genome_build"]\`\`)
        ...         and the method returns \`\`None\`\`.
        ...     \"\"\"
        ...     pass

        >>> def enum_and_defaults_example():
        ...     \"\"\"
        ...     Function demonstrating enum types and various default formats.
        ...
        ...     Parameters
        ...     ----------
        ...     build : {"19", "38"}
        ...         Genome build. Default is "38".
        ...     mode : {'fast', 'slow'}, default='fast'
        ...         Processing mode.
        ...     threshold : float
        ...         Threshold value. Default: 0.05
        ...     enabled : bool
        ...         Enable feature. Default is True.
        ...     size : tuple, default=(10, 20)
        ...         Size tuple (converted to list [10, 20]).
        ...     \"\"\"
        ...     pass

    Returns:
        dict: Parsed docstring information with the following structure:
        
        {
          "description": str
              Combined summary text from all locations (before sections, between sections).
              Multiple summaries joined with "\\n\\n".
          
          "parameters": dict
              All parameters from all "Parameters" and "Less Used Parameters" sections.
              Merged into single dictionary. Key is parameter name, value is:
              {
                 "type": str,           # JSON-compatible type: "integer", "number", "string", 
                                         # "boolean", "array", "object"
                 "default": any,         # Python value (None, int, float, str, bool, list, dict)
                                         # Tuples converted to lists for JSON compatibility
                 "description": str,     # Full multi-line description (preserves formatting)
                 "enum": list,           # Optional: list of enum values if type is enum
                 "required": bool        # True if no default value, False if optional/has default
              }
          
          "main_parameters": dict
              Only parameters from "Parameters" sections (excludes "Less Used Parameters").
              Same structure as "parameters" dict.
          
          "returns": dict or None
              Parsed Returns section information (None if no Returns section):
              {
                 "name": str,            # Return value name (default: "return_value")
                 "type": str,            # Normalized type: "integer", "number", "string", etc.
                 "description": str,    # Full multi-line description
                 "enum": list            # Optional: enum values if return type is enum
              }
        }
    
    Notes:
        - All type names are normalized to JSON-compatible types (integer, number, string, 
          boolean, array, object)
        - Complex types (pandas.DataFrame, numpy.ndarray, etc.) are normalized to "object"
        - Enum types are detected from curly brace notation: {"option1", "option2"}
        - Default values are extracted from both type annotations and description text
        - Tuple defaults are automatically converted to lists for JSON compatibility
        - The "log" parameter is automatically filtered out from results
        - Multiple "Parameters" sections are merged; "main_parameters" only includes 
          the main "Parameters" sections
        - Summary text is collected from text before and between sections
    """
    doc = inspect.getdoc(obj) or ""
    lines = doc.splitlines()
    n = len(lines)

    # Initialize data structures
    summaries = []
    parameters = {}
    main_parameters = {}
    returns_info = None

    # Collect first summary (before any sections)
    first_summary, i = _collect_until_section(lines, 0)
    if first_summary:
        summaries.append(first_summary)

    current_section_is_main = True  # Default: first Parameters block is main

    # Main parsing loop
    while i < n:
        line = lines[i].strip()
        key = line.rstrip(":").lower()

        # Handle Parameters sections
        if key == "parameters":
            current_section_is_main = True
            skip = _is_section_header(lines, i, "Parameters")
            i += skip
            i = _parse_parameters_section(
                lines, i, current_section_is_main, parameters, main_parameters
            )
            continue

        # Handle Less Used Parameters sections
        elif key == "less used parameters":
            current_section_is_main = False
            skip = _is_section_header(lines, i, "Less Used Parameters")
            i += skip
            i = _parse_parameters_section(
                lines, i, current_section_is_main, parameters, main_parameters
            )
            continue

        # Handle Returns section
        elif key == "returns":
            skip = _is_section_header(lines, i, "Returns")
            i += skip
            i, returns_info = _parse_returns_section(lines, i)
            continue

        # Handle other recognized sections: skip block
        elif key in SECTION_NAMES:
            skip = _is_section_header(lines, i, line.rstrip(":"))
            i += skip
            # Move to next section start
            while i < n:
                line = lines[i].strip()
                if line.rstrip(":").lower() in SECTION_NAMES:
                    break
                i += 1
            continue

        # Any loose text between sections counts as an additional summary
        extra_summary, i = _collect_until_section(lines, i)
        if extra_summary:
            summaries.append(extra_summary)

    # Post-process parameters
    parameters, main_parameters = _post_process_parameters(parameters, main_parameters)

    # Combine summaries
    combined_summary = "\n\n".join([s for s in summaries if s])

    # Ensure array items are properly structured
    ensure_items_for_arrays(parameters)
    ensure_items_for_arrays(main_parameters)

    return {
        "description": combined_summary.strip(),
        "parameters": parameters,  # full param dictionary
        "main_parameters": main_parameters,  # only main section parameters
        "returns": returns_info  # parsed Returns section information
    }


def ensure_items_for_arrays(params):
    """
    Ensure array and object types have required schema properties.
    
    For arrays:
    - Add 'items' property if missing
    - Infer item type from enum or default value
    
    For objects:
    - Add 'additionalProperties' if missing (required by Azure)
    """
    for k, v in params.items():
        if v.get("type") != "array":
            continue

        # If items already exists, skip
        if "items" in v:
            continue

        # Enum → array of enums
        if v.get("enum"):
            v["items"] = {"type": "string", "enum": v["enum"]}
            continue

        # Default-based inference
        d = v.get("default")
        if isinstance(d, list) and d:
            elem = d[0]
            if isinstance(elem, bool):
                t = "boolean"
            elif isinstance(elem, int):
                t = "integer"
            elif isinstance(elem, float):
                t = "number"
            elif isinstance(elem, dict):
                t = "object"
            else:
                t = "string"
            v["items"] = {"type": t}
            continue

        # Fallback safe
        v["items"] = {"type": "string"}

    # Ensure objects have additionalProperties
    for k, v in params.items():
        if v.get("type") == "object":
            # Azure requires additionalProperties or properties
            if "properties" not in v and "additionalProperties" not in v:
                v["additionalProperties"] = {"type": "string"}


def fix_array_items(schema: dict):
    """
    Ensure every array type in schema has 'items'. Azure will error otherwise.
    Apply recursively.
    """
    if not isinstance(schema, dict):
        return

    if schema.get("type") == "array":
        if "items" not in schema:
            # safe fallback
            schema["items"] = {"type": "string"}

    # Deep fix for nested objects
    for key, value in schema.items():
        if isinstance(value, dict):
            fix_array_items(value)
        elif isinstance(value, list):
            for v in value:
                fix_array_items(v)

import json
import re
import numpy as np
import pandas as pd
from collections.abc import Iterable
import traceback

_DF_QUERY_RE = re.compile(r"^(df_\d+)\.query\((.*)\)\.([A-Za-z0-9_]+)(?:\[:?(\d+)\])?$")
_DF_SIMPLE_RE = re.compile(r"(df_\d+)\.([A-Za-z0-9_]+)(?:\[:?(\d+)\])?")

def _success_json(method_name, out_type, data, log_text):
    return json.dumps(
        {
            "status": "success",
            "method": method_name,
            "type": out_type,
            "data": data,
            "log": log_text.strip() if log_text else "",
        },
        ensure_ascii=False,
    )

def _ci_lookup_column(df, name):
    if name in df.columns:
        return name
    n = str(name).lower()
    for c in df.columns:
        if str(c).lower() == n:
            return c
    return name

def _materialize_column(df, column_name, slice_len):
    col = _ci_lookup_column(df, column_name)
    s = df[col]
    if isinstance(slice_len, str):
        s = s.iloc[:int(slice_len)]
    if isinstance(s, pd.Series):
        return s.tolist()
    if isinstance(s, np.ndarray):
        return s.tolist()
    return list(s) if isinstance(s, Iterable) else s

def _df_payload(df, max_rows, max_cols, registry=None, include_columns=False):
    if isinstance(df.index, pd.MultiIndex):
        df = df.reset_index()
    total_rows = int(len(df))
    total_cols = int(df.shape[1])
    preview = df.iloc[:max_rows, :max_cols]
    try:
        preview_str = preview.to_markdown(index=False)
    except Exception:
        preview_str = preview.to_string(index=False)
    
    # Clean up preview_str: strip extra spaces and normalize whitespace
    if preview_str:
        lines = preview_str.split('\n')
        # Strip leading/trailing whitespace from each line
        lines = [line.rstrip() for line in lines]
        # Remove trailing empty lines
        while lines and not lines[-1].strip():
            lines.pop()
        # Remove leading empty lines
        while lines and not lines[0].strip():
            lines.pop(0)
        # Rejoin with single newlines (normalize line breaks)
        preview_str = '\n'.join(lines)
    
    # Get column information
    column_names = df.columns.tolist()
    column_dtypes = {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)}
    
    # Sample data types and non-null counts for better understanding
    sample_info = {}
    for col in column_names[:min(10, total_cols)]:  # Sample first 10 columns
        col_data = df[col]
        sample_info[col] = {
            "dtype": str(col_data.dtype),
            "non_null": int(col_data.notna().sum()),
            "null_count": int(col_data.isna().sum()),
            "sample_values": col_data.dropna().head(3).tolist() if col_data.notna().any() else []
        }
    
    out = {
        "description": f"DataFrame with {total_rows:,} rows and {total_cols} columns",
        "preview": preview_str,
        "rows": total_rows,
        "cols": total_cols,
        "column_names": column_names,
        "column_dtypes": column_dtypes,
        "sample_column_info": sample_info,
        "truncated_rows": total_rows > max_rows,
        "truncated_cols": total_cols > max_cols,
        "usage_note": "This DataFrame is registered and can be accessed directly in scripts using its result_id (e.g., df_X.COLUMN_NAME expressions)."
    }
    if include_columns:
        out["columns"] = column_names
    if registry is not None:
        result_id = registry.put(df)
        out["result_id"] = result_id
        out["usage_note"] = f"This DataFrame is registered as '{result_id}'. Access it directly in scripts using '{result_id}.COLUMN_NAME' expressions."
    return out

def _series_payload(series, max_items=1000):
    total_items = int(len(series))
    dtype_str = str(series.dtype)
    non_null = int(series.notna().sum())
    null_count = int(series.isna().sum())
    
    # Get basic statistics if numeric
    stats = {}
    if pd.api.types.is_numeric_dtype(series):
        try:
            stats = {
                "min": float(series.min()) if not series.empty else None,
                "max": float(series.max()) if not series.empty else None,
                "mean": float(series.mean()) if not series.empty else None,
                "median": float(series.median()) if not series.empty else None,
            }
        except Exception:
            pass
    
    series_dict = series.to_dict()
    
    if total_items > max_items:
        preview = series.iloc[:max_items]
        return {
            "description": f"pandas Series with {total_items:,} items (dtype: {dtype_str})",
            "preview": preview.to_dict(),
            "size": total_items,
            "dtype": dtype_str,
            "non_null_count": non_null,
            "null_count": null_count,
            "statistics": stats if stats else None,
            "truncated": True,
            "usage_note": f"Series contains {total_items:,} values. First {max_items} items shown in preview. Use .tolist() to convert to list if needed."
        }
    
    # For smaller series, return dict directly, but add metadata
    # The dict itself serves as the data, and we add description as a separate field if needed
    return series_dict

def _ndarray_payload(arr, max_size=10000, preview_count=1000):
    shape = list(arr.shape)
    dtype_str = str(arr.dtype)
    size = int(arr.size)
    ndim = arr.ndim
    
    # Get statistics if numeric
    stats = {}
    if np.issubdtype(arr.dtype, np.number):
        try:
            stats = {
                "min": float(np.nanmin(arr)),
                "max": float(np.nanmax(arr)),
                "mean": float(np.nanmean(arr)),
                "std": float(np.nanstd(arr)),
            }
        except Exception:
            pass
    
    if arr.size > max_size:
        preview = arr.ravel()[:min(arr.size, preview_count)].tolist()
        return {
            "description": f"NumPy array with shape {shape} ({ndim}D, dtype: {dtype_str}, {size:,} total elements)",
            "preview": preview,
            "shape": shape,
            "ndim": ndim,
            "dtype": dtype_str,
            "size": size,
            "statistics": stats if stats else None,
            "truncated": True,
            "usage_note": f"Large array with {size:,} elements. First {preview_count} elements shown in preview. Use .tolist() to convert full array to list."
        }
    
    return {
        "description": f"NumPy array with shape {shape} ({ndim}D, dtype: {dtype_str}, {size:,} elements)",
        "data": arr.tolist(),
        "shape": shape,
        "ndim": ndim,
        "dtype": dtype_str,
        "size": size,
        "statistics": stats if stats else None,
        "usage_note": "Complete array data. Use .tolist() to convert to list if needed."
    }

def _list_tuple_payload(seq, max_items=1000):
    total_items = int(len(seq))
    seq_type = type(seq).__name__
    
    # Analyze content type
    if total_items > 0:
        first_item = seq[0]
        item_type = type(first_item).__name__
        # Check if all items are same type
        all_same_type = all(type(item) == type(first_item) for item in seq[:min(100, total_items)])
        content_info = {
            "first_item_type": item_type,
            "all_same_type": all_same_type if total_items <= 100 else "unknown (too large to check)",
        }
    else:
        content_info = {"note": "Empty sequence"}
    
    if isinstance(total_items, int) and total_items > max_items:
        return {
            "description": f"{seq_type} with {total_items:,} items",
            "preview": list(seq[:max_items]),
            "size": total_items,
            "type": seq_type,
            "content_info": content_info,
            "truncated": True,
            "usage_note": f"Large {seq_type} with {total_items:,} items. First {max_items} items shown in preview."
        }
    
    return {
        "description": f"{seq_type} with {total_items:,} items",
        "data": seq,
        "size": total_items,
        "type": seq_type,
        "content_info": content_info,
        "usage_note": f"Complete {seq_type} data."
    }

def build_payload_for_result(
    result,
    registry=None,
    df_rows=20,
    df_cols=20,
    include_columns=False,
    series_max_items=100,
    ndarray_max_size=1000,
    ndarray_preview_count=100,
    list_max_items=100,
):
    if isinstance(result, pd.DataFrame):
        out_type = "DataFrame"
        data = _df_payload(
            result,
            max_rows=df_rows,
            max_cols=df_cols,
            registry=registry,
            include_columns=include_columns,
        )
        return out_type, data
    if isinstance(result, pd.Series):
        out_type = "Series"
        data = _series_payload(result, max_items=series_max_items)
        # Add metadata for smaller series that return dict directly
        if isinstance(data, dict) and "description" not in data:
            total_items = int(len(result))
            dtype_str = str(result.dtype)
            non_null = int(result.notna().sum())
            # Wrap in metadata structure
            data = {
                "description": f"pandas Series with {total_items:,} items (dtype: {dtype_str})",
                "data": data,  # The actual dict data
                "size": total_items,
                "dtype": dtype_str,
                "non_null_count": non_null,
                "null_count": int(result.isna().sum()),
                "usage_note": "Complete Series data as dictionary. Access values using dict[key] or convert to list."
            }
        return out_type, data
    if isinstance(result, np.ndarray):
        out_type = "ndarray"
        data = _ndarray_payload(
            result,
            max_size=ndarray_max_size,
            preview_count=ndarray_preview_count,
        )
        return out_type, data
    if isinstance(result, (list, tuple)):
        out_type = type(result).__name__
        data = _list_tuple_payload(result, max_items=list_max_items)
        return out_type, data
    if isinstance(result, dict):
        return "dict", {
            "description": f"Dictionary with {len(result)} keys",
            "data": result,
            "keys": list(result.keys())[:20],  # Show first 20 keys
            "total_keys": len(result),
            "usage_note": "Dictionary data. Access values using dict['key'] or dict.get('key')."
        }
    from numbers import Number
    if isinstance(result, Number):
        number_type = "integer" if isinstance(result, int) else "float"
        return "number", {
            "description": f"{number_type} value",
            "value": result,
            "type": number_type,
            "usage_note": "Numeric value that can be used in calculations or comparisons."
        }
    if isinstance(result, str):
        str_len = len(result)
        return "string", {
            "description": f"String with {str_len:,} characters",
            "value": result,
            "length": str_len,
            "truncated": str_len > 1000,
            "preview": result[:1000] if str_len > 1000 else result,
            "usage_note": "String value. Use directly or convert to other types as needed."
        }
    if result is None:
        return "none", {
            "description": "No return value",
            "message": "Executed successfully (no return value).",
            "usage_note": "Operation completed successfully but did not return any data."
        }
    data = json.loads(json.dumps(result, default=str))
    return "unknown_jsonable", {
        "description": f"JSON-serializable object of type {type(result).__name__}",
        "data": data,
        "type": type(result).__name__,
        "usage_note": "Data has been serialized to JSON format."
    }

def build_error_payload(self, method_name, e, scrubber=None):
    err_log = ""
    if hasattr(self.log, "getvalue"):
        err_log = self.log.getvalue()
    if callable(scrubber):
        err_log = scrubber(err_log)
    return json.dumps({
        "status": "error",
        "method": method_name,
        "error": str(e),
        "log": err_log.strip(),
        "traceback": traceback.format_exc()
    }, ensure_ascii=False)

def _convert_str_slicing_to_query_compatible(expr):
    """
    Convert string slicing operations in filter expressions to pandas query-compatible format.
    
    Converts patterns like:
    - COLUMN.str[:N] == 'value' → COLUMN.str.startswith('value') (if len(value) == N)
    - COLUMN.str[:N] != 'value' → ~COLUMN.str.startswith('value') (if len(value) == N)
    - COLUMN.str[0:N] == 'value' → COLUMN.str.startswith('value') (if len(value) == N)
    - COLUMN.str[0:N] != 'value' → ~COLUMN.str.startswith('value') (if len(value) == N)
    
    This is needed because pandas query() doesn't support string slicing directly.
    """
    import re
    
    if not isinstance(expr, str):
        return expr
    
    # Pattern: COLUMN.str[:N] == 'value' or COLUMN.str[:N] != 'value'
    # Also handle COLUMN.str[0:N] patterns
    # Match the full comparison expression
    pattern_eq = r'(\w+)\.str\[(?:0:)?(\d+)\]\s*==\s*[\'"]([^\'"]+)[\'"]'
    pattern_ne = r'(\w+)\.str\[(?:0:)?(\d+)\]\s*!=\s*[\'"]([^\'"]+)[\'"]'
    
    def replace_eq(match):
        column = match.group(1)
        slice_len = int(match.group(2))
        value = match.group(3)
        # Convert to startswith if the value length matches the slice length
        if len(value) == slice_len:
            return f"{column}.str.startswith('{value}')"
        # If lengths don't match, try to handle it differently
        # For now, return original and let pandas handle the error
        return match.group(0)
    
    def replace_ne(match):
        column = match.group(1)
        slice_len = int(match.group(2))
        value = match.group(3)
        # Convert to ~startswith if the value length matches the slice length
        if len(value) == slice_len:
            return f"~{column}.str.startswith('{value}')"
        # If lengths don't match, return original
        return match.group(0)
    
    # Apply conversions (order matters - do != before == to avoid conflicts)
    expr_modified = re.sub(pattern_ne, replace_ne, expr)
    expr_modified = re.sub(pattern_eq, replace_eq, expr_modified)
    
    return expr_modified

def prepare_kwargs(self, name, method, kwargs, filterer_set, resolver):
    if (
        isinstance(name, str)
        and (name in filterer_set or name.startswith("filter"))
        and ("inplace" not in kwargs)
    ):
        import inspect as _inspect
        sig = _inspect.signature(method)
        if "inplace" in sig.parameters:
            kwargs["inplace"] = False
    
    # Preprocess filter expressions to convert string slicing to query-compatible format
    if (
        isinstance(name, str)
        and (name in filterer_set or name.startswith("filter"))
        and "expr" in kwargs
        and isinstance(kwargs["expr"], str)
    ):
        kwargs["expr"] = _convert_str_slicing_to_query_compatible(kwargs["expr"])
    
    kwargs = resolver(self, kwargs)
    return kwargs

def image_payload(name, result, log_text, is_figure, show_locally, message):
    if is_callable(is_figure) and is_figure(result):
        if is_callable(show_locally):
            show_locally(result)
        return json.dumps({
            "status": "success",
            "method": name,
            "type": "image_redacted",
            "data": message,
            "log": log_text
        }, ensure_ascii=False)
    return None

def is_callable(fn):
    return callable(fn)

def sumstats_payload(self, name, result, previous_log_end, filterer_set, scrubber):
    import gwaslab as _gl
    if isinstance(result, _gl.Sumstats):
        if isinstance(name, str) and name in filterer_set:
            obj_id = self.RESULTS.put(result)
            new_log = self.RESULTS.get(obj_id).log.log_text[previous_log_end + 1:]
            
            # Get basic info about the filtered Sumstats
            try:
                variant_count = len(result.data) if hasattr(result, 'data') and result.data is not None else "unknown"
                description = f"Filtered Sumstats object with {variant_count:,} variants" if isinstance(variant_count, int) else "Filtered Sumstats object"
            except Exception:
                description = "Filtered Sumstats object"
            
            return {
                "status": "success",
                "type": "filtered Sumstats object",
                "description": description,
                "result_id": obj_id,
                "instructions": (
                    f"This filtered Sumstats object is registered as '{obj_id}'. "
                    f"Access it directly in scripts using '{obj_id}' for visualization and processing. "
                    f"Available operations include: head(), tail(), plot_*(), filter_*(), get_*(), and other Sumstats methods."
                ),
                "usage_note": (
                    f"Access this object directly in scripts using '{obj_id}'. "
                    f"Example: {obj_id}.head(n=10) to see first 10 rows."
                ),
                "log": scrubber(new_log) if is_callable(scrubber) else new_log,
            }
        else:
            new_log = self.log.log_text[previous_log_end:]
            return json.dumps({
                "status": "success",
                "method": name,
                "type": "none",
                "data": "Executed successfully (no return value).",
                "log": scrubber(new_log) if is_callable(scrubber) else new_log
            }, ensure_ascii=False)
    return None

def _parse_container_string(s):
    s = s.strip()
    if (s.startswith("[") and s.endswith("]")) or (s.startswith("{") and s.endswith("}")):
        return json.loads(s)
    return None

def _resolve_query_expr(self, match):
    frame_id = match.group(1)
    query_expr = match.group(2).strip()
    if (query_expr.startswith('"') and query_expr.endswith('"')) or (query_expr.startswith("'") and query_expr.endswith("'")):
        query_expr = query_expr[1:-1]
    column_name = match.group(3)
    slice_len = match.group(4)
    frame = self.RESULTS.get(frame_id)
    filtered_frame = frame.query(query_expr, engine="python")
    return _materialize_column(filtered_frame, column_name, slice_len)


def _is_safe_ast(tree):
    import ast

    valid_nodes = (
        ast.Expression, ast.Attribute, ast.Subscript, ast.Call,
        ast.Name, ast.Load, ast.Constant, ast.Slice, ast.Index, ast.Tuple, ast.List,
        ast.Str, ast.Num, ast.keyword,
        ast.Compare, ast.BinOp, ast.UnaryOp, ast.BoolOp,
        ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In, ast.NotIn,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.LShift, ast.RShift,
        ast.BitOr, ast.BitXor, ast.BitAnd, ast.MatMult,
        ast.UAdd, ast.USub, ast.Not, ast.Invert,
        ast.And, ast.Or
    )

    for node in ast.walk(tree):
        if not isinstance(node, valid_nodes):
            return False
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            return False
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in ("list", "len", "set", "tuple", "dict", "int", "float", "str", "bool"):
                continue
            if not isinstance(node.func, ast.Attribute):
                return False
    return True


def _eval_in_registry(self, value):
    try:
        import ast
        tree = ast.parse(value, mode="eval")
    except Exception:
        return value
    if not _is_safe_ast(tree):
        return value
    local_context = self.RESULTS.copy()
    safe_globals = {
        "__builtins__": {},
        "list": list,
        "len": len,
        "set": set,
        "tuple": tuple,
        "dict": dict,
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
    }
    try:
        return eval(value, safe_globals, local_context)
    except Exception:
        return value


def _resolve_simple_expr(self, match):
    frame_id = match.group(1)
    key = match.group(2)
    slice_len = match.group(3)
    frame = self.RESULTS.get(frame_id)

    if key in ("shape",):
        return frame.shape
    if key in ("columns",):
        return frame.columns.tolist() if hasattr(frame.columns, "tolist") else list(frame.columns)
    if key in ("index",):
        return frame.index.tolist() if hasattr(frame.index, "tolist") else list(frame.index)
    if key in ("iloc", "loc"):
        if slice_len is None:
            return getattr(frame, key)
        try:
            idx = int(slice_len)
            return getattr(frame, key)[idx]
        except Exception:
            expr = f"{frame_id}.{key}[{slice_len}]"
            return _eval_in_registry(self, expr)

    return _materialize_column(frame, key, slice_len)

def _resolve_df_value(self, value):
    if isinstance(value, str):
        import re as _re
        if _re.fullmatch(r"df_\d+$", value):
            return value
        parsed = _parse_container_string(value)
        if isinstance(parsed, list):
            return [_resolve_df_value(self, item) for item in parsed]
        if isinstance(parsed, dict):
            return {key: _resolve_df_value(self, inner_value) for key, inner_value in parsed.items()}
        
        # 1. Try regex matching for simple cases (speed optimization)
        m = _DF_QUERY_RE.fullmatch(value)
        if m:
            return _resolve_query_expr(self, m)
        m = _DF_SIMPLE_RE.fullmatch(value)
        if m:
            return _resolve_simple_expr(self, m)
            
        # 2. Try to evaluate if it looks like a df operation (starts with df_ or list(df_))
        # This allows for arbitrary pandas operations like df_0.CHR.iloc[0] or df_0.loc[0, 'CHR']
        # Also supports simple wrapping functions like list()
        stripped_value = value.strip()
        is_df_expr = stripped_value.startswith("df_")
        is_list_expr = stripped_value.startswith("list(") and "df_" in stripped_value
        
        if (is_df_expr or is_list_expr) and hasattr(self, "RESULTS"):
            resolved_value = _eval_in_registry(self, value)
            if isinstance(resolved_value, (pd.Series, np.ndarray)):
                return resolved_value.tolist()
            return resolved_value



        return value
    if isinstance(value, list):
        return [_resolve_df_value(self, item) for item in value]
    if isinstance(value, dict):
        return {key: _resolve_df_value(self, inner_value) for key, inner_value in value.items()}
    return value

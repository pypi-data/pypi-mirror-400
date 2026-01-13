import pandas as pd
import json
import numpy as np
from numbers import Number
import traceback
import inspect
import gwaslab as gl
from gwaslab_agent.core.g_image import _scrub_log
from gwaslab_agent.core.g_image import _show_locally
from gwaslab_agent.core.g_image import _is_figure
from gwaslab_agent.tools.g_tools import FILTERER_SET
from gwaslab_agent.history.g_history_stages import TOOL_EXECUTION
from gwaslab_agent.tools.g_warp_tools_helper import (
    _success_json,
    _df_payload,
    _series_payload,
    _ndarray_payload,
    _list_tuple_payload,
    _resolve_df_value,
    build_payload_for_result,
    build_error_payload,
    prepare_kwargs,
    image_payload,
    sumstats_payload,
)

def _normalize_readargs_escape_sequences(kwargs):
    """Normalize escape sequences in readargs.sep to prevent pandas regex warnings.
    
    Converts literal escape sequences like '\\t' to actual tab character '\t'.
    This fixes the issue where LLM provides '\\t' (string with backslash-t) 
    instead of '\t' (actual tab), causing pandas to use regex engine.
    """
    if 'readargs' not in kwargs:
        return kwargs
    
    readargs = kwargs.get('readargs')
    if not isinstance(readargs, dict):
        return kwargs
    
    if 'sep' in readargs and isinstance(readargs['sep'], str):
        sep = readargs['sep']
        # Map common escape sequences
        escape_map = {
            '\\t': '\t',  # Tab
            '\\n': '\n',  # Newline
            '\\r': '\r',  # Carriage return
            '\\s': ' ',  # Space (though ' ' is more common)
        }
        # Check if sep matches any escape sequence pattern
        if sep in escape_map:
            readargs = readargs.copy()  # Don't modify original dict
            readargs['sep'] = escape_map[sep]
            kwargs = kwargs.copy()  # Don't modify original kwargs
            kwargs['readargs'] = readargs
    
    return kwargs

def wrap_loader_method(self, name, method):
    def wrapped(**kwargs):
        previous_log_end = len(self.log.log_text)
        # Normalize escape sequences in readargs to prevent pandas regex warnings
        kwargs = _normalize_readargs_escape_sequences(kwargs)
        try:
            result = method(**kwargs)
        except Exception as e:
            return build_error_payload(self, name, e, _scrub_log)
        # Store original result for processing
        original_result = result
        # Add stage to archive entry - result can be any type, wrap if needed
        if isinstance(result, dict):
            archive_entry = dict(result)  # Create a copy to avoid modifying original
            archive_entry["stage"] = TOOL_EXECUTION
        else:
            archive_entry = {"result": result, "stage": TOOL_EXECUTION}
        self.archive.append(archive_entry)
        new_log = self.log.log_text[previous_log_end:]
        
        if isinstance(original_result, gl.Sumstats):
            out_type = "gl.Sumstats"
            data_string = "Sumstats has been successfully loaded."
            self.sumstats.data = original_result.data
            self.sumstats.meta = original_result.meta
            self.sumstats.build = original_result.build
            self.log.combine(original_result.log,pre=False)
            new_log = self.log.log_text[previous_log_end + 1:]
            return _success_json(name, out_type, data_string, new_log)

        else:
            out_type, data = build_payload_for_result(
                original_result,
                registry=None,
                df_rows=5,
                df_cols=20,
                include_columns=True,
                series_max_items=100,
                ndarray_max_size=1000,
                ndarray_preview_count=100,
                list_max_items=100,
            )

        return _success_json(name, out_type, data, new_log)
    return wrapped


def wrap_main_agent_method(self, name, method):
    def wrapped(**kwargs):
        previous_log_end = len(self.log.log_text)
        kwargs = prepare_kwargs(self, name, method, kwargs, FILTERER_SET, _resolve_df_value)
        try:
            result = method(**kwargs)
        except Exception as e:
            return build_error_payload(self, name, e, _scrub_log)
        
        # Store original result for processing
        original_result = result
        # Add stage to archive entry - result can be any type, wrap if needed
        if isinstance(result, dict):
            archive_entry = dict(result)  # Create a copy to avoid modifying original
            archive_entry["stage"] = TOOL_EXECUTION
        else:
            archive_entry = {"result": result, "stage": TOOL_EXECUTION}
        self.archive.append(archive_entry)
        new_log = self.log.log_text[previous_log_end:]
        new_log = _scrub_log(new_log)

        if isinstance(original_result, dict) and "result_id" in original_result:
            obj_id = original_result["result_id"]
            obj = self.RESULTS.get(obj_id)
            original_result = obj

        img_payload = image_payload(
            name,
            original_result,
            new_log,
            _is_figure,
            _show_locally,
            "Image/figure creation finished.",
        )
        if img_payload is not None:
            return img_payload

        ss_payload = sumstats_payload(self, name, original_result, previous_log_end, FILTERER_SET, _scrub_log)
        if ss_payload is not None:
            return ss_payload

        else:
            out_type, data = build_payload_for_result(
                original_result,
                registry=self.RESULTS,
                df_rows=5,
                df_cols=40,
                include_columns=False,
                series_max_items=100,
                ndarray_max_size=1000,
                ndarray_preview_count=100,
                list_max_items=100,
            )

        return json.dumps({
            "status": "success",
            "method": name,
            "type": out_type,
            "data": data,
            "log": _scrub_log(new_log)
        }, ensure_ascii=False)
    return wrapped

# ===== Standard Library =====
import inspect
import json
import os
import sys
from numbers import Number
from typing import get_type_hints

# ===== Third-Party Libraries =====
import numpy as np
import pandas as pd
from langchain.agents.middleware import after_model, wrap_tool_call
from langchain_core.messages import ToolMessage
from langchain_core.tools import StructuredTool

# ===== Project: GWASLab =====
import gwaslab as gl

# ===== Project: GWASLab Agent =====
from gwaslab_agent.core.g_docstring_parser import parse_numpy_style_params
from gwaslab_agent.data.d_data_registry import DataRegistry
from gwaslab_agent.tools.g_tools import HARMONIZER_SET, DOWNSTREAM_SET, PLOTTER_SET, FILTERER_SET, EXCLUDED_SUMSTATS_METHODS
from gwaslab_agent.core.g_image import _is_figure

RESULTS = DataRegistry()

from langchain_core.messages import AIMessage
import json5
import json

@wrap_tool_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors with custom messages."""
    try:
        return handler(request)
    except Exception as e:
        # Return a custom error message to the model
        return ToolMessage(
            content=f"Tool error: Please check your input and try again. ({str(e)})",
            tool_call_id=request.tool_call["id"]
        )
    
def retry_tool_wrapper(max_retries=3):
    """Return a wrap_tool_call function that retries failed tool calls."""
    @wrap_tool_call
    def wrapper(request, handler):
        tool_name = request.tool_call["name"]   # FIXED
        retries = 0

        while True:
            try:
                return handler(request)

            except Exception as e:
                retries += 1

                if retries >= max_retries:
                    return ToolMessage(
                        content=(
                            f"Tool error: `{tool_name}` failed after "
                            f"{max_retries} retries. Last error: {e}"
                        ),
                        tool_call_id=request.tool_call["id"]
                    )

                print(f"[Tool Retry] {tool_name}: attempt {retries}/{max_retries}")

    return wrapper

def _build_tools_from_methods(self, verbose=True):
    tools = []
    ########################################################################################################
    # gl.Sumstats
    for name, method in inspect.getmembers(self.sumstats, predicate=inspect.ismethod):
        if name.startswith("_"):
            continue
        if name in EXCLUDED_SUMSTATS_METHODS:
            continue
        detailed_docs, all_schema, schema  = _build_args_schema(method, if_sig=False)
        # Store all_schema (includes _returns if available) in full_schema
        self.full_schema[name] = all_schema
        # Also store return info in schema for easy access
        if "_returns" in all_schema:
            if not isinstance(schema, dict):
                schema = {"type": "object", "properties": {}, "required": []}
            schema["returns"] = all_schema["_returns"]

        wrapped = self._wrap_method(name, method)

        tool_obj = StructuredTool.from_function(
            func=wrapped,
            name=name,
            description=detailed_docs or "No description provided.",
            args_schema=schema,
        )
        tools.append(tool_obj)
        self.tool_docs[name] = detailed_docs
    ########################################################################################################
    # global
    #excluded_tools = ["get_path","check_available_ref","scatter","run_susie_rss","update_available_ref","update_formatbook","update_record","remove_file"
    #                    "read_popcorn","read_ldsc","rank_based_int","process_vcf_to_hfd5","plot_stacked_mqq","plot_miami2","plot_miami",
    #                    "plot_forest","meta_analyze","load_pickle","h2_se_to_p","h2_obs_to_liab","get_power","download_ref","reset_option","scan_downloaded_files",
    #                    "remove_file","read_tabular"  ,"read_popcorn","dump_pickle","gwascatalog_trait","compare_effect","plot_rg","plot_power_x"
    #                ]
    #for name, method in inspect.getmembers(gl, predicate=inspect.isfunction):
    #    if name.startswith("_"):
    #        continue
    #    if name in excluded_tools:
    #        continue
    #    detailed_docs, all_schema, schema = _build_args_schema(method, if_sig=False)
    #    self.full_schema[name] = all_schema
    #    wrapped = self._wrap_method(name, method)
#
    #    tools.append(
    #        StructuredTool.from_function(
    #            func=wrapped,
    #            name=name,
    #            description=inspect.getdoc(method) or "No description provided.",
    #            args_schema=schema,
    #        )
    #    )
    #    self.tool_docs[name] = detailed_docs
    ########################################################################################################
    # gl.config
    #excluded_tools=["set_option"]
    #for name, method in inspect.getmembers(self.config, predicate=inspect.ismethod):
    #    if name.startswith("_"):
    #        continue
    #    if name in excluded_tools:
    #        continue
    #    detailed_docs, all_schema, schema = _build_args_schema(method, if_sig=False)
    #    self.full_schema[name] = all_schema
    #    wrapped = self._wrap_method(name, method)
    #    tools.append(
    #        StructuredTool.from_function(
    #            func=wrapped,
    #            name=name,
    #            description=inspect.getdoc(method) or "No description provided.",
    #            args_schema=schema,
    #        )
    #    )
    #    self.tool_docs[name] = detailed_docs

    ########################################################################################################
    # run_on_results removed - objects are now directly accessible in script namespace
    # All registered objects (subset_*, df_*) are available directly in scripts
    # Example: Instead of run_on_results(result_id="subset_0", tool_name="head", n=5)
    #          Just use: subset_0.head(n=5) in the script
    ########################################################################################################
    #wrapped = self._wrap_method("search_full_docs", self.search_full_docs)
    #tools.append(
    #    StructuredTool.from_function(
    #        func=wrapped,
    #        name="search_full_docs",
    #        description='Search full documentations including descriptions and arguments for a tool',
    #        args_schema={"tool_name": {"type": "string","description": "tool_name", "eum":list(self.tool_docs.keys())}}
    #    )
    #)
    #########################################################################################################
    #wrapped = self._wrap_method("get_template_script_for_tools", self.get_template_script_for_tools)
    #tools.append(
    #    StructuredTool.from_function(
    #        func=wrapped,
    #        name="get_template_script_for_tools",
    #        description='get examples on how to use a tool',
    #        args_schema={"tool_name": {"type": "string","description": "tool_name", "eum":list(self.tool_docs.keys())}}
    #    )
    #)
    ########################################################################################################
    # get_reference_file_path method removed - reference paths are now resolved via PathManager in the workflow
    # wrapped = self._wrap_method("get_reference_file_path", self.get_reference_file_path)
    # detailed_docs, all_schema, schema = _build_args_schema(self.get_reference_file_path, if_sig=False)
    # grfp_tool = StructuredTool.from_function(
    #     func=wrapped,
    #     name="get_reference_file_path",
    #     description=detailed_docs,
    #     args_schema=schema
    # )
    # tools.append(grfp_tool)
    ########################################################################################################
    #wrapped = self._wrap_method("get_data_from_registry", self.get_data_from_registry)
    #detailed_docs, all_schema, schema = _build_args_schema(self.get_data_from_registry, if_sig=True)
    #gdf_tool = StructuredTool.from_function(
    #    func=wrapped,
    #    name="get_data_from_registry",
    #    description=detailed_docs or "Access DataFrames by evaluating Python expressions against RESULTS.",
    #    args_schema=schema
    #)
    #tools.append(gdf_tool)
    #plot_tools.append(gdf_tool)
    #harmonizer_tools.append(gdf_tool)
    #downstreamer_tools.append(gdf_tool)
    #filter_tools.append(gdf_tool)
    #utility_tools.append(gdf_tool)
    ########################################################################################################
    # Suppress tool registration message when loading via chat
    # self.log.write(f" -Registered {len(tools)} tools for Worker and Planner...", verbose=verbose)
    return tools

def _build_args_schema(func, if_sig=True):
    import inspect
    from typing import get_type_hints

    sig = inspect.signature(func)
    hints = get_type_hints(func)
    
    # Parse NumPy-style docstring parameters
    parsed_dict = parse_numpy_style_params(func)
    doc_description  = parsed_dict["description"]
    doc_params_main =  parsed_dict["main_parameters"]
    doc_params_all =  parsed_dict["parameters"]
    doc_returns = parsed_dict.get("returns")  # Extract Returns section information
    
    props, required = {}, []

    # ------------------------------------------------------------
    # 1) Start from DOC PARAMS (these define the primary argument set)
    # ------------------------------------------------------------
    for name, info in doc_params_main.items():
        arg_schema = {}

        # Always preserve full info dictionary
        arg_schema = dict(info)

        # --------------------------------------------------
        # FIX: invalid defaults for array type
        # --------------------------------------------------
        if arg_schema.get("type") == "array":
            # Azure does NOT allow boolean defaults on array fields
            if isinstance(arg_schema.get("default"), bool):
                arg_schema["default"] = []

            # Null defaults also not ideal for array (Azure sometimes rejects)
            if arg_schema.get("default") is None:
                arg_schema["default"] = []

        # --------------------------------------------------
        # FIX: object defaults must be null or {}
        # --------------------------------------------------
        if arg_schema.get("type") == "object":
            if arg_schema.get("default") in (True, False):
                arg_schema["default"] = None
        #arg_schema = {}

        # directly from docstring
        #if info["description"]:
        #    arg_schema["description"] = info["description"]
        #if info["type"]:
        #    arg_schema["type"] = info["type"]
        #if info["default"] is not None:
        #    arg_schema["default"] = info["default"]
        # Fix invalid defaults for object-type fields

        # supplement type from type hints
        if "type" not in arg_schema and name in hints:
            arg_schema["type"] = hints[name].__name__
        
        if arg_schema.get("type") == "object" and isinstance(arg_schema.get("default"), bool):
            arg_schema["default"] = None

        # supplement default from function signature
        if name in sig.parameters:
            param = sig.parameters[name]
            if "default" not in arg_schema and param.default is not inspect.Parameter.empty:
                arg_schema["default"] = param.default
    
        
        # determine required
        if "default" not in arg_schema:
            required.append(name)

        props[name] = arg_schema

        if "required" in arg_schema:
            del arg_schema["required"]
    # ------------------------------------------------------------
    # 2) Handle parameters *present in signature but absent in docstring*
    # ------------------------------------------------------------
    if if_sig:
        for name, param in sig.parameters.items():
            if name in ("self", "kwargs", "insumstats", "kwreadargs", *doc_params_main.keys()):
                continue

            arg_schema = {}

            # type from type hint
            if name in hints:
                arg_schema["type"] = hints[name].__name__
            else:
                arg_schema["type"] = "string"

            # default from signature
            if param.default is not inspect.Parameter.empty:
                arg_schema["default"] = param.default
            else:
                required.append(name)

            props[name] = arg_schema

    # Build return schema if return information is available
    return_schema = None
    if doc_returns:
        return_schema = {
            "type": doc_returns.get("type", "object"),
            "description": doc_returns.get("description", "")
        }
        if "enum" in doc_returns:
            return_schema["enum"] = doc_returns["enum"]
    
    # Include return information in the schema
    result_schema = {"type": "object", "properties": props, "required": required}
    if return_schema:
        result_schema["returns"] = return_schema
    
    # Also include return info in all_schema for easy access
    all_schema_with_returns = dict(doc_params_all)
    if return_schema:
        all_schema_with_returns["_returns"] = return_schema

    return doc_description, all_schema_with_returns, result_schema

def _build_args_schema_gwaslab(func):
    sig = inspect.signature(func)
    hints = get_type_hints(func)
    props, required = {}, []
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        hint = hints.get(name, str)
        props[name] = {"type": "string"}
        if param.default is inspect.Parameter.empty:
            required.append(name)
    return {"type": "object", "properties": props, "required": required}

from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import json, os
from typing import Union, Optional

GLOBAL_LLM_CACHE = {}


def load_llm_config(path: str) -> Union[dict, list[dict]]:
    """
    Load LLM configuration from JSON file.
    Supports both legacy single-object format and new array format.

    Args:
        path: Path to LLM_KEY file

    Returns:
        dict or list[dict]: Configuration(s) from file
    """
    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config


def select_llm_profile(
    configs: Union[dict, list[dict]],
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> dict:
    """
    Select an LLM profile from configuration(s) based on provider/model criteria.

    Selection rules:
    - If configs is a dict (legacy): return it directly
    - If configs is a list:
      - No criteria: return first item
      - provider only: return first matching provider
      - provider + model: return first matching both
      - No match: raise ValueError with available options

    Args:
        configs: Single dict or list of dicts
        provider: Optional provider name to match
        model: Optional model name to match

    Returns:
        dict: Selected configuration profile

    Raises:
        ValueError: If no matching profile found
    """
    if isinstance(configs, dict):
        if provider is not None and configs.get("provider") != provider:
            raise ValueError(
                f"Provider '{provider}' not found in legacy configuration. "
                f"Available provider: {configs.get('provider', 'unknown')}"
            )
        if model is not None and configs.get("model") != model:
            raise ValueError(
                f"Model '{model}' not found in legacy configuration. "
                f"Available model: {configs.get('model', 'unknown')}"
            )
        return configs

    if not isinstance(configs, list):
        raise ValueError(
            f"Invalid configuration format: expected dict or list, got {type(configs)}"
        )

    if len(configs) == 0:
        raise ValueError("Configuration list is empty")

    if provider is None and model is None:
        return configs[0]

    for cfg in configs:
        if not isinstance(cfg, dict):
            continue

        provider_match = provider is None or cfg.get("provider") == provider
        model_match = model is None or cfg.get("model") == model

        if provider_match and model_match:
            return cfg

    if provider is not None and model is not None:
        available = []
        for cfg in configs:
            if isinstance(cfg, dict):
                p = cfg.get("provider", "unknown")
                m = cfg.get("model", "unknown")
                available.append(f"  - provider: {p}, model: {m}")

        raise ValueError(
            f"No profile found matching provider='{provider}' and model='{model}'. "
            f"Available profiles:\n" + "\n".join(available)
        )
    elif provider is not None:
        available_providers = set()
        for cfg in configs:
            if isinstance(cfg, dict):
                available_providers.add(cfg.get("provider", "unknown"))
        raise ValueError(
            f"No profile found matching provider='{provider}'. "
            f"Available providers: {', '.join(sorted(available_providers))}"
        )

    return configs[0]


def _make_cache_key(config: dict) -> str:
    """
    Create a cache key from configuration dict.
    Uses key fields that uniquely identify an LLM instance.

    Args:
        config: Configuration dictionary

    Returns:
        str: Cache key
    """
    key_parts = [
        config.get("provider", "unknown"),
        config.get("model", ""),
        config.get("base_url", ""),
        config.get("azure_deployment", ""),
        config.get("azure_endpoint", ""),
        config.get("api_version", ""),
    ]
    return "|".join(str(p) for p in key_parts)


def get_llm(log, llm_configuration=None, provider=None, model=None, verbose=True):
    """
    Get or create an LLM instance based on configuration.

    Supports multiple profiles in mLLM_KEY file and selection via provider/model.
    Falls back to LLM_KEY (legacy single profile) if mLLM_KEY doesn't exist.

    Priority:
    1. mLLM_KEY (multiple profiles, array format) - if exists
    2. LLM_KEY (legacy single profile, object format) - if mLLM_KEY doesn't exist
    3. At least one of LLM_KEY or mLLM_KEY must exist

    Args:
        log: Logger instance
        llm_configuration: Optional dict or list[dict] configuration (overrides file)
        provider: Optional provider name to select from multiple profiles
        model: Optional model name to select from multiple profiles
        verbose: Whether to log messages

    Returns:
        LLM instance (ChatOpenAI, AzureChatOpenAI, or ChatGoogleGenerativeAI)
    """
    log.write("Initiating connection to Large Language Model API...", verbose=verbose)

    if llm_configuration is None:
        gwaslab_dir = os.path.expanduser("~/.gwaslab")
        mllm_key_path = os.path.join(gwaslab_dir, "mLLM_KEY")
        llm_key_path = os.path.join(gwaslab_dir, "LLM_KEY")

        if os.path.exists(mllm_key_path):
            configs = load_llm_config(mllm_key_path)
        elif os.path.exists(llm_key_path):
            configs = load_llm_config(llm_key_path)
        else:
            raise FileNotFoundError(
                "Neither LLM_KEY nor mLLM_KEY found in ~/.gwaslab/. "
                "Please create at least one of these files."
            )
    else:
        configs = llm_configuration

    selected_config = select_llm_profile(configs, provider=provider, model=model)
    cache_key = _make_cache_key(selected_config)

    global GLOBAL_LLM_CACHE

    if cache_key in GLOBAL_LLM_CACHE:
        log.write(" -Using cached LLM instance...", verbose=verbose)
        llm_instance = GLOBAL_LLM_CACHE[cache_key]
        # Get model name for cached instance
        model_name = getattr(llm_instance, "model", None) or getattr(
            llm_instance, "model_name", None
        )
        if model_name:
            log.write(f" -Model: {model_name}", verbose=verbose)
    else:
        provider_name = selected_config.get("provider", "openai")
        model_name = selected_config.get("model", "unknown")

        config = {k: v for k, v in selected_config.items() if k != "provider"}

        if provider_name == "openai":
            llm_instance = ChatOpenAI(**config)
            log.write(f" -Detected OpenAI-like API: {model_name}", verbose=verbose)
        elif provider_name == "google":
            llm_instance = ChatGoogleGenerativeAI(**config)
            log.write(f" -Detected Google API: {model_name}", verbose=verbose)
        elif provider_name == "azure":
            llm_instance = AzureChatOpenAI(**config)
            log.write(f" -Detected Azure OpenAI API: {model_name}", verbose=verbose)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")

        GLOBAL_LLM_CACHE[cache_key] = llm_instance

    return llm_instance


# ---------------------------------------------------------------------------------
# Token usage helpers
# ---------------------------------------------------------------------------------

def extract_token_usage(msg):
    usage = getattr(msg, "response_metadata", {}).get("token_usage") \
            or getattr(msg, "usage_metadata", None)
    if not usage:
        return None
    prompt = usage.get("prompt_tokens", usage.get("input_tokens"))
    completion = usage.get("completion_tokens", usage.get("output_tokens"))
    total = usage.get("total_tokens")
    return {
        "input": prompt if isinstance(prompt, int) else 0,
        "output": completion if isinstance(completion, int) else 0,
        "total": total if isinstance(total, int) else None,
    }

def accumulate_token_usage(counter, usage: dict):
    """
    Accumulate token usage into counter.
    
    Supports both dict and TokenTracker objects for counter.
    
    Parameters
    ----------
    counter : dict or TokenTracker
        Token counter to update
    usage : dict
        Token usage dict with 'input', 'output', 'total' keys
    """
    if not isinstance(usage, dict):
        return
    
    p = usage.get("input", 0) or 0
    c = usage.get("output", 0) or 0
    t = usage.get("total")
    if not isinstance(t, int):
        t = p + c
    
    # Handle TokenTracker object
    if hasattr(counter, 'accumulate'):
        # TokenTracker has accumulate() method
        counter.accumulate(p, c)
    # Handle dict
    elif isinstance(counter, dict):
        counter["input"] = counter.get("input", 0) + p
        counter["output"] = counter.get("output", 0) + c
        counter["total"] = counter.get("total", 0) + t
    # Handle TokenTracker with direct attribute access (fallback)
    elif hasattr(counter, 'input') and hasattr(counter, 'output') and hasattr(counter, 'total'):
        counter.input += p
        counter.output += c
        counter.total = counter.input + counter.output

def snapshot_counters(counter):
    """
    Snapshot token counters.
    
    Supports both dict and TokenTracker objects.
    
    Parameters
    ----------
    counter : dict or TokenTracker
        Token counter (dict with 'input', 'output', 'total' keys, or TokenTracker object)
    
    Returns
    -------
    tuple
        (input_tokens, output_tokens, total_tokens)
    """
    # Handle TokenTracker object
    if hasattr(counter, 'to_dict'):
        # TokenTracker has to_dict() method
        counter_dict = counter.to_dict()
        return (
            counter_dict.get("input", 0),
            counter_dict.get("output", 0),
            counter_dict.get("total", 0),
        )
    # Handle dict
    elif isinstance(counter, dict):
        return (
            counter.get("input", 0),
            counter.get("output", 0),
            counter.get("total", 0),
        )
    # Handle TokenTracker with direct attribute access (fallback)
    elif hasattr(counter, 'input') and hasattr(counter, 'output') and hasattr(counter, 'total'):
        return (
            getattr(counter, 'input', 0),
            getattr(counter, 'output', 0),
            getattr(counter, 'total', 0),
        )
    # Fallback: return zeros
    else:
        return (0, 0, 0)

def log_run_totals(log, label: str, start_tuple, end_tuple, verbose=True):
    si, so, st = start_tuple
    ei, eo, et = end_tuple
    di = max(0, ei - si)
    do = max(0, eo - so)
    dt = max(0, et - st)
    # Only log usage if there's actual usage (non-zero counts)
    if dt > 0:
        log.write(f"[USAGE] This {label}: prompt={di}, completion={do}, total={dt}", verbose=verbose)
        log.write(f"[USAGE] Accumulative: prompt={ei}, completion={eo}, total={et}", verbose=verbose)

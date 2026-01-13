from langchain.agents.middleware import SummarizationMiddleware, ModelRetryMiddleware, ToolRetryMiddleware
from gwaslab_agent.tools.g_build_tools import handle_tool_errors

class MiddlewareManager:
    def __init__(self, llm):
        self.llm = llm
        self.config = {
            "summarization": True,
            "tool_retry": True,
            "model_retry": True,
            "summarization_trigger": None,
            "summarization_keep": None,
        }
    def build(self):
        items = []
        if self.config.get("summarization"):
            trig = self.config.get("summarization_trigger")
            keep_conf = self.config.get("summarization_keep")
            trigger = trig if isinstance(trig, (list, tuple)) else ("messages", 24)
            keep = keep_conf if isinstance(keep_conf, (list, tuple)) else ("messages", 12)
            items.append(SummarizationMiddleware(model=self.llm, trigger=trigger, keep=keep))
        items.append(handle_tool_errors)
        if self.config.get("tool_retry"):
            items.append(ToolRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0))
        if self.config.get("model_retry"):
            items.append(ModelRetryMiddleware(max_retries=3, backoff_factor=2.0, initial_delay=1.0))
        return items
    def set_options(self, summarization=None, tool_retry=None, model_retry=None, summarization_trigger=None, summarization_keep=None):
        if summarization is not None:
            self.config["summarization"] = bool(summarization)
        if tool_retry is not None:
            self.config["tool_retry"] = bool(tool_retry)
        if model_retry is not None:
            self.config["model_retry"] = bool(model_retry)
        if summarization_trigger is not None:
            self.config["summarization_trigger"] = summarization_trigger
        if summarization_keep is not None:
            self.config["summarization_keep"] = summarization_keep
    def adjust_for_mode(self, mode, last_plan_steps=0):
        if mode == "plan_run_sum":
            self.set_options(summarization=True)
        elif mode in ("plan", "plan_run"):
            self.set_options(summarization=False)
        elif mode == "run":
            self.set_options(summarization=False)
        else:
            self.set_options(summarization=False)

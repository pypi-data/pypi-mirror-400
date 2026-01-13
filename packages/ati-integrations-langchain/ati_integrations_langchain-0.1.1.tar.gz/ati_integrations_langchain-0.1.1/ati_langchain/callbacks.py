from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from opentelemetry.trace import Span

from ati_sdk import AtiConfig, AtiTracer
from ati_sdk.semantics import AtiSpanType, ATI_ATTR

try:
    from langchain_core.callbacks import BaseCallbackHandler
except ImportError:
    try:
        from langchain.callbacks.base import BaseCallbackHandler
    except ImportError:  # pragma: no cover
        BaseCallbackHandler = object  # type: ignore


@dataclass(eq=False)
class AtiLangChainCallbackHandler(BaseCallbackHandler):
    tracer: AtiTracer
    config: AtiConfig
    agent_id: str = "langchain_agent"

    # Explicitly define BaseCallbackHandler attributes to ensure they exist
    # even if inheritance fails or imports are wonky.
    ignore_chain: bool = False
    ignore_llm: bool = False
    ignore_agent: bool = False
    ignore_retriever: bool = False
    ignore_chat_model: bool = False
    raise_error: bool = False

    _llm_span: Optional[Span] = None
    _tool_span: Optional[Span] = None
    _chain_span: Optional[Span] = None

    def __post_init__(self) -> None:
        # Try to initialize base if possible, but we have defaults now.
        try:
            super().__init__()
        except Exception:
            pass

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:
        self._chain_span = self.tracer.start_span(
            "langchain.chain.run",
            AtiSpanType.STEP,
            agent_id=self.agent_id,
            step_type="executor",
            attributes={ATI_ATTR.step_name: serialized.get("name") if isinstance(serialized, dict) else None},
        )

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        if self._chain_span:
            self._chain_span.end()
            self._chain_span = None

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        if self._chain_span:
            self._chain_span.record_exception(error)
            self._chain_span.end()
            self._chain_span = None

    def on_llm_start(self, serialized: Dict[str, Any], prompts: Any, **kwargs: Any) -> None:
        self._llm_span = self.tracer.start_span(
            "langchain.llm.call",
            AtiSpanType.LLM,
            agent_id=self.agent_id,
            step_type="llm",
            attributes={
                ATI_ATTR.llm_model: (serialized or {}).get("name") if isinstance(serialized, dict) else None,
                ATI_ATTR.payload_enabled: bool(self.config.capture_prompts),
            },
        )
        if self._llm_span and self.config.emit_events and self.config.capture_prompts:
            self.tracer.add_payload_event(
                self._llm_span,
                kind="prompt",
                content=str(prompts),
                redaction_patterns=self.config.redaction_patterns if self.config.redaction_enabled else (),
                enabled=True,
            )

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        if not self._llm_span:
            return
        # Best-effort token usage extraction (varies by provider/package)
        try:
            llm_output = getattr(response, "llm_output", None) or {}
            token_usage = llm_output.get("token_usage") or llm_output.get("usage") or {}
            if isinstance(token_usage, dict):
                self._llm_span.set_attribute(ATI_ATTR.tokens_in, token_usage.get("prompt_tokens"))
                self._llm_span.set_attribute(ATI_ATTR.tokens_out, token_usage.get("completion_tokens"))
        except Exception:
            pass
        self._llm_span.end()
        self._llm_span = None

    def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
        if self._llm_span:
            self._llm_span.record_exception(error)
            self._llm_span.end()
            self._llm_span = None

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        name = serialized.get("name") if isinstance(serialized, dict) else None
        self._tool_span = self.tracer.start_span(
            "langchain.tool.call",
            AtiSpanType.TOOL,
            agent_id=self.agent_id,
            step_type="tool",
            attributes={
                ATI_ATTR.tool_name: name,
                ATI_ATTR.payload_enabled: bool(self.config.capture_payloads),
            },
        )
        if self._tool_span and self.config.emit_events and self.config.capture_payloads:
            self.tracer.add_payload_event(
                self._tool_span,
                kind="tool_args",
                content=input_str,
                redaction_patterns=self.config.redaction_patterns if self.config.redaction_enabled else (),
                enabled=True,
            )

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        if self._tool_span:
            if self.config.emit_events and self.config.capture_payloads:
                self.tracer.add_payload_event(
                    self._tool_span,
                    kind="tool_output",
                    content=output,
                    redaction_patterns=self.config.redaction_patterns if self.config.redaction_enabled else (),
                    enabled=True,
                )
            self._tool_span.end()
            self._tool_span = None

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        if self._tool_span:
            self._tool_span.record_exception(error)
            self._tool_span.end()
            self._tool_span = None

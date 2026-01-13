from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from ati_sdk import AtiConfig, AtiTracer
from .callbacks import AtiLangChainCallbackHandler


@dataclass
class LangChainInstrumentor:
    _enabled: bool = False
    _handler: Optional[AtiLangChainCallbackHandler] = None

    def instrument(self, config: AtiConfig | None = None, *, agent_id: str = "langchain_agent") -> AtiLangChainCallbackHandler:
        if self._enabled and self._handler:
            return self._handler
        cfg = AtiConfig.from_env().merged(config)
        tracer = AtiTracer(framework="langchain", tracer_name="ati.langchain", config=cfg)
        self._handler = AtiLangChainCallbackHandler(tracer=tracer, config=cfg, agent_id=agent_id)
        self._enabled = True
        return self._handler

    def uninstrument(self) -> None:
        self._enabled = False
        self._handler = None

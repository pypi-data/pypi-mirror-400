from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping
import re

from opentelemetry import trace
from opentelemetry.trace import Tracer, Span

from .config import AtiConfig
from .semantics import ATI_SCHEMA_VERSION, ATI_ATTR

def redact_text(text: str, patterns: tuple[re.Pattern[str], ...]) -> str:
    redacted = text
    for p in patterns:
        redacted = p.sub("[REDACTED]", redacted)
    return redacted

@dataclass
class AtiTracer:
    framework: str
    tracer_name: str = "ati"
    tracer: Tracer | None = None
    config: AtiConfig | None = None

    def __post_init__(self) -> None:
        if self.tracer is None:
            self.tracer = trace.get_tracer(self.tracer_name)

    def start_span(
        self,
        name: str,
        span_type: str,
        *,
        agent_id: str | None = None,
        agent_name: str | None = None,
        agent_role: str | None = None,
        step_type: str | None = None,
        step_id: str | None = None,
        attributes: Mapping[str, Any] | None = None,
    ) -> Span:
        attrs: dict[str, Any] = {
            ATI_ATTR.schema_version: ATI_SCHEMA_VERSION,
            ATI_ATTR.framework: self.framework,
            ATI_ATTR.span_type: span_type,
        }
        if agent_id:
            attrs[ATI_ATTR.agent_id] = agent_id
        if agent_name:
            attrs[ATI_ATTR.agent_name] = agent_name
        if agent_role:
            attrs[ATI_ATTR.agent_role] = agent_role
        if step_type:
            attrs[ATI_ATTR.step_type] = step_type
        if step_id:
            attrs[ATI_ATTR.step_id] = step_id
        if attributes:
            for k, v in attributes.items():
                if v is not None:
                    attrs[k] = v
        return self.tracer.start_span(name, attributes=attrs)

    def add_payload_event(
        self,
        span: Span,
        *,
        kind: str,
        content: str,
        redaction_patterns: tuple[re.Pattern[str], ...],
        enabled: bool,
    ) -> None:
        if not enabled:
            return
        payload = content
        redacted = False
        if redaction_patterns:
            payload2 = redact_text(payload, redaction_patterns)
            redacted = payload2 != payload
            payload = payload2
        span.add_event("ati.payload", {"kind": kind, "redacted": redacted, "content": payload})

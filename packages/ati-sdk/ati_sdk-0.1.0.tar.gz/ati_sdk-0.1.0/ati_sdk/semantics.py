from __future__ import annotations

from dataclasses import dataclass

ATI_SCHEMA_VERSION = "0.1"

class AtiSpanType:
    AGENT = "agent"
    STEP = "step"
    TOOL = "tool"
    LLM = "llm"
    IO = "io"
    ORCHESTRATION = "orchestration"

@dataclass(frozen=True)
class _Attr:
    schema_version: str = "ati.trace.schema_version"
    framework: str = "ati.framework"
    span_type: str = "ati.span.type"

    agent_id: str = "ati.agent.id"
    agent_name: str = "ati.agent.name"
    agent_role: str = "ati.agent.role"

    step_id: str = "ati.step.id"
    step_name: str = "ati.step.name"
    step_type: str = "ati.step.type"
    parent_step_id: str = "ati.parent_step.id"
    loop_iteration: str = "ati.loop.iteration"

    tool_name: str = "ati.tool.name"
    llm_model: str = "ati.llm.model"
    tokens_in: str = "ati.tokens.in"
    tokens_out: str = "ati.tokens.out"

    fanout_size: str = "ati.fanout.size"
    retry_count: str = "ati.retry.count"

    payload_enabled: str = "ati.payload.enabled"

ATI_ATTR = _Attr()

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Pattern

def _env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}

def _env_str(name: str, default: str | None = None) -> str | None:
    v = os.getenv(name)
    return v if v is not None else default

@dataclass(frozen=True)
class AtiConfig:
    service_name: str | None = None
    capture_payloads: bool = False
    capture_prompts: bool = False
    redaction_enabled: bool = True
    redaction_patterns: tuple[Pattern[str], ...] = ()
    emit_events: bool = True

    @staticmethod
    def from_env() -> "AtiConfig":
        patterns_raw = os.getenv("ATI_REDACTION_PATTERNS", "")
        patterns: list[Pattern[str]] = []
        if patterns_raw.strip():
            for part in patterns_raw.split(","):
                part = part.strip()
                if part:
                    patterns.append(re.compile(part))
        return AtiConfig(
            service_name=_env_str("OTEL_SERVICE_NAME") or _env_str("SERVICE_NAME"),
            capture_payloads=_env_bool("ATI_CAPTURE_PAYLOADS", False),
            capture_prompts=_env_bool("ATI_CAPTURE_PROMPTS", False),
            redaction_enabled=_env_bool("ATI_REDACTION_ENABLED", True),
            redaction_patterns=tuple(patterns),
            emit_events=_env_bool("ATI_EMIT_EVENTS", True),
        )

    def merged(self, override: "AtiConfig | None") -> "AtiConfig":
        if override is None:
            return self
        return AtiConfig(
            service_name=override.service_name or self.service_name,
            capture_payloads=override.capture_payloads if override.capture_payloads != self.capture_payloads else self.capture_payloads,
            capture_prompts=override.capture_prompts if override.capture_prompts != self.capture_prompts else self.capture_prompts,
            redaction_enabled=override.redaction_enabled if override.redaction_enabled != self.redaction_enabled else self.redaction_enabled,
            redaction_patterns=override.redaction_patterns or self.redaction_patterns,
            emit_events=override.emit_events if override.emit_events != self.emit_events else self.emit_events,
        )

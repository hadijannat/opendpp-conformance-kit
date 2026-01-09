from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, List

from pydantic import BaseModel, Field


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Finding(BaseModel):
    rule_id: str
    severity: Severity
    message: str
    evidence: dict[str, Any] | None = None


class ConformanceReport(BaseModel):
    target: str
    profile_id: str
    profile_version: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    artifacts: List[str] = Field(default_factory=list)
    findings: List[Finding] = Field(default_factory=list)
    passed: bool | None = None

    def add_finding(
        self,
        rule_id: str,
        severity: Severity,
        message: str,
        evidence: dict[str, Any] | None = None,
    ) -> None:
        self.findings.append(
            Finding(rule_id=rule_id, severity=severity, message=message, evidence=evidence)
        )

    def finalize(self) -> None:
        self.passed = all(f.severity != Severity.ERROR for f in self.findings)

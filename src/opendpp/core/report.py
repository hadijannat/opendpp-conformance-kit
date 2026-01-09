from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, List, Optional

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


class ArtifactRecord(BaseModel):
    uri: str
    sha256: str
    content_type: Optional[str]
    artifact_type: str
    size: int
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConformanceReport(BaseModel):
    target: str
    profile_id: str
    profile_version: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    artifacts: List[ArtifactRecord] = Field(default_factory=list)
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

    def add_artifact(
        self,
        *,
        uri: str,
        sha256: str,
        content_type: Optional[str],
        artifact_type: str,
        size: int,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.artifacts.append(
            ArtifactRecord(
                uri=uri,
                sha256=sha256,
                content_type=content_type,
                artifact_type=artifact_type,
                size=size,
                metadata=metadata or {},
            )
        )

    def finalize(self) -> None:
        self.passed = all(f.severity != Severity.ERROR for f in self.findings)

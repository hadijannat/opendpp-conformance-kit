from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class Finding(BaseModel):
    rule_id: str
    severity: Severity
    message: str
    location: Optional[str] = None # JSON pointer, line number, or path
    evidence_links: List[str] = Field(default_factory=list) # links to artifact hashes
    fix_suggestion: Optional[str] = None

class ReportArtifact(BaseModel):
    uri: str
    hash_sha256: str
    mime_type: str
    local_path: str

class ConformanceReport(BaseModel):
    target: str
    profile_id: str
    profile_version: str
    timestamp: datetime = Field(default_factory=datetime.now)
    findings: List[Finding] = Field(default_factory=list)
    artifacts: List[ReportArtifact] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    passed: bool = False

    def add_finding(self, finding: Finding) -> None:
        self.findings.append(finding)
        if finding.severity in [Severity.ERROR, Severity.CRITICAL]:
            self.passed = False

    def finalize(self) -> None:
        error_count = sum(1 for f in self.findings if f.severity in [Severity.ERROR, Severity.CRITICAL])
        self.summary = {
            "total_findings": len(self.findings),
            "errors": error_count,
            "warnings": sum(1 for f in self.findings if f.severity == Severity.WARNING),
            "info": sum(1 for f in self.findings if f.severity == Severity.INFO),
        }
        self.passed = error_count == 0

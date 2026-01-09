from typing import Any

import yaml

from opendpp.core.artifact import Artifact
from opendpp.core.report import ConformanceReport, Severity


class PolicyEngine:
    def __init__(self, rules_path: str) -> None:
        with open(rules_path, "r") as f:
            self.rules: list[dict[str, Any]] = yaml.safe_load(f).get("rules", [])

    def run_checks(
        self, artifacts: list[Artifact], report: ConformanceReport
    ) -> None:
        """Runs custom policy checks based on the profile's rules."""
        for rule in self.rules:
            self._evaluate_rule(rule, artifacts, report)

    def _evaluate_rule(
        self,
        rule: dict[str, Any],
        artifacts: list[Artifact],
        report: ConformanceReport,
    ) -> None:
        """Evaluate a single policy rule against artifacts."""
        rule_id = rule.get("id", "UNKNOWN")
        severity_str = rule.get("severity", "warning")
        severity = Severity(severity_str)
        message = rule.get("message", "Policy check")

        # Placeholder: currently just logs the rule as INFO
        # Full implementation would use JSONPath/SPARQL selectors and assertions
        report.add_finding(
            rule_id=rule_id,
            severity=severity,
            message=message,
            evidence={"rule": rule_id, "artifacts_count": len(artifacts)},
        )

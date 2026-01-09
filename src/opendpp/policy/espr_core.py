import json
import re
from typing import Any, Dict, List

import yaml
from jsonpath_ng import parse as jsonpath_parse

from opendpp.core.artifact import Artifact, ArtifactType
from opendpp.core.report import ConformanceReport, Severity


class PolicyEngine:
    def __init__(self, rules_path: str):
        with open(rules_path, "r", encoding="utf-8") as f:
            self.rules = yaml.safe_load(f).get("rules", [])

    def run_checks(self, artifacts: List[Artifact], report: ConformanceReport) -> None:
        """Runs policy checks based on the profile's rules."""
        for rule in self.rules:
            self._evaluate_rule(rule, artifacts, report)

    def _evaluate_rule(
        self, rule: Dict[str, Any], artifacts: List[Artifact], report: ConformanceReport
    ) -> None:
        rule_id = rule.get("id", "ESPR-RULE")
        severity = Severity(rule.get("severity", "warning"))
        selector = rule.get("selector")
        assertion = rule.get("assertion", "exists")
        message = rule.get("message", "Policy rule failed")

        if not selector:
            report.add_finding(
                rule_id=rule_id,
                severity=severity,
                message="Policy rule missing selector; skipped",
                evidence={"rule": rule},
            )
            return

        target = next(
            (a for a in artifacts if a.artifact_type == ArtifactType.DPP_PAYLOAD),
            None,
        )
        if not target:
            report.add_finding(
                rule_id=rule_id,
                severity=Severity.ERROR,
                message="No DPP payload available for policy evaluation",
                evidence={"rule": rule},
            )
            return

        try:
            data = json.loads(target.raw_bytes)
            expr = jsonpath_parse(selector)
            matches = [m.value for m in expr.find(data)]
        except Exception as exc:
            report.add_finding(
                rule_id=rule_id,
                severity=Severity.ERROR,
                message=f"Policy rule evaluation error: {str(exc)}",
                evidence={"selector": selector, "artifact_hash": target.sha256},
            )
            return

        passed = False
        if assertion == "exists":
            passed = len(matches) > 0
        elif assertion.startswith("equals:"):
            expected = assertion.split("equals:", 1)[1]
            passed = any(str(m) == expected for m in matches)
        elif assertion.startswith("regex:"):
            pattern = assertion.split("regex:", 1)[1]
            passed = any(re.search(pattern, str(m)) for m in matches)

        if not passed:
            report.add_finding(
                rule_id=rule_id,
                severity=severity,
                message=message,
                evidence={
                    "selector": selector,
                    "assertion": assertion,
                    "artifact_hash": target.sha256,
                    "matches": matches,
                },
            )

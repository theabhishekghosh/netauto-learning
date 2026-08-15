from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Severity(Enum):
    HIGH   = "HIGH"
    MEDIUM = "MEDIUM"
    LOW    = "LOW"
    INFO   = "INFO"


class CheckStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"


@dataclass
class Finding:
    device:   str
    check:    str
    severity: Severity
    message:  str
    detail:   str = ""


@dataclass
class CheckResult:
    check_name:      str
    status:          CheckStatus
    findings:        list[Finding] = field(default_factory=list)
    devices_checked: int = 0


@dataclass
class AuditReport:
    network_name:  str
    generated_at:  str = field(default_factory=lambda: datetime.now().isoformat())
    check_results: list[CheckResult] = field(default_factory=list)

    def all_findings(self) -> list[Finding]:
        return [
            finding
            for result in self.check_results # iterate over report.check_results in audit_runner.py 
            for finding in result.findings
        ]

    def findings_by_severity(self, severity: Severity) -> list[Finding]:
        return [f for f in self.all_findings() if f.severity == severity]

    def summary(self) -> dict:
        findings = self.all_findings()
        return {
            "total_findings": len(findings),
            "high":   len([f for f in findings if f.severity == Severity.HIGH]),
            "medium": len([f for f in findings if f.severity == Severity.MEDIUM]),
            "low":    len([f for f in findings if f.severity == Severity.LOW]),
            "info":   len([f for f in findings if f.severity == Severity.INFO]),
        }

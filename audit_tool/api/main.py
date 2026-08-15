# audit_tool/api/main.py
import sys
import logging
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from audit_tool.audit_runner import run_audit
from audit_tool.checks.models import AuditReport, Severity
from audit_tool.audit_runner import run_audit, commit_findings
from audit_tool.reports.markdown_report import save_markdown
from audit_tool.audit_runner import run_audit, run_audit_online, commit_findings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    stream=sys.stdout
)

app = FastAPI(title="Network Config Audit API")

API_KEY = "audit-secret-2026"
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

# store last report in memory — simple cache
_last_report: AuditReport | None = None


def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key


class AuditRequest(BaseModel):
    inventory_path: str = "audit_tool/inputs/device_inventory.yaml"
    snapshot_dir: str = "audit_tool/inputs/snapshots"

class OnlineAuditRequest(BaseModel):
    inventory_path: str = "audit_tool/inputs/device_inventory.yaml"
    user: str = "labroot"
    password: str = "lab123"

@app.get("/")
def root():
    return {"status": "ok", "message": "Network Config Audit API"}


@app.post("/audit/offline", dependencies=[Depends(verify_api_key)])
def run_offline_audit(request: AuditRequest):
    """
    Trigger an offline audit against config file snapshots.
    Returns full findings as JSON.
    """
    global _last_report
    try:
        report = run_audit(
            inventory_path=request.inventory_path,
            snapshot_dir=request.snapshot_dir
        )
        _last_report = report

        # convert to JSON-serializable format
        return {
            "network_name": report.network_name,
            "generated_at": report.generated_at,
            "summary": report.summary(),
            "findings": [
                {
                    "device": f.device,
                    "check": f.check,
                    "severity": f.severity.value,
                    "message": f.message,
                    "detail": f.detail
                }
                for f in report.all_findings()
            ]
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit failed: {e}")


@app.get("/audit/summary", dependencies=[Depends(verify_api_key)])
def get_audit_summary():
    """Return summary of the last audit run."""
    if not _last_report:
        raise HTTPException(
            status_code=404,
            detail="No audit has been run yet. POST to /audit/offline first."
        )
    return {
        "network_name": _last_report.network_name,
        "generated_at": _last_report.generated_at,
        "summary": _last_report.summary()
    }


@app.get("/audit/findings/{severity}", dependencies=[Depends(verify_api_key)])
def get_findings_by_severity(severity: str):
    """Return findings filtered by severity — HIGH, MEDIUM, LOW, INFO."""
    if not _last_report:
        raise HTTPException(
            status_code=404,
            detail="No audit has been run yet."
        )
    try:
        severity_enum = Severity(severity.upper())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid severity: {severity}. Use HIGH, MEDIUM, LOW, or INFO."
        )

    findings = _last_report.findings_by_severity(severity_enum)
    return {
        "severity": severity.upper(),
        "count": len(findings),
        "findings": [
            {
                "device": f.device,
                "check": f.check,
                "message": f.message,
                "detail": f.detail
            }
            for f in findings
        ]
    }
@app.post("/audit/offline", dependencies=[Depends(verify_api_key)])
def run_offline_audit(request: AuditRequest):
    global _last_report
    try:
        report = run_audit(
            inventory_path=request.inventory_path,
            snapshot_dir=request.snapshot_dir
        )
        _last_report = report

        # save and commit findings
        save_markdown(report, "audit_report.md")
        committed = commit_findings("audit_report.md", report.network_name)

        return {
            "network_name": report.network_name,
            "generated_at": report.generated_at,
            "committed_to_git": committed,
            "summary": report.summary(),
            "findings": [
                {
                    "device": f.device,
                    "check": f.check,
                    "severity": f.severity.value,
                    "message": f.message,
                    "detail": f.detail
                }
                for f in report.all_findings()
            ]
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit failed: {e}")

@app.post("/audit/online", dependencies=[Depends(verify_api_key)])
def run_online_audit(request: OnlineAuditRequest):
    """
    Trigger a live audit against real devices via PyEZ.
    Requires network access to management IPs.
    """
    global _last_report
    try:
        report = run_audit_online(
            inventory_path=request.inventory_path,
            user=request.user,
            password=request.password
        )
        _last_report = report
        save_markdown(report, "audit_report_online.md")
        committed = commit_findings("audit_report_online.md", report.network_name)

        return {
            "network_name": report.network_name,
            "generated_at": report.generated_at,
            "mode": "online",
            "committed_to_git": committed,
            "summary": report.summary(),
            "findings": [
                {
                    "device": f.device,
                    "check": f.check,
                    "severity": f.severity.value,
                    "message": f.message,
                    "detail": f.detail
                }
                for f in report.all_findings()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Online audit failed: {e}")
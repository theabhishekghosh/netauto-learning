from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
from week1_day6 import NetworkDevice
from week4_day19 import poll_one_device
from jnpr.junos.exception import ConnectError
from jnpr.junos.utils.config import ConfigLoadError, CommitError
import logging
logging.getLogger("paramiko").setLevel(logging.CRITICAL)
logging.getLogger("paramiko.transport").setLevel(logging.CRITICAL)

API_KEY = "netauto-secret-2026"
API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    """Verify the API key from request header."""
    if api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )
    return api_key

app = FastAPI(title="Network Automation API")

USER = "labroot"
PASSWORD = "lab123"

DEVICES = [
    NetworkDevice("10.207.194.11",  "PE", USER, PASSWORD),
    NetworkDevice("10.207.194.94", "PE", USER, PASSWORD),
    NetworkDevice("10.207.195.43", "PE", USER, PASSWORD),
    NetworkDevice("10.207.194.92",  "P",  USER, PASSWORD),
    NetworkDevice("10.207.205.22",  "PE", USER, PASSWORD),
    NetworkDevice("10.207.207.208", "PE", USER, PASSWORD),
    NetworkDevice("10.207.210.187", "PE", USER, PASSWORD),
    NetworkDevice("10.207.213.128",  "CE", USER, PASSWORD),
    NetworkDevice("10.207.208.59", "CE", USER, PASSWORD),
    NetworkDevice("10.207.206.34",   "CE", USER, PASSWORD),
    NetworkDevice("10.207.216.116",  "CE", USER, PASSWORD),
]


class DeployRequest(BaseModel):
    host: str
    role: str = "PE"
    config: str
    confirm_minutes: int = 1


@app.get("/")
def root():
    return {"status": "ok", "message": "Network Automation API"}


@app.get("/inventory", dependencies=[Depends(verify_api_key)])
def get_inventory():
    """Get facts from all devices concurrently."""
    with ThreadPoolExecutor(max_workers=11) as executor:
        results = list(executor.map(poll_one_device, DEVICES))
    return results


@app.get("/device/{host}/facts", dependencies=[Depends(verify_api_key)])
def get_device_facts(host: str):
    """Get facts for a specific device by IP."""
    try:
        with NetworkDevice(host, "PE", USER, PASSWORD) as device:
            return device.get_summary()
    except ConnectError as e:
        raise HTTPException(status_code=503, detail=f"Device unreachable: {e}")


@app.get("/device/{host}/interfaces", dependencies=[Depends(verify_api_key)])
def get_device_interfaces(host: str):
    """Get interface status for a specific device."""
    try:
        with NetworkDevice(host, "PE", USER, PASSWORD) as device:
            return device.get_interfaces()
    except ConnectError as e:
        raise HTTPException(status_code=503, detail=f"Device unreachable: {e}")


@app.get("/device/{host}/bgp", dependencies=[Depends(verify_api_key)])
def get_device_bgp(host: str):
    """Get BGP neighbor status for a specific device."""
    try:
        with NetworkDevice(host, "PE", USER, PASSWORD) as device:
            return device.get_bgp_neighbors()
    except ConnectError as e:
        raise HTTPException(status_code=503, detail=f"Device unreachable: {e}")


@app.post("/deploy", dependencies=[Depends(verify_api_key)])
def deploy_config(request: DeployRequest):
    """
    Deploy config to a device using commit confirmed.
    POST body: {"host": "10.207.194.11", "config": "set interfaces...", "confirm_minutes": 1}
    """
    try:
        with NetworkDevice(request.host, request.role, USER, PASSWORD) as device:
            diff = device.deploy_dry_run(request.config)
            if not diff:
                return {"status": "no_changes", "host": request.host}
            return {"status": "success", "host": request.host, "diff": diff}
    except ConnectError as e:
        raise HTTPException(status_code=503, detail=f"Device unreachable: {e}")
    except (ConfigLoadError, CommitError) as e:
        raise HTTPException(status_code=400, detail=f"Config validation failed: {e}")
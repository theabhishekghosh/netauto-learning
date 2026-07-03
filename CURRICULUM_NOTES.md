# Network Automation Learning Journal
**Author:** Abhishek Ghosh  
**Started:** June 2026  
**Repo:** github.com/theabhishekghosh/netauto-learning

---

## Background

Senior Technology Consultant, Juniper Networks PS, Bengaluru.  
Triple JNCIE (SP, DC, ENT), 16+ years SP/DC/ENT networking experience.  
Goal: Build production-grade Python network automation skills 
---

## Lab Environment

**Platform:** 11x MX240, Junos 24.4R2-S3.2  

| Device | Role | Management IP |
|--------|------|--------------|
| PE1_RE | PE | 10.49.0.137 |
| PE2_RE | PE | 10.49.16.181 |
| PE3_RE | PE | 10.49.16.140 |
| P4_RE  | P  | 10.49.16.84 |
| PE5_RE | PE | 10.49.25.94 |
| PE6_RE | PE | 10.49.15.198 |
| PE7_RE | PE | 10.49.15.126 |
| CE1_RE | CE | 10.49.16.48 |
| CE2_RE | CE | 10.49.15.128 |
| CE3_RE | CE | 10.49.0.99 |
| CE4_RE | CE | 10.49.0.197 |

**Mac setup:** Python 3.11.15 in venv at ~/netauto-learning/venv  
**Editor:** VS Code with Pylance

---

## Curriculum Progress

### Week 1 — Python Fundamentals + PyEZ Basics ✅

**Key concepts learned:**
- Type hints, Google-style docstrings, single responsibility functions
- Input validation — `strip().lower()`, `raise ValueError`, `try/except`
- Lists, dicts, list comprehensions, `.get()` for safe dict access
- Functions calling functions — DRY principle
- PyEZ — `Device`, `dev.open()`, `dev.facts`, context manager (`with`)
- Classes — `__init__`, `self`, attributes vs methods
- Modules and imports — `from week1_day6 import NetworkDevice`

**Key files:**
- `week1.py` — function fundamentals
- `week1_day3.py` — list/dict operations
- `week1_day4.py` — function composition
- `week1_day5.py` — PyEZ basics, first device connection
- `week1_day6.py` — **NetworkDevice class (core abstraction)**
- `week1_day7.py` — multi-device inventory (11 devices)

**Real finding:** P4_RE confirmed as Route Reflector with 6 PE clients, all iBGP AS65001

---

### Week 2 — Operational Data ✅

**Key concepts learned:**
- `EthPortTable` — interface operational data via PyEZ tables
- Direct RPC calls — `dev.rpc.get_bgp_summary_information()` when tables fall short
- XML navigation — `result.findall(".//tag")`, `.find("tag")`, `.text`
- `bgpTable` (lowercase) — correct module name, not `BgpTable`
- Multi-device health check — facts + interfaces + BGP across all 11 devices

**Key files:**
- `week2_day8.py` — interface tables, admin-up/oper-down detection
- `week2_day9.py` — BGP neighbor status via raw RPC
- `week2_day10.py` — full 11-device health check report

**Real finding:** 18 interfaces admin-up/oper-down on PE1 (expected in virtual lab)

---

### Week 3 — CI/CD Pipeline ✅

**Key concepts learned:**
- Jinja2 templating — `Template("set interfaces {{ interface }}...")`, `.render()`
- YAML source of truth — `yaml.safe_load()`, separating data from code
- PyEZ config utility — `Config(dev)`, `cu.load()`, `cu.diff()`, `cu.commit_check()`, `cu.rollback()`
- Git workflow — `git init`, `git add`, `git commit`, `git revert`, `git push`
- SSH keys for GitHub — `ssh-keygen -t ed25519`, `ssh-add`
- Batfish — offline fleet-wide config analysis via Docker
- `commit confirmed` — `cu.commit(confirm=N)`, `cu.commit()` to confirm
- Pre-flight conflict detection — `get_interface_addresses()` before deploying

**Key files:**
- `week3_day11.py` — Jinja2 templating
- `week3_day12.py` — YAML source of truth
- `week3_day13.py` / `week3_day13.2.py` — dry-run config push
- `week3_day15.py` — Batfish fleet analysis
- `week3_day16_CI_CD_verify.py` — **5-stage validation pipeline** (Lint→Build→Pre-flight→Test→Deploy dry-run→Verify)
- `week3_day16_CI_CD_deploy.py` — **commit confirmed deployment pipeline**

**NetworkDevice class additions:**
- `__enter__` / `__exit__` — context manager support
- `deploy_dry_run()` — load/diff/commit_check/rollback, never commits
- `deploy_confirmed()` — real commit with auto-revert safety net
- `confirm_commit()` — confirms pending commit confirmed
- `get_interface_addresses()` — pre-flight conflict detection

**Real findings:**
- Batfish caught PE5_RE missing BGP export policy (NHS) — confirmed real gap on device
- Deployed to real device, confirmed permanently, had to manually clean up — drove addition of pre-flight check
- Pre-flight check correctly blocked pipeline re-run after fix

---

### Week 4 — Concurrency ✅

**Key concepts learned:**
- `ThreadPoolExecutor` — concurrent execution of I/O-bound operations
- `executor.map(func, iterable)` — one arg per call, returns lazy iterator
- `list(executor.map(...))` — forces materialization, raises thread exceptions
- Tuple packing/unpacking — compressing multiple args for `executor.map()`
- `@dataclass` — auto-generates `__init__` from type-annotated attributes
- `str | None` — union types, `= None` default values
- Two separate `try` blocks — different failure modes, different consequences
- `raise` (bare) — re-raises caught exception preserving original traceback
- Reading tracebacks — bottom to top, find YOUR filenames first
- `stdout` vs `stderr` — intentional output vs library noise, `2>/dev/null`

**Key files:**
- `week4_day19.py` — concurrent inventory polling (85s → 9.5s, 9x speedup)
- `week4_day21.py` — concurrent bulk deployment with DeployResult

**Performance baseline:**
- Sequential (11 devices): 85.07 seconds
- Concurrent (11 devices): 9.48 seconds
- Concurrent bulk deploy (3 devices): 14.63 seconds

**NetworkDevice class additions:**
- `raise` added to `connect()` — re-raises ConnectError to caller

---

### Week 5 — REST APIs ✅

**Key concepts learned:**
- `requests.get()` / `requests.post()` — HTTP client
- `response.status_code`, `response.headers`, `response.json()`
- `response.raise_for_status()` — raises HTTPError if status >= 400
- `response.ok` — True for 2xx, False otherwise
- FastAPI — `app = FastAPI()`, `@app.get()`, `@app.post()`
- Handler functions — registered via decorators, run on matching requests
- Path parameters — `@app.get("/device/{host}/facts")`
- `BaseModel` from pydantic — validates POST request body
- `HTTPException` — correct REST API error responses
- `APIKeyHeader` + `Depends()` — dependency injection for auth
- stdout vs stderr — `2>/dev/null` to suppress library noise

**Key files:**
- `week5_day22.py` — requests library, consuming external API
- `week5_day23.py` — **FastAPI server** (inventory, device, deploy endpoints)
- `week5_day24_client.py` — Python client calling your own API

**API endpoints built:**
```
GET  /                              → health check (public)
GET  /inventory              🔒     → all 11 devices, concurrent
GET  /device/{host}/facts    🔒     → any device facts
GET  /device/{host}/interfaces 🔒   → any device interfaces
GET  /device/{host}/bgp      🔒     → any device BGP
POST /deploy                 🔒     → dry-run deployment
```

---

## Current NetworkDevice Class (week1_day6.py)

```python
class NetworkDevice:
    # Attributes set in __init__:
    # self.host, self.role, self.user, self.password, self.facts, self.dev

    # Context manager
    __enter__()          # calls connect()
    __exit__()           # calls disconnect()

    # Connection
    connect()            # opens NETCONF, populates self.facts
    disconnect()         # closes NETCONF

    # Read operations
    get_summary()        # hostname, role, model, version, uptime
    get_interfaces()     # list of {name, oper, admin} dicts
    get_bgp_neighbors()  # list of {peer, state} dicts via raw RPC
    get_interface_addresses(interface_name)  # list of configured IPs

    # Write operations
    deploy_dry_run(config_text)                        # always rollback
    deploy_confirmed(config_text, confirm_minutes=1)   # real commit, auto-revert
    confirm_commit()                                   # confirms pending commit
```

---

## Capstone Plan — Network Config Audit Tool (Weeks 9-10)

**Motivation:** Optus CPC audit (PID51156) — 62-node BGP-LU seamless MPLS core, 13-year-old HLD/LLD inadequate as intent baseline, no live device access.

**What it does:**
```
Input:  Config files (from RANCID/Oxidized) + optional live device access
Output: JSON (API) + Markdown report + Git-committed findings
```

**Audit checks:**
- Batfish fleet-wide: BGP policy consistency, undefined references, unused structures
- Golden config compliance: compare each device against a template
- EOS/EOL flagging: identify devices past end of support
- Operational state (if live access): BGP neighbors, interface status, version consistency

**Structure:**
```
audit_tool/
├── parsers/
│   ├── batfish_checks.py
│   └── config_parser.py
├── collectors/
│   └── live_state.py
├── checks/
│   ├── bgp_consistency.py
│   ├── eos_eol.py
│   └── interface_audit.py
├── reports/
│   ├── markdown_report.py
│   └── json_output.py
└── api/
    └── main.py
```

---

## Remaining Curriculum

| Week | Topic |
|------|-------|
| 6 | Logging — replace print() with logging module, log levels, file handlers |
| 7-8 | pytest — unit testing, mocking device connections |
| 9-10 | **Network Config Audit Tool (capstone)** |
| 11-12 | Buffer / Arista AVD+pyavd |

---

## Key Lessons Learned

1. **Type hints don't enforce at runtime** — write your own validation
2. **`if not x` checks truthiness** — empty string/list/dict is falsy
3. **`return` inside a loop exits the function immediately**
4. **Context managers (`with`) guarantee cleanup** — even on exceptions
5. **`self.x` vs local `x`** — class attributes survive across methods, local variables don't
6. **`executor.map()` returns lazy iterator** — `list()` forces materialization
7. **Two `try` blocks for two failure modes** — connection failure ≠ validation failure
8. **Read tracebacks bottom-up** — find your filenames, ignore library internals
9. **Pre-flight checks beat post-deploy verification** — catch before you commit
10. **DRY principle** — if the same logic appears twice, it should be a function
11. **`raise` (bare) vs `raise Exception(...)` ** — re-raise original vs create new
12. **Module vs function vs method** — file vs top-level def vs def inside class

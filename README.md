# Network Automation Learning Curriculum

Python network automation curriculum built against a real 11-device 
Junos lab (MX240s running Junos 24.4R2-S3.2).

## Structure

| Week | Topic |
|------|-------|
| 1-2 | Python fundamentals, OOP, PyEZ basics, operational data |
| 3 | Jinja2, YAML, Git, Batfish, CI/CD pipeline |
| 4 | Concurrency — ThreadPoolExecutor, bulk deployment |
| 5 | REST APIs — FastAPI, authentication |
| 6 | Logging — handlers, rotation |
| 7-8 | pytest — unit testing, mocking |
| 9-10 | Capstone — Network Config Audit Tool |

## Capstone — Network Config Audit Tool

Offline and online network configuration audit tool for PS engineers.

### Features
- Offline audit against config file snapshots (no device access needed)
- Online audit via live PyEZ polling (concurrent, 7 devices)
- BGP export policy consistency check
- CE interface hygiene check
- Markdown report generation
- FastAPI REST interface
- Git-committed findings for audit trail
- 44 pytest tests

### Usage

```bash
# Offline audit
python3 -m audit_tool.audit_runner

# API
uvicorn audit_tool.api.main:app --port 8001
```

### Environment variables

```bash
cp .env.example .env
# edit .env with your credentials
```

## ⚠️ Note on credentials

Weekly exercise scripts (week1_*.py through week6_*.py) contain 
hardcoded lab credentials for a private learning environment.
Replace with environment variables before use in production.
The audit tool (audit_tool/) uses environment variables via config.py.

## Lab topology

7-device BGP-LU Seamless MPLS lab:
- PE1-PE3, PE5-PE7 — Provider Edge routers
- P4 — Provider core / Route Reflector
- CE1-CE4 — Customer Edge routers

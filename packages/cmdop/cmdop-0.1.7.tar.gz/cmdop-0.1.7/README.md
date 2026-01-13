# cmdop

**Turn any machine into an API endpoint.**

[![PyPI](https://img.shields.io/pypi/v/cmdop)](https://pypi.org/project/cmdop/)
[![Python](https://img.shields.io/pypi/pyversions/cmdop)](https://pypi.org/project/cmdop/)
[![License](https://img.shields.io/pypi/l/cmdop)](https://github.com/cmdop/cmdop-python/blob/main/LICENSE)

```python
from cmdop import CMDOPClient

# Server in another country. Behind NAT. Behind firewall. Don't care.
with CMDOPClient.remote(api_key="cmd_xxx") as server:
    server.terminal.execute("docker restart app")
    server.files.write("/etc/nginx/sites/new.conf", config)
    logs = server.files.read("/var/log/app/error.log")
```

No SSH. No VPN. No open ports. No bullshit.

---

## The Problem

You need to run a command on a remote server. What do you do?

**Option A: SSH**
```
→ Generate keys
→ Copy public key to server
→ Configure sshd
→ Open port 22
→ Hope firewall allows it
→ Pray NAT doesn't break it
→ paramiko/fabric in Python
→ Debug why it doesn't work
```

**Option B: Build an API**
```
→ Write FastAPI endpoints
→ Implement authentication
→ Get SSL certificate
→ Open ports
→ Deploy to every server
→ Maintain all of this
→ Write client code
→ Repeat for each new operation
```

**Option C: CMDOP**
```python
server.terminal.execute("your command")
```

That's it.

---

## How It Works

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Your Code  │ ──── │ Cloud Relay │ ──── │   Agent     │
│   (SDK)     │      │grpc.cmdop.com│     │  (on server)│
└─────────────┘      └─────────────┘      └─────────────┘
                            │
        Outbound only ──────┘
        No open ports
        Works through any NAT/firewall
```

1. Install agent on target machine
2. Agent connects outbound to cloud relay
3. Your code connects to same relay with API key
4. Commands flow through, results come back
5. Zero network configuration required

---

## What Can You Do?

**Terminal — full shell access:**
```python
session = server.terminal.create(shell="/bin/bash")
server.terminal.send_input(session.session_id, "kubectl get pods\n")
output = server.terminal.get_history(session.session_id)
```

**Files — complete filesystem control:**
```python
server.files.list("/home/user")
server.files.read("/etc/nginx/nginx.conf")
server.files.write("/tmp/config.json", b'{"key": "value"}')
server.files.delete("/tmp/garbage", recursive=True)
server.files.copy("/backup/db.sql", "/restore/db.sql")
```

**AI Agents — run LLM agents with type-safe responses:**
```python
from pydantic import BaseModel

class ServerHealth(BaseModel):
    status: str
    cpu_percent: float
    memory_used_gb: float
    disk_free_gb: float
    issues: list[str]

# Run agent, get typed response
result = server.agent.run(
    prompt="Check server health and report issues",
    output_schema=ServerHealth
)
health: ServerHealth = result.output  # Fully typed!
if health.issues:
    alert(health.issues)
```

---

## Real World

### Give AI Agents Hands

```python
from pydantic import BaseModel

class DeployResult(BaseModel):
    success: bool
    version: str
    containers_running: int
    errors: list[str]

# Agent executes commands, parses output, returns structured data
with CMDOPClient.remote(api_key=KEY) as server:
    result = server.agent.run(
        prompt="Deploy myapp:v2.1 and verify all containers are healthy",
        agent_type="terminal",
        output_schema=DeployResult
    )
    if not result.output.success:
        rollback(result.output.errors)
```

### Deploy Without The Circus

```python
# No Ansible. No Terraform. No YAML hell.
def deploy(version: str):
    with CMDOPClient.remote(api_key=PROD_KEY) as prod:
        prod.terminal.execute(f"docker pull myapp:{version}")
        prod.terminal.execute("docker-compose up -d")

        # Verify
        health = prod.files.read("/var/log/myapp/health.log")
        assert b"healthy" in health
```

### Fleet Management

```python
# Update 1000 edge devices
async def update_fleet(device_keys: list[str], new_config: bytes):
    async with asyncio.TaskGroup() as tg:
        for key in device_keys:
            tg.create_task(update_device(key, new_config))

async def update_device(key: str, config: bytes):
    async with AsyncCMDOPClient.remote(api_key=key) as device:
        await device.files.write("/etc/app/config.yml", config)
        await device.terminal.execute("systemctl restart app")
```

### Debug Customer Issues

```python
# Support engineer gets temporary access
def diagnose(customer_key: str):
    with CMDOPClient.remote(api_key=customer_key) as machine:
        # See what's running
        session = machine.terminal.create()
        machine.terminal.send_input(session.session_id, "ps aux\n")

        # Read their logs
        logs = machine.files.read("~/Library/Logs/MyApp/error.log")

        # Check disk space
        machine.terminal.send_input(session.session_id, "df -h\n")
```

---

## Installation

```bash
pip install cmdop
```

## Quick Start

```python
from cmdop import CMDOPClient

# Remote server via cloud relay
with CMDOPClient.remote(api_key="cmd_xxx") as client:
    result = client.files.list("/home")
    print(result.entries)

# Local agent on same machine
with CMDOPClient.local() as client:
    result = client.files.list("/home")
```

## Async

```python
from cmdop import AsyncCMDOPClient

async with AsyncCMDOPClient.remote(api_key="cmd_xxx") as client:
    await client.terminal.execute("echo hello")
    content = await client.files.read("/etc/hostname")
```

---

## API

### Terminal

| Method | What it does |
|--------|--------------|
| `create(shell, cols, rows)` | Start terminal session |
| `send_input(id, data)` | Send commands/keystrokes |
| `get_history(id)` | Get output |
| `resize(id, cols, rows)` | Resize terminal |
| `send_signal(id, signal)` | Send SIGINT/SIGTERM/etc |
| `close(id)` | End session |

### Files

| Method | What it does |
|--------|--------------|
| `list(path)` | List directory |
| `read(path)` | Read file |
| `write(path, content)` | Write file |
| `delete(path)` | Delete file/dir |
| `copy(src, dst)` | Copy |
| `move(src, dst)` | Move/rename |
| `mkdir(path)` | Create directory |
| `info(path)` | Get metadata |

### Agent

| Method | What it does |
|--------|--------------|
| `run(prompt, output_schema=None)` | Run AI agent, optionally with Pydantic model for structured output |

**Supported agent types:** `chat`, `terminal`, `command`, `router`, `planner`

**Structured output with Pydantic:**
```python
class MyResult(BaseModel):
    answer: str
    confidence: float

result = client.agent.run("...", output_schema=MyResult)
typed_data: MyResult = result.output  # Validated against schema
```

---

## Security

- **TLS everywhere** — all traffic encrypted
- **Outbound only** — agent never accepts incoming connections
- **API key scoping** — keys bound to specific agents/teams
- **No credentials on wire** — no SSH keys, no passwords
- **Audit logs** — every action tracked

---

## Requirements

- Python 3.10+
- CMDOP agent running on target machine

## Links

[cmdop.com](https://cmdop.com)

## License

MIT

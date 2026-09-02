# 🔐 SSH Module

A lightweight wrapper around **Paramiko** providing:

- automatic parsing of SSH config files (including `Include`)
- support for `ProxyJump` (jump hosts)
- identity file loading (`IdentityFile`)
- simple `connect → execute → close` workflow
- optional password authentication
- reusable SSH sessions

Ideal for automation, CI/CD workflows, and remote command execution.

---

## ✅ Quick Start

```python
from cscs_tools.ssh.services.ssh_service import SshService

ssh = SshService(
    config_path="~/.ssh/config",
    key_path="~/.ssh/id_rsa",
)

ssh.connect_to_host("my-host")
print(ssh.execute("hostname && whoami"))
ssh.close()
```

---

## 📁 SSH Config Support

`SshService` reads:

- a single SSH config file (e.g. `~/.ssh/config`)
- files included via `Include`
- host aliases
- `ProxyJump` configuration
- `IdentityFile` entries (unless overridden manually)

### Example SSH config

```
Host my-host
    HostName 10.1.2.3
    User ubuntu
    IdentityFile ~/.ssh/id_rsa

Host internal
    HostName 10.2.3.4
    User deploy
    ProxyJump my-host
```

### Usage

```python
ssh = SshService("~/.ssh/config")
ssh.connect_to_host("internal")   # automatically jumps via my-host
print(ssh.execute("uname -a"))
ssh.close()
```

---

## 🚀 Multiple Hosts Example

If you need to connect to multiple hosts, **close between connections**:

```python
from cscs_tools.ssh.services.ssh_service import SshService

ssh = SshService(config_path="~/.ssh/config")

# --- Host 1 ---
ssh.connect_to_host("my-host")
print(ssh.execute("hostname && whoami"))
ssh.close()

# --- Host 2 ---
ssh.connect_to_host("internal")
print(ssh.execute("hostname && whoami"))
ssh.close()
```

**Why close?**

`connect_to_host()` opens a new SSH connection but does **not** close the previous one.  
To avoid leaving unused TCP sessions open, you should always:

- connect  
- execute  
- close  

---

## 🛠 `SshService` Parameters

### Optional arguments (with defaults)

| Parameter      | Type | Default | Description |
|----------------|------|---------|-------------|
| `config_path`  | str  | `~/.ssh/config` | Path to the SSH config file. Supports `~`. |
| `key_path`     | str  | `~/.ssh/id_rsa` | Private key path. Overrides any `IdentityFile`. |
| `password`     | str  | None    | Forces password authentication. |
| `timeout`      | int  | 10–15   | Timeout for connect & command execution. |

---

## 🔌 Connecting

### Direct host

```python
ssh.connect_to_host("server1")
```

### With password auth

```python
ssh = SshService(config_path="~/.ssh/config", password="mypassword")
ssh.connect_to_host("server1")
```

### ProxyJump (jump host)

```python
ssh.connect_to_host("internal-host")  # jump-host handled automatically
```

---

## 🧾 Executing Commands

```python
output = ssh.execute("hostname && whoami")
print(output)
```

If a command outputs *only stderr* (no stdout), `RuntimeError` is raised.

---

## 🔒 Identity Files

- Replaces all `IdentityFile` entries with `key_path`
- Loads the **first** key only
- Raises a clear error if the key requires a passphrase

---

## ✨ Full Example

```python
from cscs_tools.ssh.services.ssh_service import SshService

servers = ["uke2", "sm-producer"]

ssh = SshService("~/.ssh/config")

for host in servers:
    print(f"\n--- Connecting to {host} ---")
    ssh.connect_to_host(host)
    print(ssh.execute("hostname && whoami"))
    ssh.close()
```

---

## 🧪 Samples

See:

```
sample/ssh/ssh_sample.py
```

---

## 📝 Notes

- Relative paths are resolved against the **current working directory**, not script location.
- For consistent behavior, prefer absolute paths or `"~/.ssh/config"`.
- Jump-host and target connections are both closed via `ssh.close()`.

---

## 📄 License

MIT © Csaba Cselko
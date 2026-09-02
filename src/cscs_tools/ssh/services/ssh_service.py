import os
import glob
import shlex
import paramiko
from paramiko.config import SSHConfig


class SshService:
    """
    A lightweight SSH helper built on top of Paramiko with support for
    SSH config parsing, identity file normalization, and ProxyJump
    (jump‑host) connections.

    This service reads an SSH configuration file (and any included
    files), resolves host aliases, loads identity keys, and establishes
    direct or jump‑host SSH connections. It provides a simple
    `execute()` method for running remote commands and returns their
    output.

    Parameters
    ----------
    config_path : str, optional
        Path to the SSH config file (default: "~/.ssh/config").
    key_path : str, optional
        Path to the private key to use for all connections. Overrides
        any IdentityFile entries in the SSH config (default: "~/.ssh/id_rsa").
    password : str, optional
        Password for SSH authentication. Used only if provided; otherwise
        key‑based auth is attempted.

    Attributes
    ----------
    conf : paramiko.config.SSHConfig
        Parsed SSH configuration including included files.
    client : paramiko.SSHClient or None
        Active SSH client for the final destination host.
    jump_client : paramiko.SSHClient or None
        SSH client for the jump host when ProxyJump is used.
    _host_dict : dict
        Mapping of host aliases to their resolved ssh‑config properties.

    Methods
    -------
    connect_to_host(host, timeout=10)
        Open an SSH connection to the given host alias or hostname.
        Supports ProxyJump if defined in SSH config.
    execute(cmd, timeout=10)
        Run a remote command and return its stdout output.
    close()
        Close active SSH and jump‑host connections.
    """

    def __init__(
            self,
            config_path: str | None = "~/.ssh/config",
            key_path: str | None = "~/.ssh/id_rsa",
            password: str | None = None
    ):
        self.config_path = os.path.abspath(os.path.expanduser(config_path))
        self.key_path = os.path.abspath(os.path.expanduser(key_path))
        self.password = password
        self.conf = self._load_ssh_config()
        self._fix_identityfile_paths()
        self._host_dict = self._build_host_dict(self.conf)
        self.client = None
        self.client_jumphost = None
        self.jump_client = None

    def _load_ssh_config(self) -> SSHConfig:
        conf = SSHConfig()

        if os.path.isfile(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
                f.seek(0)
                conf.parse(f)
        else:
            raise FileNotFoundError(f"SSH config not found: {self.config_path}")

        include_patterns = []
        for line in lines:
            line = line.strip()
            if line.lower().startswith("include"):
                parts = shlex.split(line)
                include_patterns.extend(parts[1:])

        base_dir = os.path.dirname(self.config_path)

        for pat in include_patterns:
            pat_path = os.path.join(base_dir, pat)
            for inc in glob.glob(os.path.expanduser(pat_path), recursive=True):
                if os.path.isfile(inc):
                    with open(inc, "r", encoding="utf-8") as f:
                        conf.parse(f)

        return conf

    def _fix_identityfile_paths(self):
        for entry in self.conf._config:
            cfg = entry.get("config", {})
            if "identityfile" in cfg:
                cfg["identityfile"] = [self.key_path]

    def _build_host_dict(self, conf: SSHConfig) -> dict[str, dict]:
        host_dict = {}
        for entry in conf._config:
            hosts = entry.get("host", [])
            cfg = entry.get("config", {})
            for h in hosts:
                if "*" in h or "?" in h:
                    continue
                d = {k.lower(): v for k, v in cfg.items()}
                d.setdefault("hostname", h)
                host_dict[h] = d
        return host_dict

    def _ssh_lookup(self, alias: str) -> dict:
        return self._host_dict.get(alias, {"hostname": alias})

    def _load_first_key(self, identity_files: list[str] | None):
        if not identity_files:
            return None
        key_path = os.path.abspath(os.path.expanduser(identity_files[0]))
        if not os.path.exists(key_path):
            return None
        try:
            return paramiko.RSAKey.from_private_key_file(key_path)
        except paramiko.PasswordRequiredException:
            raise RuntimeError(f"Key requires passphrase: {key_path}")

    def _open_jump_channel(self, jump_alias: str, target_host: str, target_port: int, timeout: int = 15):
        jcfg = self._ssh_lookup(jump_alias)
        jhost = jcfg.get("hostname", jump_alias)
        juser = jcfg.get("user") or "root"
        jport = int(jcfg.get("port", 22))
        jpkey = self._load_first_key(jcfg.get("identityfile"))

        jump_client = paramiko.SSHClient()
        jump_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        jump_client.connect(
            hostname=jhost,
            port=jport,
            username=juser,
            pkey=jpkey,
            look_for_keys=False,
            allow_agent=False,
            timeout=timeout,
            auth_timeout=timeout,
            banner_timeout=timeout,
        )

        transport = jump_client.get_transport()
        chan = transport.open_channel(
            "direct-tcpip",
            (target_host, target_port),
            (jhost, 0),
            timeout=timeout
        )
        return jump_client, chan

    def connect_to_host(self, host: str, timeout: int = 10):
        cfg = self._ssh_lookup(host)
        hostname = cfg.get("hostname", host)
        port = int(cfg.get("port", 22))
        proxyjump = cfg.get("proxyjump")

        sock = None
        self.jump_client = None

        if proxyjump:
            self.jump_client, sock = self._open_jump_channel(
                proxyjump, hostname, port, timeout=timeout
            )

        key = self._load_first_key(cfg.get("identityfile"))

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=hostname,
            port=port,
            username=cfg.get("user") or "root",
            password=self.password,
            pkey=key if not self.password else None,
            look_for_keys=False,
            allow_agent=False,
            sock=sock,
            timeout=timeout,
            auth_timeout=timeout,
            banner_timeout=timeout,
        )
        self.client = client

    def execute(self, cmd, timeout: int = 10):
        stdin, stdout, stderr = self.client.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode("utf-8", "ignore")
        err = stderr.read().decode("utf-8", "ignore")
        if err and not out.strip():
            raise RuntimeError(err.strip())
        return out.strip()

    def close(self):
        if self.client:
            self.client.close()
            self.client = None
        if self.jump_client:
            self.jump_client.close()
            self.jump_client = None

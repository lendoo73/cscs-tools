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
    config_dir : str, optional
        Directory containing `ssh-config` and any included SSH config
        fragments (default: ".ssh").
    key_path : str, optional
        Path to the private key to use for all connections. Overrides
        any IdentityFile entries in the SSH config (default: ".ssh/id_rsa").
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

    Examples
    --------
    >>> ssh = SshService(
    ...     config_dir="~/.ssh",
    ...     key_path="~/.ssh/id_rsa"
    ... )
    >>> ssh.connect_to_host("my-server")
    >>> output = ssh.execute("uname -a")
    >>> print(output)
    >>> ssh.close()

    >>> # Using ProxyJump defined in ssh-config
    >>> ssh = SshService(".ssh")
    >>> ssh.connect_to_host("private-host")   # automatically jumps through proxy
    >>> print(ssh.execute("df -h"))
    >>> ssh.close()
    """

    def __init__(
            self,
            config_dir: str | None = ".ssh",
            key_path: str | None = ".ssh/id_rsa",
            password: str | None = None
    ):
        self.config_dir = os.path.abspath(config_dir)
        self.key_path = os.path.abspath(key_path)
        self.password = password
        self.conf = self._load_ssh_config()
        self._fix_identityfile_paths()
        self._host_dict = self._build_host_dict(self.conf)
        self.client = None
        self.client_jumphost = None
        self.jump_client = None

    def _load_ssh_config(self) -> SSHConfig:
        cfg_path = os.path.join(self.config_dir, "ssh-config")
        conf = SSHConfig()
        lines = []

        if os.path.exists(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
                f.seek(0)
                conf.parse(f)

        include_patterns = []
        for line in lines:
            line = line.strip()
            if line.lower().startswith("include"):
                parts = shlex.split(line)
                include_patterns.extend(parts[1:])

        for pat in include_patterns:
            pat_path = os.path.join(self.config_dir, pat)
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
        key_path = identity_files[0]
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
        """
        Establish an SSH connection to a host alias or hostname.

        This method resolves the host using the parsed SSH configuration,
        applies ProxyJump (if defined), loads the appropriate identity key,
        and opens an SSH connection using Paramiko. The resulting SSHClient
        is stored in `self.client`.

        Parameters
        ----------
        host : str
            Host alias or hostname to connect to. If an alias is defined in
            the SSH config, its parameters (hostname, port, user, proxyjump)
            are used automatically.
        timeout : int, optional
            Timeout (in seconds) for the SSH connection, authentication, and
            banner exchange (default: 10).

        Raises
        ------
        RuntimeError
            If key‑based authentication fails due to a missing passphrase.
        paramiko.SSHException
            For connection or authentication errors.

        Examples
        --------
        >>> ssh = SshService(".ssh")
        >>> ssh.connect_to_host("my-server")
        >>> print(ssh.execute("hostname"))
        >>> ssh.close()

        >>> # Host using ProxyJump defined in ssh-config
        >>> ssh = SshService(".ssh")
        >>> ssh.connect_to_host("internal-server")
        """
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

        """
        Execute a command on the connected remote host.

        Runs the specified command over the active SSH connection and
        returns the decoded stdout output. If the command produces stderr
        without stdout, a RuntimeError is raised.

        Parameters
        ----------
        cmd : str
            Shell command to execute remotely.
        timeout : int, optional
            Command execution timeout in seconds (default: 10).

        Returns
        -------
        str
            The command's stdout output, stripped of whitespace.

        Raises
        ------
        RuntimeError
            If the command writes only to stderr.
        paramiko.SSHException
            If no SSH connection is active or command execution fails.

        Examples
        --------
        >>> ssh = SshService(".ssh")
        >>> ssh.connect_to_host("my-server")
        >>> print(ssh.execute("uname -a"))
        >>> ssh.close()
        """

        stdin, stdout, stderr = self.client.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode("utf-8", "ignore")
        err = stderr.read().decode("utf-8", "ignore")
        if err and not out.strip():
            raise RuntimeError(err.strip())
        return out.strip()

    def close(self):
        """
        Close the active SSH session and any jump‑host session.

        This method should be called after all remote commands have been
        executed. A single SSH connection can be reused to run multiple
        commands with `execute()`, which is more efficient than opening a
        new SSH session for each command.

        Safely terminates both the primary SSH client and any jump‑host
        client if ProxyJump was used.

        Examples
        --------
        >>> ssh = SshService(".ssh")
        >>> ssh.connect_to_host("my-server")
        >>> print(ssh.execute("hostname"))
        >>> print(ssh.execute("whoami"))
        >>> print(ssh.execute("uptime"))
        >>> ssh.close()

        Notes
        -----
        - Safe to call multiple times.
        - Closes both direct and ProxyJump connections.
        """
        if self.client:
            self.client.close()
            self.client = None
        if self.jump_client:
            self.jump_client.close()
            self.jump_client = None
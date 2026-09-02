from cscs_tools.ssh.services.ssh_service import SshService

ssh = SshService(config_path=".ssh_sample/ssh-config", key_path=".ssh_sample/id_rsa")

ssh.connect_to_host("myjumphost")
response = ssh.execute("hostname && whoami")
print(response)
ssh.close()

ssh.connect_to_host("server-producer")
response = ssh.execute("hostname && whoami")
print(response)
ssh.close()
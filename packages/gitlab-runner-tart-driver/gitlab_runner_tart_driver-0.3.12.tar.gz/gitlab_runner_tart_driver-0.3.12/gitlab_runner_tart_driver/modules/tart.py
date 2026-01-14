import json
import os
import re
import subprocess
import tempfile

import click
from jinja2 import Environment
from jinja2 import FileSystemLoader
from paramiko import MissingHostKeyPolicy
from paramiko import SSHClient
from pydantic import BaseModel
from pydantic import Field
from tabulate import tabulate


class TartImage(BaseModel):
    source: str = Field()
    name: str = Field()
    size: int = Field()
    running: bool = Field()


class TartVmSpec(BaseModel):
    cpu_count: int
    memory: int
    disk: int
    display: str
    running: bool
    ip_address: str
    os: str
    size: str


class TartVolume(BaseModel):
    name: str
    source: str
    dest: str
    ro: bool = Field(default=False)

    @classmethod
    def from_string(cls, value):
        components = value.split(":")
        if len(components) < 2:
            raise ValueError(f"'{value}' is not a valid volume mount definition")

        source = os.path.abspath(os.path.expanduser(components[0])).rstrip("/")
        dest = components[1].rstrip("/")
        name = dest.strip("/").replace("/", "__")
        ro = False
        if len(components) > 2:
            if "ro" == components[2]:
                ro = True
            else:
                raise ValueError(f"'{components[2]}' flag unknown")

        return cls(name=name, source=source, dest=dest, ro=ro)


class TartSshSession:
    def __init__(self, username, password, ip):
        self.user = username
        self.ip = ip
        self.password = password
        self.ssh_client = SSHClient()
        self.ssh_client.set_missing_host_key_policy(MissingHostKeyPolicy())
        self.ssh_client.connect(ip, username=username, password=password)

    def exec_ssh_command(self, command, get_pty=True):
        """Executes an ssh command and prints it's output continously to stdout/stderr"""
        _, stdout, stderr = self.ssh_client.exec_command(command, get_pty=get_pty)
        stdout._set_mode("b")
        stderr._set_mode("b")
        for line in iter(lambda: stdout.readline(2048).decode("utf-8", "ignore"), ""):
            click.echo(line, nl=False)
        for line in iter(lambda: stderr.readline(2048).decode("utf-8", "ignore"), ""):
            click.echo(line, nl=False, err=True)
        return stdout.channel.recv_exit_status()


class Tart(object):
    def __init__(self, exec_path="tart"):
        self.tart_executable = exec_path

    def version(self) -> str:
        """Returns the tart version"""
        return self.exec(["--version"]).strip()

    def login(self, username: str, password: str, host: str) -> None:
        """Authenticates against a private OCI registry"""
        p = subprocess.Popen(
            [self.tart_executable, "login", host, "--username", username, "--password-stdin"],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        p.communicate(input=password.encode())
        ret = p.wait()
        if ret != 0:
            raise ValueError("Could not login to OCI registry")

    def pull(self, image) -> None:
        """pulls a new tart VM from a OCI registry. Make sure to use 'login' for private registries"""
        self.exec(["pull", image])

    def clone(self, source_name, new_name) -> None:
        """clones a tart VM"""
        self.exec(["clone", source_name, new_name])

    def delete(self, name) -> None:
        """deletes a tart VM"""
        self.exec(["delete", name])

    def set(self, name, cpu: int = None, memory: int = None, display: str = "") -> None:
        """sets the virtualization parameters like cpu, memory and display for a given tart VM"""
        args = ["set", name]
        if cpu:
            args.extend(["--cpu", str(cpu)])
        if memory:
            args.extend(["--memory", str(memory)])
        if display:
            args.extend(["--display", display])
        self.exec(args)

    def get(self, name) -> TartVmSpec:
        specs = self.exec(["get", name])

        # 'spec' will look like this:
        #
        # tart version < 2.7
        # CPU Memory Disk Display  Running
        # 4   8192   46   1024x768 true
        #
        # tart version > 2.6
        # CPU Memory Disk Size   Display  State
        # 4   8192   50   20.794 1024x768 running
        #
        # tart version > 2.8
        # OS     CPU Memory Disk Size   Display  State
        # darwin 4   8192   50   22.294 1024x768 stopped

        # Read headers
        headers = specs.split("\n")[0]
        header_elements = headers.split(" ")
        header_elements = [s.strip().lower() for s in header_elements if s]

        spec = specs.split("\n")[1]
        spec_elements = spec.split(" ")
        spec_elements = [s.strip() for s in spec_elements if s]

        specs = {}
        for i, spec_element in enumerate(spec_elements):
            specs[header_elements[i]] = spec_element

        # check the state of the machine
        vm_state = specs.get("state", "n/a")
        running = True
        if vm_state == "running" or vm_state == "true":
            running = True
        else:
            running = False

        vm_spec = TartVmSpec(
            cpu_count=int(specs.get("cpu", 0)),
            memory=int(specs.get("memory", 0)),
            disk=int(specs.get("disk", 0)),
            display=specs.get("display", "n/a"),
            running=running,
            ip_address="n/a",
            os=specs.get("os", "n/a"),
            size=specs.get("size", "n/a"),
        )

        if vm_spec.running:
            vm_spec.ip_address = self.ip(name)

        return vm_spec

    def print_spec(self, name, tablefmt="fancy_grid"):
        spec = self.get(name)
        data = [
            (str(spec.cpu_count), str(spec.memory), str(spec.disk), spec.display, str(spec.running), spec.ip_address)
        ]
        print(tabulate(data, headers=["CPU", "Memory", "Disk", "Display", "Running", "IP Address"], tablefmt=tablefmt))

    def stop(self, name) -> None:
        """stops a given tart VM"""
        self.exec(["stop", name])

    def run(self, name: str, volumes: list[TartVolume] = [], no_graphics=True, softnet=False, vnc=False) -> None:
        """starts a given tart VM"""
        args = ["run", name]
        if no_graphics:
            args.append("--no-graphics")
        if softnet:
            args.append("--net-softnet")
        if vnc:
            args.append("--vnc")

        if volumes:
            for d in volumes:
                source_path = os.path.abspath(os.path.expanduser(d.source))
                if d.ro:
                    source_path = f"{source_path}:ro"
                args.extend(["--dir", f"{d.name}:{source_path}"])
        try:
            print(f"Starting VM '{name}'")
            print(f"Command: 'tart {' '.join(args)}'")
            self.spawn_exec(args)
        except Exception as e:
            print(f"Error when running VM {name}")
            raise e

    def ip(self, name, timeout=30, resolver="dhcp") -> str:
        """return the IP adress of a given tart VM"""
        ip = ""
        ret = self.exec(["ip", name, "--wait", str(timeout), "--resolver", resolver])
        for line in ret.split("\n"):
            m = re.match(r"^((?:[0-9]{1,3}\.){3}[0-9]{1,3})$", line)
            if m:
                ip = m.group(1)
                break
        return ip

    def list(self) -> list[TartImage]:
        """lists all available tart images and VMs"""
        tart_images = []

        resources_json = self.exec(["list", "--format", "json"])
        resource_items = json.loads(resources_json)

        for r in resource_items:
            tart_images.append(
                TartImage(
                    source=r.get("Source", None),
                    name=r.get("Name", None),
                    size=int(r.get("Size", 0)),
                    running=r.get("State", "stopped") == "running",
                )
            )
        return tart_images

    def exec(self, cmd) -> str:
        """Executes a given command using subprocess and returns decoded string"""
        exec_cmd = [self.tart_executable]
        if cmd:
            exec_cmd.extend(cmd)

        # GitLab CI passes all TART_* as CUSTOM_ENV_TART* variables to the runner, we need to pass them to tart with the correct key names
        tart_env_vars = self.__load_tart_env_vars()
        exec_env = os.environ.copy()
        exec_env.update(tart_env_vars)

        return subprocess.check_output(exec_cmd, env=exec_env).decode("utf-8")

    def spawn_exec(self, cmd):
        """Spawns a new main process using 'nohup'"""
        exec_cmd = ["nohup", self.tart_executable]
        if cmd:
            exec_cmd.extend(cmd)
        subprocess.Popen(exec_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def ssh_session(self, name, username, password) -> TartSshSession:
        ip = self.ip(name=name)
        if not ip:
            raise ValueError("Could not retrievew IP")

        return TartSshSession(ip=ip, username=username, password=password)

    def install_gitlab_runner(self, name, username, password, force=False, version="latest"):
        file_loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), os.path.pardir, "scripts"))
        env = Environment(loader=file_loader)
        template = env.get_template("install-gitlab-runner.sh.j2")

        data = {"gitlab_runner_force_install": "true" if force else "false", "gitlab_runner_version": version}

        temp = tempfile.NamedTemporaryFile()
        with open(temp.name, "w") as f:
            f.write(template.render(**data))
        f.close()

        remote_temp_dir = "/tmp"
        remote_script_path = os.path.join(remote_temp_dir, "install-gitlab-runner.sh")

        ssh_session = self.ssh_session(name=name, username=username, password=password)
        sftp = ssh_session.ssh_client.open_sftp()
        sftp.put(temp.name, remote_script_path)
        sftp.close()

        # ssh_session.exec_ssh_command(f"cd {remote_build_dir}")
        script_exit_code = ssh_session.exec_ssh_command(f"bash -l {remote_script_path}", get_pty=True)

        if script_exit_code != 0:
            raise ValueError("Error when installing GitLab Runner")

    def __load_tart_env_vars(self, prefix="CUSTOM_ENV_"):
        """Loads all tart related environment variables starting with CUSTOM_ENV prefix"""
        tart_env_vars = {}
        for key, value in os.environ.items():
            if key.startswith(f"{prefix}TART"):
                tart_env_vars[key.replace(f"{prefix}", "")] = value
        return tart_env_vars

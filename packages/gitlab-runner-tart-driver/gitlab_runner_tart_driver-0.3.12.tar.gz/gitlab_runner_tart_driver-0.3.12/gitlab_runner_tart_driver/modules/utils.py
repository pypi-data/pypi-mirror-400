import math
import os
import platform

import click
import psutil
from pydantic import BaseModel
from tabulate import tabulate


class HostSpec(BaseModel):
    memory: int
    cpu_count: int
    os_version: str
    architecture: str


def print_host_spec(tablefmt="fancy_grid"):
    spec = get_host_spec()
    data = [(spec.os_version, str(spec.cpu_count), str(spec.memory), spec.architecture)]
    click.echo(
        tabulate(data, headers=["Host OSX Version", "Host CPUs", "Host RAM", "Host Architecture"], tablefmt=tablefmt)
    )


def get_host_spec() -> HostSpec:
    return HostSpec(
        memory=convert_to_megabytes(psutil.virtual_memory().total),
        cpu_count=os.cpu_count(),
        os_version=platform.mac_ver()[0],
        architecture=platform.mac_ver()[2],
    )


def convert_to_megabytes(size_bytes):
    if size_bytes == 0:
        return 0
    return int(round(size_bytes / math.pow(1024, 2), 2))

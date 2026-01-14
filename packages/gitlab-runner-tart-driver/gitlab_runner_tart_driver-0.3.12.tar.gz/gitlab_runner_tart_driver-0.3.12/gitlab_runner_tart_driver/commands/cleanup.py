import re

import click

from gitlab_runner_tart_driver.modules.gitlab_custom_command_config import GitLabCustomCommandConfig
from gitlab_runner_tart_driver.modules.tart import Tart


@click.command()
@click.option("-x", "--tart-executable", required=False, default="tart", type=str, help="Path to the tart executable.")
def cleanup(tart_executable):
    """Command to greet a user."""
    p = GitLabCustomCommandConfig()

    tart = Tart(exec_path=tart_executable)

    # check if we are actually running in a CI
    if p.ci_project_name:
        tart_vm_name = p.vm_name()
        # remove specific VM that we started
        try:
            click.echo(f"[INFO] stopping '{tart_vm_name}'")
            tart.stop(tart_vm_name)
        except:
            click.secho(f"[ERROR] failed to stop '{tart_vm_name}'", fg="red")

        # remove the VM
        try:
            click.echo(f"[INFO] deleting '{tart_vm_name}'")
            tart.delete(tart_vm_name)
        except:
            click.secho(f"[ERROR] failed to delete '{tart_vm_name}'", fg="red")


def _remove_stopped_vms(tart, pattern):
    tart_images = tart.list()
    tart_vm_map = dict()
    # create map from images
    for i in tart_images:
        tart_vm_map[i.name] = i

    for vm_name, vm in tart_vm_map.items():
        if vm.running or not re.match(pattern, vm_name):
            continue
        try:
            click.echo(f"[INFO] deleting '{vm_name}'")
            tart.delete(vm.name)
        except:
            click.secho(f"[ERROR] failed to delete '{vm_name}'", fg="red")

import socket

import click

from gitlab_runner_tart_driver.__init__ import __version__
from gitlab_runner_tart_driver.modules.gitlab_custom_driver_config import GitLabCustomDriver
from gitlab_runner_tart_driver.modules.gitlab_custom_driver_config import GitLabCustomDriverConfig


@click.command()
def config():
    """Implementation of the CONFIG stage of the Custom Executor.
    Details on how to use this command can be found at
    https://docs.gitlab.com/runner/executors/custom.html#config."""

    c = GitLabCustomDriverConfig(
        builds_dir="/opt/builds",
        cache_dir="/opt/cache",
        hostname=socket.gethostname(),
        driver=GitLabCustomDriver(name="tart", version=__version__),
    )

    click.echo(c.json(exclude_none=True))

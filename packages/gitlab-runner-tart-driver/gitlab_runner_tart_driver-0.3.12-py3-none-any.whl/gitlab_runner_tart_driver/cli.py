import click

from gitlab_runner_tart_driver.__init__ import __version__
from gitlab_runner_tart_driver.commands.cleanup import cleanup
from gitlab_runner_tart_driver.commands.config import config
from gitlab_runner_tart_driver.commands.prepare import prepare
from gitlab_runner_tart_driver.commands.run import run


@click.group()
@click.version_option(__version__, "--version", "-v", message="%(version)s")
def cli(): ...


cli.add_command(config)
cli.add_command(prepare)
cli.add_command(run)
cli.add_command(cleanup)


def start():
    cli(auto_envvar_prefix="gitlab_runner_tart_driver")

"""dragonfly-designbuilder commands which will be added to the dragonfly CLI."""
import click

from dragonfly.cli import main
from .translate import translate


# command group for all designbuilder extension commands.
@click.group(help='dragonfly designbuilder commands.')
def designbuilder():
    pass


# add sub-commands for designbuilder
designbuilder.add_command(translate)

# add designbuilder sub-commands to dragonfly CLI
main.add_command(designbuilder)

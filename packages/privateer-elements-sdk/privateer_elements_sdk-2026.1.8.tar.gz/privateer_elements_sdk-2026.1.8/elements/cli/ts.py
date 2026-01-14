#!/usr/bin/env python

import click
from elements.cli.lib.aliased_group import AliasedGroup
from elements.cli.commands.algorithm import algorithm
from elements.cli.commands.analysis import analysis
from elements.cli.commands.aoi import aoi
from elements.cli.commands.environment import environment
from elements.cli.commands.permission import permission
from elements.cli.commands.credit import credit
from elements.cli.commands.toi import toi
from elements.cli.commands.data import data
from elements.cli.commands.imagery import imagery
from elements.cli.commands.visualization import visualization
from elements.cli.commands.manifest import manifest
from elements.cli.commands.tasks import tasks


@click.command(cls=AliasedGroup)
@click.pass_context
def main(ctx):
    pass


main.add_command(algorithm)
main.add_command(analysis)
main.add_command(aoi)
main.add_command(environment)
main.add_command(permission)
main.add_command(credit)
main.add_command(toi)
main.add_command(data)
main.add_command(imagery)
main.add_command(visualization)
main.add_command(manifest)
main.add_command(tasks)


if __name__ == '__main__':
    main(obj={})

#!/usr/bin/env python3
import click

from pevx.commands import aws_each, docker_proxy, pyclient, uv_proxy


@click.group()
@click.version_option()
def cli():
    """Prudentia CLI - Development tools for Prudentia internal developers."""
    pass


cli.add_command(uv_proxy)

cli.add_command(docker_proxy)

cli.add_command(aws_each)

cli.add_command(pyclient)

if __name__ == "__main__":
    cli()

#!/usr/bin/env python3
"""
ymliu-tool CLI
"""

import click
from . import __version__


@click.group()
@click.version_option(version=__version__)
def main():
    """ymliu-tool - A simple utility tool"""
    pass


@main.command()
@click.argument('text', required=False)
def echo(text):
    """Echo the input text"""
    if text:
        click.echo(text)
    else:
        click.echo("No text provided")


@main.command()
@click.argument('number', type=int)
def square(number):
    """Calculate the square of a number"""
    result = number ** 2
    click.echo(f"{number}² = {result}")


@main.command()
@click.argument('numbers', nargs=-1, type=int)
def sum_cmd(numbers):
    """Sum multiple numbers"""
    if not numbers:
        click.echo("No numbers provided")
        return
    result = sum(numbers)
    click.echo(f"Sum: {result}")


@main.command()
def info():
    """Show tool information"""
    click.echo("ymliu-tool v" + __version__)
    click.echo("A simple utility tool by ymliu")


if __name__ == '__main__':
    main()


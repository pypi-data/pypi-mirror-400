#!/usr/bin/env python
"""
cli.py

Command line interface for tools in Moonframe
"""
import click
import moonframe


def add_version(f):
    """
    Add the version of the tool to the help heading.
    :param f: function to decorate
    :return: decorated function
    """
    doc = f.__doc__
    f.__doc__ = (
        "Package " + moonframe.__name__ + " v" + moonframe.__version__ + "\n\n" + doc
    )

    return f


@click.group()
@add_version
def main_cli():
    """
                    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣴⡶⠖⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣴⣾⣿⠟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣶⣶⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⢀⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣶⣶⡆⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⣶⣤⡄⠀⣿⣿⡇⠀⣿⣿⡇⠀⠀⠀⠀⠀⡄⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠸⣿⣿⣿⣿⣿⡆⠀⣶⣶⡆⠀⣿⣿⡇⠀⣿⣿⡇⠀⣿⣿⡇⠀⠀⠀⠀⢠⠇⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⢻⣿⣿⣿⣿⣿⣦⡙⢿⡇⠀⣿⣿⡇⠀⣿⣿⡇⠀⣿⣿⡇⠀⠀⢀⣴⡟⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⣿⣿⣦⣀⡀⠿⢿⡇⠀⣿⣿⡇⠀⡿⠿⢃⣠⣴⣿⠟⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣦⣤⣭⣭⣤⣴⣶⣾⣿⣿⠿⠋⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠛⠛⠛⠛⠛⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

    ------------------------------  Moonframe  ------------------------------

    You are now using the Command line interface of moonframe package,
    a set of tools created at CERFACS (https://cerfacs.fr).

    This is a python package currently installed in your python environement.

    All graphs are displayed in your default web browser.
    """
    pass


@click.command()
@click.argument(
    "filename",
    type=click.Path(exists=True),
)
@click.option(
    "--delimiter",
    "-d",
    type=str,
    default=",",
    help="Delimiter for the .csv. Default to ','",
)
@click.option(
    "--skip",
    "-s",
    type=int,
    default=None,
    help="Skip the Nth first rows.",
)
@click.option(
    "--port", "-p", type=str, default=None, help="Set port."
)
def scatter(filename, port, delimiter, skip):
    """Scatter plot

    Takes a .csv by default"""
    from moonframe.app_builder import build_app_scatter
    from moonframe.application import serve_app

    app = build_app_scatter(filename, delimiter, skip)
    serve_app(app, port)


main_cli.add_command(scatter)

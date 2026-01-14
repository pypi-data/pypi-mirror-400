"""App builders wraps general Flask application (defined in application.py)
to create specific graphs (scatter, circular packing, ...)
All app builders returns a Flask app. To use it, serve it with the
`serve_app()` function."""

import json
from flask import Flask
from moonframe.application import (
    create_flask_app,
    create_flask_app_dict,
    create_flask_app_with_summary,
)


def build_app_scatter(filepath: str, delimiter: str = ";", skip: int = None) -> Flask:
    """Build a Flask app for the scatter plot.
    Take a CSV file as input.

    Args:
        filepath (str): Path to the CSV input file.
        delimiter (str, optional): Separator used in the CSV file. Defaults to ";".

    Returns:
        Flask: Flask app. Serve with `serve_app()`
    """
    return create_flask_app(
        "scatter.html", filepath=filepath, delimiter=delimiter, skip=skip
    )


def build_app_treeshow(
    filepath: str, repo_path: str, repo_name: str, color_rules: dict = {}
) -> Flask:
    """Build a Flask app to explore repository with a circular packing graph.
    Made for Marauders map tree-show : `mmap tree-showjs`
    Take `struct_repo.json` file as input (see mmap).

    Args:
        filepath (str): Path to the `struct_repo.json` file.
        repo_path (str): Path to the repository.
        repo_name (str): Name of the package.
        color_rules (dict): Custom color pattern. Default to {}.

    Returns:
        Flask: Flask app. Serve with `serve_app()`
    """
    return create_flask_app(
        "circular_packing.html",
        filepath=filepath,
        repo_name=repo_name,
        repo_path=repo_path,
        color_rules=json.dumps(color_rules),
        is_summary=False,
    )


def build_app_treeshow_with_summary(
    filepath: str,
    summarypath: str,
    repo_path: str,
    repo_name: str,
    color_rules: dict = {},
) -> Flask:
    """Build a Flask app to explore repository with a circular packing graph.
    Made for Marauders map tree-show : `mmap tree-showjs`
    Take two files as input :

            - the repo structure dataset = `struct_repo.json` (filepath)
            - an additionnal dataset (summarypath) to add more context.

    Args:
        filepath (str): Path to the `struct_repo.json` file.
        summarypath (str): Path to the summary file
        repo_path (str): Path to the repository.
        repo_name (str): Name of the package.
        color_rules (dict): Custom color pattern. Default to {}.

    Returns:
        Flask: Flask app. Serve with `serve_app()`
    """
    return create_flask_app_with_summary(
        "circular_packing.html",
        filepath=filepath,
        summarypath=summarypath,
        repo_name=repo_name,
        repo_path=repo_path,
        color_rules=json.dumps(color_rules),
        is_summary=True,
    )


def build_app_nobvisual(data: dict, title: str, legend: dict = {}) -> Flask:
    """Build a Flask app to explore files with a circular packing graph.
    Made for nobvisual.

    Take as input a nested structure with `id`, `text`, `color`, `datum` and `children` key
    like this :

    [
        {
            "id": "0",
            "text": "my root",
            "color": "red",
            "children": [
                {
                    "id": "01",
                    "text": "children1",
                    "color": "green",
                    "children": [],
                    "datum": 1.0,
                },
                {
                    "id": "02",
                    "text": "children2",
                    "color": "green",
                    "children": [],
                    "datum": 1.0,
                }
            "datum": 1.0
        }
    ]

    Args:
        data (dict) : Input dict from nobvisual.
        title (str): Title of the graph.
        legend (dict): Custom legend.

    Returns:
        Flask: Flask app. Serve with `serve_app()`.
    """
    return create_flask_app_dict(
        "nobvisual.html",
        data=data,
        title=title,
        legend=json.dumps(legend),
    )


def build_app_network(
    filepath: str, repo_path: str, repo_name: str, color_rules: dict = {}
) -> Flask:
    """
    Build a Flask app to explore a repository with a network chart.
    Made for Marauders map cg-show: `mmap cg-showjs`
    Take `callgraph.json` file as input (see mmap).

    Args:
        filepath (str): Path to the .json.
        repo_path (str): Path to the repo
        repo_name (str): Name of the repo
        color_rules (dict): Custom color pattern. Default to {}.

    Returns:
        Flask: Flask app. Serve with `serve_app()`.
    """
    return create_flask_app(
        "network.html",
        filepath=filepath,
        repo_path=repo_path,
        repo_name=repo_name,
        color_rules=json.dumps(color_rules),
    )

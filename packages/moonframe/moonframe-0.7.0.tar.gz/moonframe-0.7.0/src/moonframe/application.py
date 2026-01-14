"""The application module provides low-level functions that build Flask app.
Each function :

   - Takes any HTML file as template.
   - Defines a general route "/data" to pass user's database to HTML.
   - Accepts flexible **kwargs parameters to configure the app as needed.

In Moonframe, app builders are used on top of theses applications to create the graphs.
See app_builder.py.
"""

import webbrowser
from pathlib import Path
import json
import socket
from flask import Flask, render_template, send_from_directory, Response
import waitress
from loguru import logger


def get_free_port():  # pragma: no cover
    """
    Get a random and available port (local) for any application.

    Returns:
        str: Port number
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def create_flask_app(html: str, filepath: str, **kwargs) -> Flask:
    """
    Create a basic Flask app for Moonframe that takes any data file (.json,
    .csv, ...) as input. The input data is stored in the "/data" route.
    You can pass as many variables as you need using the **kwargs arg.
    For example :

    ```
    app = create_flask_app(html="index.html", filepath="test.csv", arg1=0)
    ```

    You can get `arg1` in your HTML template with :

    ```
    <script>
        const arg1 = "{{ arg1 }}"
    </script>
    ```
    WARNING : this returns a string. You can use a parser to get another
    type. e.g. : 

    ````
    <script>
        const arg1 = parseInt("{{ arg1 }}")
    </script>
    ```
    
    Args:
        html (str): html filename.
        filepath (str): Path to the data file.

    Returns:
        Flask : Flask app
    """
    app = Flask("moonframe")

    @app.route("/")
    def index():
        return render_template(html, **kwargs)

    @app.route("/data")
    def get_data():
        file = Path(filepath).resolve()
        return send_from_directory(file.parent, file.name)

    return app


def create_flask_app_with_summary(
    html: str, filepath: str, summarypath: str, **kwargs
) -> Flask:
    """
    Create a basic Flask app that takes two files as input :

            - the plot's dataset (filepath)
            - an additionnal dataset (summarypath) to add more context.

    The additionnal dataset must be a simple dictionnary :

    ```
    {
        "path1": "summary1",
        "path2": "summary2",
        ...
    }
    ```

    You can fetch a specific value using the route "/summary/<path_id>"
    where `<path_id>` is the key in the dictionnary ("path1", "path2").
    You can pass also as many variables as you need using the **kwargs arg.
    For example :

    ```
    app = create_flask_app(html="index.html", filepath="test.csv", arg1=0)
    ```

    You can get `arg1` in your HTML template with :

    ```
    <script>
        const arg1 = "{{ arg1 }}"
    </script>
    ```

    Args:
        html (str): html filename.
        filepath (str): Path to the file.

    Returns:
        Flask : Flask app
    """
    app = Flask("moonframe")

    @app.route("/")
    def index():
        return render_template(html, **kwargs)

    @app.route("/data")
    def get_data():
        file = Path(filepath).resolve()
        return send_from_directory(file.parent, file.name)

    # Load summary JSON at start-up
    with open(summarypath, "r", encoding="utf-8") as f:
        summaryjson = json.load(f)

    @app.route("/summary/<path:path_id>")
    def get_summary(path_id):
        summary = summaryjson.get(path_id)
        if summary:
            return Response(summary, mimetype="text/plain")
        return Response("Not found", status=404, mimetype="text/plain")

    return app


def create_flask_app_dict(html: str, data: dict, **kwargs) -> Flask:
    """
    Create a Flask app that takes a dict as input.

    Get your dict in your HTML file with:

    ```
    <script>
        const data = JSON.parse('{{ data | safe }}')
    </script>
    ```

    You can also pass as many variables as you want with the **kwargs arg.
    For example :

    ```
    app = create_flask_app(html="index.html", filepath="test.csv", arg1=0)
    ```

    You can get `arg1` in your HTML template with :

    ```
    <script>
        const arg1 = "{{ arg1 }}"
    </script>
    ```

    Args:
        html (str): html filename.
        data (dict): Input dict.

    Returns:
        Flask : Flask app
    """
    app = Flask("moonframe")

    @app.route("/")
    def index():
        return render_template(html, data=json.dumps(data), **kwargs)

    return app


def serve_app(app: Flask, port: str = None) -> None:  # pragma: no cover
    """Serve locally any Flask app with waitress and open it in your default browser.
    It is a production server.

    Args:
        app (Flask): Flask app.
        port (str): Port.
    """
    if port is None:
        port = get_free_port()
    logger.success(f"App created. Serve at :\nhttp://127.0.0.1:{port}")
    logger.info("Press CTRL+C to exit.")
    webbrowser.open(f"http://127.0.0.1:{port}")
    waitress.serve(app, port=port, threads=6)

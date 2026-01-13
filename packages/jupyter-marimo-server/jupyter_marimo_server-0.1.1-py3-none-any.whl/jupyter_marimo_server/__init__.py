from pathlib import Path
import secrets
import base64


def setup_marimo():
    token = secrets.token_urlsafe(16)
    return {
        "command": [
            "marimo",
            "edit",
            "--port",
            "{port}",
            "--token",
            "--token-password",
            token,
            "--headless",
        ],
        "environment": {},
        "timeout": 120,
        "request_headers_override": {
            "Authorization": "Basic "
            + base64.b64encode(b" :" + token.encode()).decode()
        },
        "launcher_entry": {
            "title": "Marimo",
            "icon_path": Path(__file__).parent.joinpath("icons", "marimo.svg"),
        },
    }

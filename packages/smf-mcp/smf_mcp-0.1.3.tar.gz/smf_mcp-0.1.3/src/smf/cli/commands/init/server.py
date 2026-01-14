from pathlib import Path

from smf.cli.commands.init.templates import server_template
from smf.cli.io import write_utf8


def write_server(project_path: Path) -> None:
    server_file = project_path / "server.py"
    write_utf8(server_file, server_template())

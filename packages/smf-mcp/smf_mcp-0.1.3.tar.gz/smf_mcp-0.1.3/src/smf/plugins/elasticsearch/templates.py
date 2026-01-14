from importlib import resources


def _read_template(name: str) -> str:
    return resources.files(__package__).joinpath("templates", name).read_text(encoding="utf-8")


def server_template(server_name: str, default_index: str, es_hosts: str) -> str:
    return (
        _read_template("server.tpl")
        .replace("{server_name}", server_name)
        .replace("{default_index}", default_index)
        .replace("{es_hosts}", es_hosts)
    )


def env_template(es_hosts: str, server_name: str) -> str:
    return (
        _read_template("env.tpl")
        .replace("{es_hosts}", es_hosts)
        .replace("{server_name}", server_name)
    )


def readme_template(server_name: str, default_index: str, es_hosts: str) -> str:
    return (
        _read_template("readme.tpl")
        .replace("{server_name}", server_name)
        .replace("{default_index}", default_index)
        .replace("{es_hosts}", es_hosts)
    )


def requirements_template(version: str) -> str:
    return _read_template("requirements.tpl").replace("{version}", version)


def custom_tools_template() -> str:
    return _read_template("custom_tools.tpl")

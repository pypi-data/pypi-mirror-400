from importlib import resources


def _read_template(name: str) -> str:
    # Import from the templates package (not this module)
    return resources.files("smf.plugins.elasticsearch.templates").joinpath(name).read_text(encoding="utf-8")


def server_template(server_name: str, default_index: str, es_hosts: str) -> str:
    template = _read_template("server.tpl")
    # Replace variables first
    template = template.replace("{server_name}", server_name)
    template = template.replace("{default_index}", default_index)
    template = template.replace("{es_hosts}", es_hosts)
    # Then replace double braces with single braces (for f-strings and dict literals)
    template = template.replace("{{", "{").replace("}}", "}")
    return template


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


def elasticsearch_tools_template() -> str:
    return _read_template("elasticsearch.tpl")

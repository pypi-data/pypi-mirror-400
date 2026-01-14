from importlib import resources


def _read_template(name: str) -> str:
    # Import from the templates package (not this module)
    return resources.files("smf.cli.commands.init.templates").joinpath(name).read_text(encoding="utf-8")


def example_tool_template() -> str:
    return _read_template("tools.tpl")


def example_resource_template() -> str:
    return _read_template("resources.tpl")


def example_prompt_template() -> str:
    return _read_template("prompts.tpl")


def example_test_template() -> str:
    return _read_template("tests.tpl")


def server_template() -> str:
    return _read_template("server.tpl")


def readme_template(project_name: str) -> str:
    return _read_template("readme.tpl").replace("{project_name}", project_name)

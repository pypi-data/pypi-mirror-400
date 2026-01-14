from importlib import resources


def _read_template(name: str) -> str:
    return resources.files(__package__).joinpath("templates", name).read_text(encoding="utf-8")


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

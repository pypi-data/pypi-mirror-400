from importlib import resources


def _read_template(name: str) -> str:
    return resources.files(__package__).joinpath("templates", name).read_text(encoding="utf-8")


def tool_template(tool_name: str, description: str | None) -> str:
    desc = description or "Tool description"
    return (
        _read_template("tool.tpl")
        .replace("{tool_name}", tool_name)
        .replace("{description}", desc)
    )

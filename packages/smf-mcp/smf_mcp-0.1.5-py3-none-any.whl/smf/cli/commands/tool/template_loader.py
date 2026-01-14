from importlib import resources


def _read_template(name: str) -> str:
    # Import from the templates package (not this module)
    return resources.files("smf.cli.commands.tool.templates").joinpath(name).read_text(encoding="utf-8")


def tool_template(tool_name: str, description: str | None) -> str:
    desc = description or "Tool description"
    template = _read_template("tool.tpl")
    # Replace variables first
    template = template.replace("{tool_name}", tool_name)
    template = template.replace("{description}", desc)
    # Then replace double braces with single braces (for dict literals)
    template = template.replace("{{", "{").replace("}}", "}")
    return template

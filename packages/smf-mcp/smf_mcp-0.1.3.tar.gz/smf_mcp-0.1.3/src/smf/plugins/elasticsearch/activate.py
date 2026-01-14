from pathlib import Path

from smf.plugins.elasticsearch.env import update_env
from smf.plugins.elasticsearch.requirements import ensure_requirements
from smf.plugins.elasticsearch.templates import custom_tools_template
from smf.cli.io import write_utf8


def activate_plugin_command(args) -> int:
    plugin_name = args.plugin
    target_dir = Path(args.directory).resolve()

    if not target_dir.exists():
        print(f"Error: Directory {target_dir} does not exist.")
        return 1

    if not (target_dir / "server.py").exists():
        print(
            f"Warning: {target_dir} does not appear to be a standard SMF project (missing server.py)."
        )
        if not args.force:
            print("Use --force to proceed anyway.")
            return 1

    if plugin_name == "elasticsearch":
        return _activate_elasticsearch(target_dir, args)

    print(
        f"Error: Unknown plugin '{plugin_name}'. Available plugins: elasticsearch",
    )
    return 1


def _activate_elasticsearch(project_path: Path, args) -> int:
    print(f"Activating Elasticsearch plugin in {project_path}...")

    tools_dir = project_path / "src" / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)

    custom_tool_file = tools_dir / "elasticsearch_custom.py"

    if custom_tool_file.exists() and not args.force:
        print(f"Warning: {custom_tool_file} already exists. Skipping creation.")
    else:
        content = custom_tools_template()
        write_utf8(custom_tool_file, content)
        print(f"? Created {custom_tool_file}")

    update_env(project_path, args.hosts or "http://localhost:9200")
    ensure_requirements(project_path)

    print("\n? Elasticsearch plugin activated!")
    print("\nNext steps:")
    print("1. Install dependencies:")
    print("   uv add smf-mcp[elasticsearch]")
    print("\n2. Update your server.py to register the plugin:")
    print(
        """
    from smf.plugins.elasticsearch import ElasticsearchClient, create_elasticsearch_tools
    from src.tools.elasticsearch_custom import create_custom_tools
    import os

    # Setup Elasticsearch
    es_client = ElasticsearchClient(hosts=os.getenv(\"ELASTICSEARCH_HOSTS\", \"http://localhost:9200\"))

    # Register standard tools
    es_tools = create_elasticsearch_tools(es_client, index=\"my_index\")
    for tool in es_tools:
        mcp.tool(tool)

    # Register custom tools
    custom_tools = create_custom_tools(es_client, index=\"my_index\")
    for tool in custom_tools:
        mcp.tool(tool)
    """
    )

    return 0

from pathlib import Path

from smf.cli.commands.init.examples import write_examples
from smf.cli.commands.init.readme import write_readme
from smf.cli.commands.init.server import write_server
from smf.cli.commands.init.structure import create_structure


def init_project(args) -> int:
    project_path = Path(args.directory)
    if project_path.exists() and not args.force:
        print(f"Error: Directory {project_path} already exists. Use --force to overwrite.")
        return 1

    project_path.mkdir(parents=True, exist_ok=True)

    paths = create_structure(project_path)
    write_examples(paths)
    
    # Check if Elasticsearch plugin is requested
    if getattr(args, "elasticsearch", False):
        _init_elasticsearch_plugin(project_path, args)
        # Use Elasticsearch-specific server and readme
        _write_elasticsearch_server(project_path, args)
        _write_elasticsearch_readme(project_path, args)
    else:
        write_server(project_path)
        project_name = args.directory or "SMF Server"
        write_readme(project_path, project_name)

    print(f"Created MCP project in {project_path}")
    
    if getattr(args, "elasticsearch", False):
        print("\nNext steps:")
        print(f"  1. cd {project_path}")
        print("  2. Configure .env file with your Elasticsearch settings")
        print("  3. Run: smf run server.py")
        print("  4. Test: smf inspector server.py")
    
    return 0


def _init_elasticsearch_plugin(project_path: Path, args) -> None:
    """Initialize Elasticsearch plugin in the project."""
    from smf.plugins.elasticsearch.env import write_env_example
    from smf.plugins.elasticsearch.template_loader import elasticsearch_tools_template
    from smf.plugins.elasticsearch.requirements import ensure_requirements
    from smf.cli.io import write_utf8
    
    es_hosts = getattr(args, "es_hosts", "http://localhost:9200") or "http://localhost:9200"
    default_index = getattr(args, "es_index", None) or "my_index"
    server_name = args.name or f"Elasticsearch SMF Server ({default_index})"
    
    # Create .env.example (template, not the actual .env)
    write_env_example(project_path, es_hosts, server_name)
    
    # Create Elasticsearch tools file
    tools_dir = project_path / "src" / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)
    elasticsearch_tools_file = tools_dir / "elasticsearch.py"
    write_utf8(elasticsearch_tools_file, elasticsearch_tools_template())
    print(f"? Created {elasticsearch_tools_file}")
    
    # Ensure requirements.txt exists
    ensure_requirements(project_path)


def _write_elasticsearch_server(project_path: Path, args) -> None:
    """Write Elasticsearch-specific server.py."""
    from smf.plugins.elasticsearch.template_loader import server_template
    from smf.cli.io import write_utf8
    
    es_hosts = getattr(args, "es_hosts", "http://localhost:9200") or "http://localhost:9200"
    default_index = getattr(args, "es_index", None) or "my_index"
    server_name = args.name or f"Elasticsearch SMF Server ({default_index})"
    
    server_file = project_path / "server.py"
    write_utf8(server_file, server_template(server_name, default_index, es_hosts))


def _write_elasticsearch_readme(project_path: Path, args) -> None:
    """Write Elasticsearch-specific README.md."""
    from smf.plugins.elasticsearch.template_loader import readme_template
    from smf.cli.io import write_utf8
    
    es_hosts = getattr(args, "es_hosts", "http://localhost:9200") or "http://localhost:9200"
    default_index = getattr(args, "es_index", None) or "my_index"
    server_name = args.name or f"Elasticsearch SMF Server ({default_index})"
    
    readme_file = project_path / "README.md"
    write_utf8(readme_file, readme_template(server_name, default_index, es_hosts))

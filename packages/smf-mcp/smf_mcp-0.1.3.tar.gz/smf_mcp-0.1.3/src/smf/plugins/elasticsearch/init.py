from pathlib import Path

from smf.plugins.elasticsearch.env import write_env_example
from smf.plugins.elasticsearch.requirements import write_requirements
from smf.plugins.elasticsearch.settings import write_settings
from smf.plugins.elasticsearch.templates import readme_template, server_template
from smf.cli.io import write_utf8


def init_elasticsearch_command(args) -> int:
    project_path = Path(args.directory)
    if project_path.exists() and not args.force:
        print(f"Error: Directory {project_path} already exists. Use --force to overwrite.")
        return 1

    project_path.mkdir(parents=True, exist_ok=True)

    (project_path / "src").mkdir(exist_ok=True)
    tools_dir = project_path / "src" / "tools"
    tests_dir = project_path / "tests"

    tools_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)

    write_utf8(tools_dir / "__init__.py", '"""Tools module."""\n')

    es_hosts = args.hosts or "http://localhost:9200"
    default_index = args.index or "my_index"
    server_name = args.name or f"Elasticsearch SMF Server ({default_index})"

    server_file = project_path / "server.py"
    write_utf8(server_file, server_template(server_name, default_index, es_hosts))

    write_env_example(project_path, es_hosts, server_name)
    write_settings(project_path, server_name)
    write_requirements(project_path)

    readme_file = project_path / "README.md"
    write_utf8(readme_file, readme_template(server_name, default_index, es_hosts))

    print(f"\n? Elasticsearch SMF server created in '{project_path}'")
    print("\nNext steps:")
    print(f"  1. cd {project_path}")
    print("  2. Configure .env file with your Elasticsearch settings")
    print("  3. Run: smf run server.py")
    print("  4. Test: smf inspector server.py")

    return 0

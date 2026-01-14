from pathlib import Path

from smf.plugins.elasticsearch.template_loader import env_template
from smf.cli.io import write_utf8


def write_env_example(project_path: Path, es_hosts: str, server_name: str) -> None:
    env_example_file = project_path / ".env.example"
    write_utf8(env_example_file, env_template(es_hosts, server_name))


def update_env(project_path: Path, es_hosts: str) -> None:
    env_file = project_path / ".env"

    env_content = ""
    if env_file.exists():
        env_content = env_file.read_text(encoding="utf-8")

    if "ELASTICSEARCH_HOSTS" not in env_content:
        new_env_config = f'''
# Elasticsearch Configuration
ELASTICSEARCH_HOSTS={es_hosts}
# ELASTICSEARCH_API_KEY=your-api-key-here
# Basic auth options (use one of the following):
# ELASTICSEARCH_USERNAME=your-username
# ELASTICSEARCH_PASSWORD=your-password
# OR
# ELASTICSEARCH_BASIC_AUTH=["username", "password"]
# ELASTICSEARCH_VERIFY_CERTS=true
# ELASTICSEARCH_TIMEOUT=30
# ELASTICSEARCH_MAX_RETRIES=3
'''
        with open(env_file, "a", encoding="utf-8") as f:
            f.write(new_env_config)
        print(f"? Updated {env_file} with Elasticsearch configuration")
    else:
        print("? .env already contains Elasticsearch configuration")

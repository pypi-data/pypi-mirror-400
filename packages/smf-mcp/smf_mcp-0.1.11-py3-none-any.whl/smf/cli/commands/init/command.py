import argparse

from smf.cli.commands.init.scaffold import init_project


def add_parser(subparsers) -> None:
    init_parser = subparsers.add_parser("init", help="Initialize new project")
    init_parser.add_argument("directory", help="Project directory")
    init_parser.add_argument("--name", help="Project name")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing")
    
    # Plugin options
    init_parser.add_argument(
        "--elasticsearch",
        action="store_true",
        help="Initialize with Elasticsearch plugin",
    )
    init_parser.add_argument(
        "--es-hosts",
        default="http://localhost:9200",
        help="Elasticsearch hosts (requires --elasticsearch, default: http://localhost:9200)",
    )
    init_parser.add_argument(
        "--es-index",
        help="Default Elasticsearch index name (requires --elasticsearch, default: my_index)",
    )
    
    init_parser.set_defaults(func=init_command)


def init_command(args: argparse.Namespace) -> int:
    return init_project(args)

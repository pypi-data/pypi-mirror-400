import importlib.metadata
import sys
from pathlib import Path

def _get_version() -> str:
    try:
        return importlib.metadata.version("smf-mcp")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def _print_version() -> None:
    prog = Path(sys.argv[0]).name or "smf"
    print(f"{prog} {_get_version()}")


def main() -> int:
    argv = sys.argv[1:]
    if "--version" in argv:
        _print_version()
        return 0

    from smf.cli.parser import build_parser

    parser = build_parser(_get_version())
    args = parser.parse_args(argv)

    if not getattr(args, "func", None):
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

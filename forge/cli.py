from __future__ import annotations

import argparse
import sys

from forge.update import _add_arguments as _add_update_arguments
from forge.update import _run as _run_update


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="forge")
    sub = parser.add_subparsers(dest="command", required=True)

    update_parser = sub.add_parser("update", help="diff or write composed skills")
    _add_update_arguments(update_parser)
    update_parser.set_defaults(func=_run_update)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

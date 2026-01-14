from __future__ import annotations

import argparse
import sys

from app.cli.evals import add_eval_subcommand, handle_eval


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="mengram")
    subparsers = parser.add_subparsers(dest="cmd", required=True)
    add_eval_subcommand(subparsers)
    args = parser.parse_args(argv)
    if args.cmd == "eval":
        return handle_eval(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

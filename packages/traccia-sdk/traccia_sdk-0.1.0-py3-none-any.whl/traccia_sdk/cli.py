"""CLI for traccia_sdk utilities."""

from __future__ import annotations

import argparse
import sys
import urllib.request

from traccia_sdk import start_tracing, stop_tracing
from traccia_sdk.exporter.http_exporter import DEFAULT_ENDPOINT


def _check(args) -> int:
    endpoint = args.endpoint or DEFAULT_ENDPOINT
    req = urllib.request.Request(endpoint, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            code = resp.getcode()
            print(f"Connectivity OK (status {code}) to {endpoint}")
            return 0
    except Exception as exc:
        print(f"Connectivity FAILED to {endpoint}: {exc}", file=sys.stderr)
        return 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="traccia_sdk", description="SDK utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="Verify connectivity to ingest endpoint")
    check.add_argument("--endpoint", help="Override ingest endpoint")
    check.add_argument("--api-key", help="API key (optional for basic connectivity)")
    check.set_defaults(func=_check)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())


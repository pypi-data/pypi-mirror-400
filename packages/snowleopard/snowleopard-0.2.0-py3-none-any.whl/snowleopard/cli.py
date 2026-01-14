# -*- coding: utf-8 -*-
# copyright 2025 Snow Leopard, Inc
# released under the MIT license - see LICENSE file

import dataclasses
import json
import sys
import argparse
from typing import List, Optional, Dict, Any

from httpx import HTTPStatusError
from snowleopard import __version__, SnowLeopardClient
from snowleopard.models import RetrieveResponseError


def _create_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="snowy", description="Snow Leopard client library CLI"
    )
    parser.add_argument("--apikey", "-a", required=False, help="Snow Leopard API key")
    parser.add_argument("--loc", "-l", required=False, help="Snow Leopard location")
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.set_defaults(command_func=None)
    subparsers = parser.add_subparsers(
        dest="command",
        metavar="command",
        help="run with <command name> --help for more info",
    )

    retrieve = subparsers.add_parser(
        "retrieve", help="Retrieve data for natural language query"
    )
    retrieve.set_defaults(command_func=_retrieve)
    response = subparsers.add_parser(
        "response", help="Get streaming response for natural language query"
    )
    response.set_defaults(command_func=_response)

    for subparser in (retrieve, response):
        subparser.add_argument(
            "--datafile", "-df", type=str, help="ID for playground datafile to query"
        )
        subparser.add_argument(
            "--knownData",
            "-d",
            action="append",
            help="Known data in key=value format (can be specified multiple times)",
        )
        subparser.add_argument("question", type=str, help="Natural language query")

    return parser


def _parse_known_data(known_data_list: Optional[List[str]]) -> Optional[Dict[str, Any]]:
    if not known_data_list:
        return None

    result = {}
    for item in known_data_list:
        if "=" not in item:
            print(
                f"Error: Invalid knownData format '{item}'. Expected key=value",
                file=sys.stderr,
            )
            sys.exit(1)
        key, value = item.split("=", 1)
        result[key] = value
    return result


def _get_client(parsed_args):
    try:
        client = SnowLeopardClient(api_key=parsed_args.apikey, loc=parsed_args.loc)
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    return client


def _retrieve(parsed_args):
    try:
        known_data = _parse_known_data(parsed_args.knownData)
        with _get_client(parsed_args) as client:
            resp = client.retrieve(
                user_query=parsed_args.question,
                known_data=known_data,
                datafile_id=parsed_args.datafile,
            )
            print(json.dumps(dataclasses.asdict(resp)))
            if isinstance(resp, RetrieveResponseError):
                sys.exit(1)
    except HTTPStatusError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


def _response(parsed_args):
    try:
        known_data = _parse_known_data(parsed_args.knownData)
        with _get_client(parsed_args) as client:
            for chunk in client.response(
                known_data=known_data,
                user_query=parsed_args.question,
                datafile_id=parsed_args.datafile,
            ):
                print(json.dumps(dataclasses.asdict(chunk)))
    except HTTPStatusError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


def main(args: Optional[List[str]] = None) -> None:
    """CLI entry point for snowleopard."""
    parser = _create_parser()
    parsed_args = parser.parse_args(args=args)

    if parsed_args.command_func is not None:
        parsed_args.command_func(parsed_args)
    else:
        parser.print_help(file=sys.stderr)
        sys.exit(1)

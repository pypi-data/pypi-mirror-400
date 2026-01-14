import argparse
import datetime
import json
from gocd_tools.defaults import PACKAGE_NAME
from gocd_tools.utils import eprint
from gocd_tools.cli.setup import setup_cli


def to_str(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def run():
    parser = argparse.ArgumentParser(prog=PACKAGE_NAME)
    commands = parser.add_subparsers(title="COMMAND")
    setup_parser = commands.add_parser("setup")
    setup_cli(setup_parser)

    args = parser.parse_args()
    # Execute default function
    if hasattr(args, "func"):
        success, response = args.func(args)
        output = ""
        if success:
            response["status"] = "success"
        else:
            response["status"] = "failed"

        try:
            output = json.dumps(response, indent=4, sort_keys=True, default=to_str)
        except Exception as err:
            eprint("Failed to format: {}, err: {}".format(output, err))
        if success:
            print(output)
        else:
            eprint(output)
    return None

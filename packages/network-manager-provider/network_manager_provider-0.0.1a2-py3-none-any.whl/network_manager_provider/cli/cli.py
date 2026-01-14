# Copyright (C) 2024  rasmunk
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import argparse
import datetime
import json
import sys
from network_manager_provider._version import __version__
from network_manager_provider.utils.format import eprint
from network_manager_provider.defaults import (
    PACKAGE_NAME,
    NETWORK_MANAGER_PROVIDER_CLI_STRUCTURE,
)
from network_manager_provider.cli.helpers import cli_exec, import_from_module
from network_manager_provider.codes import SUCCESS, FAILURE


def to_str(o):
    if hasattr(o, "asdict"):
        return o.asdict()
    if isinstance(o, datetime.datetime):
        return o.__str__()


def recursive_add_cli_operations(
    cli_type,
    cli_operations,
    parser,
    module_core_prefix="network_manager_provider",
    module_cli_prefix="network_manager_provider.cli.input_groups",
):
    """This functions generates the libvirt cli interfaces for each operation type."""
    for operation in cli_operations:
        if isinstance(operation, list):
            return recursive_add_cli_operations(cli_type, operation, parser)
        if isinstance(operation, dict):
            # Note, we only expect there to be one key here
            operation_key = list(operation.keys())[0]
            # We postfix the module path with the
            # operation_key, such that loading will correctly occur once
            # we get down to an operation that is a simple string
            module_core_prefix = module_core_prefix + ".{}".format(operation_key)
            module_cli_prefix = module_cli_prefix + ".{}".format(operation_key)

            # Note, we expect the values to be a list that
            # contains the underlying operations
            operation_values = operation.values()
            operation_parser = parser.add_parser(operation_key)

            return recursive_add_cli_operations(cli_type, operation_values, parser)
        # Dynamically import the different cli input groups
        if isinstance(operation, str):
            operation_parser = parser.add_parser(operation)
            operation_input_groups_func = import_from_module(
                "{}.{}".format(module_cli_prefix, cli_type),
                "{}".format(cli_type),
                "{}_groups".format(operation),
            )

            argument_groups = []
            input_groups = operation_input_groups_func(operation_parser)

            if not isinstance(input_groups, (list, set, tuple)):
                argument_groups = [input_groups]
            else:
                argument_groups = input_groups

            operation_parser.set_defaults(
                func=cli_exec,
                module_path="{}.{}.{}".format(module_core_prefix, cli_type, operation),
                module_name="{}".format(cli_type),
                func_name=operation,
                argument_groups=argument_groups,
            )


def add_network_manager_provider_cli(commands):
    for cli_structure in NETWORK_MANAGER_PROVIDER_CLI_STRUCTURE:
        for cli_type, cli_operations in cli_structure.items():
            function_provider = commands.add_parser(cli_type)
            function_parser = function_provider.add_subparsers(title="COMMAND")
            recursive_add_cli_operations(cli_type, cli_operations, function_parser)


def add_base_cli_operations(parser):
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=__version__,
        help="Print the version of the program",
    )


def main(args):
    parser = argparse.ArgumentParser(
        prog=PACKAGE_NAME, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # Add the basic CLI functions
    add_base_cli_operations(parser)
    # Add libvirt functions to the CLI
    commands = parser.add_subparsers(title="COMMAND")
    add_network_manager_provider_cli(commands)

    parsed_args = parser.parse_args(args)
    # Convert to a dictionary
    arguments = vars(parsed_args)
    # Execute default function
    if "func" in arguments:
        func = arguments.pop("func")
        success, response = func(arguments)
        output = ""
        if success:
            response["status"] = "success"
        else:
            response["status"] = "failed"

        try:
            output = json.dumps(response, indent=4, sort_keys=True, default=to_str)
        except Exception as err:
            eprint("Failed to format: {}, err: {}".format(output, err))
            return FAILURE
        if success:
            print(output)
            return SUCCESS
        else:
            eprint(output)
            return FAILURE
    return SUCCESS


def cli():
    return main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

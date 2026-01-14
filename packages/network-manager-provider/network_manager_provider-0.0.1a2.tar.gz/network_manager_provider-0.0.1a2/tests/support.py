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

import os
import json
from network_manager_provider.cli.cli import main

BASE_TESTS_PATH = os.path.abspath(os.path.dirname(__file__))
TMP_TEST_PATH = os.path.join(BASE_TESTS_PATH, "tmp")

TEST_RES_DIR = os.path.join(BASE_TESTS_PATH, "res")


def cli_action(action_type, action, *action_args):
    return_code = None
    try:
        args = [action_type, action]
        args.extend(*action_args)
        return_code = main(args)
    except SystemExit as e:
        return_code = e.code
    return return_code


def assign_cli_action(action_type, item, container, *args):
    args = [item, container, *args]
    return cli_action(action_type, "assign", args)


def create_cli_action(action_type, name, *args):
    args = [name, *args]
    return cli_action(action_type, "create", args)


def read_cli_action(action_type, _id, *args):
    args = [_id, *args]
    return cli_action(action_type, "read", args)


def update_cli_action(action_type, _id, *args):
    args = [_id, *args]
    return cli_action(action_type, "update", args)


def delete_cli_action(action_type, _id, *args):
    args = [_id, *args]
    return cli_action(action_type, "delete", args)


def flush_cli_action(action_type, *args):
    args = [*args]
    return cli_action(action_type, "flush", args)


def list_cli_action(action_type, *args):
    args = [*args]
    return cli_action(action_type, "ls", args)


def json_to_dict(json_str):
    return json.loads(json_str)

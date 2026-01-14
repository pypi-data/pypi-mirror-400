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

from network_manager_provider.defaults import BUNDLE, default_persistence_path
from network_manager_provider.cli.parsers.actions import PositionalArgumentsAction


def valid_create_group(parser):
    create_group(parser)


def create_group(parser):
    bundle_group = parser.add_argument_group(title="Bundle arguments")
    bundle_group.add_argument(
        "name", action=PositionalArgumentsAction, help="The name of the bundle"
    )
    bundle_group.add_argument(
        "-cf",
        "--config-file",
        dest="{}_config".format(BUNDLE),
        help="The path to a file that contains a bundle configuration that should be associated with the bundle that is created.",
    )
    bundle_group.add_argument(
        "-d",
        "--directory",
        dest="{}_directory".format(BUNDLE),
        help="The directory path to where the bundle database should be located/created.",
        default=default_persistence_path,
    )


def read_group(parser):
    bundle_group = parser.add_argument_group(title="Bundle read arguments")
    bundle_group.add_argument(
        "id", action=PositionalArgumentsAction, help="The id of the bundle"
    )
    bundle_group.add_argument(
        "-d",
        "--directory",
        dest="{}_directory".format(BUNDLE),
        help="The directory path to where the bundle database should be located/created.",
        default=default_persistence_path,
    )


def update_group(parser):
    bundle_group = parser.add_argument_group(title="Bundle update arguments")
    bundle_group.add_argument(
        "id", action=PositionalArgumentsAction, help="The id of the Bundle."
    )
    bundle_group.add_argument(
        "-n",
        "--name",
        dest="{}_name".format(BUNDLE),
        help="The name of the Bundle",
    ),
    bundle_group.add_argument(
        "-cf",
        "--config-file",
        dest="{}_config".format(BUNDLE),
        help="The path to a file that contains a bundle configuration that should be associated with the bundle that is created.",
    )
    bundle_group.add_argument(
        "-d",
        "--directory",
        dest="{}_directory".format(BUNDLE),
        help="The directory path to where the bundle database should be located/created.",
        default=default_persistence_path,
    )


def delete_group(parser):
    bundle_group = parser.add_argument_group(title="Bundle delete arguments")
    bundle_group.add_argument(
        "id", action=PositionalArgumentsAction, help="The id of the bundle"
    )
    bundle_group.add_argument(
        "-d",
        "--directory",
        dest="{}_directory".format(BUNDLE),
        help="The directory path to where the bundle database should be located/created.",
        default=default_persistence_path,
    )


def flush_group(parser):
    bundle_group = parser.add_argument_group(title="Bundle flush arguments")
    bundle_group.add_argument(
        "-d",
        "--directory",
        dest="{}_directory".format(BUNDLE),
        help="The directory path to where the bundle database should be located/created.",
        default=default_persistence_path,
    )


def apply_group(parser):
    bundle_group = parser.add_argument_group(title="Bundle apply arguments")
    bundle_group.add_argument(
        "id", action=PositionalArgumentsAction, help="The id of the bundle"
    )
    bundle_group.add_argument(
        "-d",
        "--directory",
        dest="{}_directory".format(BUNDLE),
        help="The directory path to where the bundle database should be located/created.",
        default=default_persistence_path,
    )


def undo_group(parser):
    bundle_group = parser.add_argument_group(title="Bundle undo arguments")
    bundle_group.add_argument(
        "id", action=PositionalArgumentsAction, help="The id of the bundle"
    )
    bundle_group.add_argument(
        "-d",
        "--directory",
        dest="{}_directory".format(BUNDLE),
        help="The directory path to where the bundle database should be located/created.",
        default=default_persistence_path,
    )


def ls_group(parser):
    bundle_group = parser.add_argument_group(title="Bundle list arguments")
    bundle_group.add_argument(
        "-r",
        "--regex",
        dest="{}_regex".format(BUNDLE),
        default=None,
        help="An optional regex pattern to match which bundle names to list.",
    )
    bundle_group.add_argument(
        "-d",
        "--directory",
        dest="{}_directory".format(BUNDLE),
        help="The directory path to where the bundle database should be located/created.",
        default=default_persistence_path,
    )

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

from network_manager_provider.defaults import INTERFACE
from network_manager_provider.cli.parsers.actions import (
    PositionalArgumentsAction,
    KeyValueAction,
    ListAction,
)


def create_group(parser):
    interface_group = parser.add_argument_group(title="Interface create arguments")
    interface_group.add_argument(
        "name", action=PositionalArgumentsAction, help="The name of the interface"
    )
    interface_group.add_argument(
        "type", action=PositionalArgumentsAction, help="The type of interface"
    )
    interface_group.add_argument(
        "--kwargs",
        dest="{}_create_kwargs".format(INTERFACE),
        metavar="KEY=VALUE",
        action=KeyValueAction,
        help="""A comma-separated string of KEY=VALUE pairs that should be passed to the creation of the interface.
        If a value contains spaces, you should define the entire argument in quotes.
        """,
    )


def read_group(parser):
    interface_group = parser.add_argument_group(title="Interface read arguments")
    interface_group.add_argument(
        "name", action=PositionalArgumentsAction, help="The name of the interface"
    )
    interface_group.add_argument(
        "--args",
        dest="{}_read_args".format(INTERFACE),
        action=ListAction,
        help="A comma-separated string of arguments that should be returned about the interface.",
    )


def update_group(parser):
    interface_group = parser.add_argument_group(title="Interface update arguments")
    interface_group.add_argument(
        "name_or_index",
        action=PositionalArgumentsAction,
        help="The name or index of the interface",
    )
    interface_group.add_argument(
        "--args",
        dest="{}_update_kwargs".format(INTERFACE),
        metavar="KEY=VALUE",
        action=KeyValueAction,
        help="""A comma-separated string of KEY=VALUE pairs that should be passed to update of the interface.
        If a value contains spaces, you should define the entire argument in quotes.
        """,
    )


def delete_group(parser):
    interface_group = parser.add_argument_group(title="Interface delete arguments")
    interface_group.add_argument(
        "name", action=PositionalArgumentsAction, help="The name of the interface"
    )


def flush_group(parser):
    interface_group = parser.add_argument_group(title="Interface flush arguments")
    interface_group.add_argument(
        "-r",
        "--regex",
        dest="{}_regex".format(INTERFACE),
        default=None,
        help="An optional regex pattern to match which interface names to flush.",
    )


def ls_group(parser):
    interface_group = parser.add_argument_group(title="Interface list arguments")
    interface_group.add_argument(
        "-r",
        "--regex",
        dest="{}_regex".format(INTERFACE),
        default=None,
        help="An optional regex pattern to match which interface to list.",
    )
    interface_group.add_argument(
        "-t",
        "--types",
        dest="{}_link_types".format(INTERFACE),
        action=ListAction,
        default="any",
        help="An optional link types to filter which type of interfaces to list.",
    )

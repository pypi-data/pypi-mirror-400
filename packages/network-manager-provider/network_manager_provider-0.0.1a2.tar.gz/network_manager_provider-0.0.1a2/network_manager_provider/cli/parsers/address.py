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

from network_manager_provider.defaults import ADDRESS
from network_manager_provider.cli.parsers.actions import (
    PositionalArgumentsAction,
    KeyValueAction,
    ListAction,
)


def assign_group(parser):
    address_group = parser.add_argument_group(title="Address assign arguments")
    address_group.add_argument(
        "addr",
        action=PositionalArgumentsAction,
        help="The address that should be assigned",
    )
    address_group.add_argument(
        "link_name",
        action=PositionalArgumentsAction,
        help="The link that the address should be attached to",
    )
    address_group.add_argument(
        "--kwargs",
        dest="{}_assign_kwargs".format(ADDRESS),
        metavar="KEY=VALUE",
        action=KeyValueAction,
        help="""A comma-separated string of KEY=VALUE pairs that should be passed to the configuration of the address.
        If a value contains spaces, you should define the entire argument in quotes.
        """,
    )


def read_group(parser):
    address_group = parser.add_argument_group(title="Address assign arguments")
    address_group.add_argument(
        "link_name",
        action=PositionalArgumentsAction,
        help="The link that the address is attached to",
    )
    address_group.add_argument(
        "--args",
        dest="{}_read_args".format(ADDRESS),
        action=ListAction,
        help="A comma-separated string of arguments that should be returned about the address.",
    )


def delete_group(parser):
    address_group = parser.add_argument_group(title="Address delete arguments")
    address_group.add_argument(
        "addr",
        action=PositionalArgumentsAction,
        help="The address that should be deleted",
    )
    address_group.add_argument(
        "link_name",
        action=PositionalArgumentsAction,
        help="The link that the address should be removed from",
    )
    address_group.add_argument(
        "--kwargs",
        dest="{}_delete_kwargs".format(ADDRESS),
        metavar="KEY=VALUE",
        action=KeyValueAction,
        help="""A comma-separated string of KEY=VALUE pairs that should be passed to the configuration of the address.
        If a value contains spaces, you should define the entire argument in quotes.
        """,
    )

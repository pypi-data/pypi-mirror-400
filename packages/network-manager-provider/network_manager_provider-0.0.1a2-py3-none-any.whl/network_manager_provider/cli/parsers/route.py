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

from network_manager_provider.defaults import ROUTE
from network_manager_provider.cli.parsers.actions import (
    PositionalArgumentsAction,
    KeyValueAction,
)


def create_group(parser):
    route_group = parser.add_argument_group(title="Route create arguments")
    route_group.add_argument(
        "to", action=PositionalArgumentsAction, help="The destination of the route"
    )
    route_group.add_argument(
        "via", action=PositionalArgumentsAction, help="The gateway of the route"
    )
    route_group.add_argument(
        "--kwargs",
        dest="{}_create_kwargs".format(ROUTE),
        metavar="KEY=VALUE",
        action=KeyValueAction,
        help="""A comma-separated string of KEY=VALUE pairs that should be passed to the creation of the route.
        If a value contains spaces, you should define the entire argument in quotes.
        """,
    )


def delete_group(parser):
    route_group = parser.add_argument_group(title="Route delete arguments")
    route_group.add_argument(
        "to", action=PositionalArgumentsAction, help="The destination of the route"
    )
    route_group.add_argument(
        "via", action=PositionalArgumentsAction, help="The gateway of the route"
    )


def flush_group(parser):
    route_group = parser.add_argument_group(title="Route flush arguments")
    route_group.add_argument(
        "to_regex",
        action=PositionalArgumentsAction,
        help="The destination regex of the route",
    )


def ls_group(parser):
    interface_group = parser.add_argument_group(title="Route list arguments")
    interface_group.add_argument(
        "-r",
        "--to-regex",
        dest="{}_to_regex".format(ROUTE),
        default=None,
        help="An optional regex pattern to match which routes to list.",
    )

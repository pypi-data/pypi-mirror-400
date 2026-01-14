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

from network_manager_provider.defaults import NAMESPACE
from network_manager_provider.cli.parsers.actions import PositionalArgumentsAction


def create_group(parser):
    namespace_group = parser.add_argument_group(title="Namespace create arguments")
    namespace_group.add_argument(
        "name", action=PositionalArgumentsAction, help="The name of the namespace"
    )


def read_group(parser):
    namespace_group = parser.add_argument_group(title="Namespace read arguments")
    namespace_group.add_argument(
        "name", action=PositionalArgumentsAction, help="The name of the namespace"
    )


def update_group(parser):
    namespace_group = parser.add_argument_group(title="Namespace update arguments")
    namespace_group.add_argument(
        "name", action=PositionalArgumentsAction, help="The name of the namespace"
    )


def delete_group(parser):
    namespace_group = parser.add_argument_group(title="Namespace delete arguments")
    namespace_group.add_argument(
        "name", action=PositionalArgumentsAction, help="The name of the namespace"
    )


def flush_group(parser):
    namespace_group = parser.add_argument_group(title="Namespace flush arguments")
    namespace_group.add_argument(
        "-r",
        "--regex",
        dest="{}_regex".format(NAMESPACE),
        default=None,
        help="An optional regex pattern to match which namespace to flush.",
    )


def ls_group(parser):
    namespace_group = parser.add_argument_group(title="Namespace list arguments")
    namespace_group.add_argument(
        "-r",
        "--regex",
        dest="{}_regex".format(NAMESPACE),
        default=None,
        help="An optional regex pattern to match which namespace to list.",
    )

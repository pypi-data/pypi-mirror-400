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
from network_manager_provider.cli.parsers.route import (
    create_group,
    flush_group,
    delete_group,
    ls_group,
)


def create_groups(parser):
    create_group(parser)

    argument_groups = [ROUTE]
    return argument_groups


def delete_groups(parser):
    delete_group(parser)

    argument_groups = [ROUTE]
    return argument_groups


def flush_groups(parser):
    flush_group(parser)

    argument_groups = [ROUTE]
    return argument_groups


def ls_groups(parser):
    ls_group(parser)

    argument_groups = [ROUTE]
    return argument_groups

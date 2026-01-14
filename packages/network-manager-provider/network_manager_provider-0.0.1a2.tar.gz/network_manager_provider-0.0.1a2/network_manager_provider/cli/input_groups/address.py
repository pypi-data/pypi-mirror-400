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
from network_manager_provider.cli.parsers.address import (
    assign_group,
    read_group,
    delete_group,
)


def assign_groups(parser):
    assign_group(parser)

    argument_groups = [ADDRESS]
    return argument_groups


def read_groups(parser):
    read_group(parser)

    argument_groups = [ADDRESS]
    return argument_groups


def delete_groups(parser):
    delete_group(parser)

    argument_groups = [ADDRESS]
    return argument_groups

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

from network_manager_provider.defaults import INTERFACE, CREATE
from network_manager_provider.helpers.pyroute2 import (
    discover_pyroute2_function_name,
    discover_pyroute2_func_args,
    discover_pyroute2_func_kwargs,
    perform_pyroute2_operation,
)


async def create(
    name,
    interface_type,
    create_kwargs=None,
    ip_route_init_kwargs=None,
):
    if not create_kwargs:
        create_kwargs = {}

    if not ip_route_init_kwargs:
        ip_route_init_kwargs = {}

    func_name = discover_pyroute2_function_name(INTERFACE)
    func_args = discover_pyroute2_func_args(CREATE)
    func_kwargs = discover_pyroute2_func_kwargs(
        INTERFACE, name=name, interface_type=interface_type, **create_kwargs
    )

    success, operation_response = await perform_pyroute2_operation(
        func_name,
        *func_args,
        function_kwargs=func_kwargs,
        ip_route_init_kwargs=ip_route_init_kwargs,
    )
    operation_msg = None
    if "msg" in operation_response:
        operation_msg = operation_response["msg"]

    response = {}
    if not success:
        response["msg"] = f"Failed to create {interface_type} with name: {name}"
        if operation_msg:
            response["msg"] += f", err: {operation_msg}"
        return False, response

    response["msg"] = f"Added {interface_type} with name: {name}"
    return True, response

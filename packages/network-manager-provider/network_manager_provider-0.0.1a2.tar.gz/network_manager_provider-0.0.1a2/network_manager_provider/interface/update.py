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

from network_manager_provider.defaults import INTERFACE, UPDATE
from network_manager_provider.helpers.pyroute2 import (
    discover_pyroute2_function_name,
    discover_pyroute2_func_args,
    discover_pyroute2_func_kwargs,
    perform_pyroute2_operation,
    discover_pyroute2_func_dynamic_kwargs,
    validate_pyroute2_func_response,
)


async def update(name, update_kwargs=None, ip_route_init_kwargs=None):
    if not ip_route_init_kwargs:
        ip_route_init_kwargs = {}

    if not update_kwargs:
        update_kwargs = {}

    response = {}
    # Find the interface
    found_dynamic, dynamic_response = await discover_pyroute2_func_dynamic_kwargs(
        "link_lookup", ifname=name, ip_route_init_kwargs=ip_route_init_kwargs
    )
    if not found_dynamic:
        response["msg"] = f"Failed to find interface to update: {dynamic_response}"
        return False, response

    validated, validation_response = validate_pyroute2_func_response(
        response=dynamic_response, expected_types=(list, tuple, set)
    )
    if not validated:
        response["msg"] = (
            f"Failed to validate the lookup response of interface: {name} before updating, err: {validation_response}"
        )
        return False, response

    if len(dynamic_response) > 1:
        response["msg"] = (
            f"Found multiple interface indicies to update: {dynamic_response}"
        )
        return False, response

    func_name = discover_pyroute2_function_name(INTERFACE)
    func_args = discover_pyroute2_func_args(UPDATE)
    func_kwargs = discover_pyroute2_func_kwargs(INTERFACE, name=name, **update_kwargs)
    func_kwargs["index"] = dynamic_response[0]

    success, operation_response = await perform_pyroute2_operation(
        func_name,
        *func_args,
        function_kwargs=func_kwargs,
        ip_route_init_kwargs=ip_route_init_kwargs,
    )
    operation_msg = None
    if "msg" in operation_response:
        operation_msg = operation_response["msg"]

    if not success:
        response["msg"] = f"Failed to update link: {name}"
        if operation_msg:
            response["msg"] += f", err: {operation_msg}"
        return False, response

    response["msg"] = f"Updated link: {name}"
    return True, response

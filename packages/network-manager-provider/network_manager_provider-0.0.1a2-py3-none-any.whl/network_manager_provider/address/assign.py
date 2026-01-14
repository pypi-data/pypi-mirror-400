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

from network_manager_provider.defaults import ADDRESS, CREATE
from network_manager_provider.helpers.pyroute2 import (
    discover_pyroute2_function_name,
    discover_pyroute2_func_args,
    discover_pyroute2_func_kwargs,
    perform_pyroute2_operation,
    discover_pyroute2_func_dynamic_kwargs,
    validate_pyroute2_func_response,
)


async def assign(
    address,
    link_name,
    assign_kwargs=None,
    ip_route_init_kwargs=None,
):
    if not assign_kwargs:
        assign_kwargs = {}

    if not ip_route_init_kwargs:
        ip_route_init_kwargs = {}

    response = {}
    # Find the interface
    found_dynamic, dynamic_response = await discover_pyroute2_func_dynamic_kwargs(
        "link_lookup", ifname=link_name, ip_route_init_kwargs=ip_route_init_kwargs
    )
    if not found_dynamic:
        response["msg"] = (
            f"Failed to find link to attach address to: {dynamic_response}"
        )
        return False, response

    validated, validation_response = validate_pyroute2_func_response(
        response=dynamic_response, expected_types=(list, tuple, set)
    )
    if not validated:
        response["msg"] = (
            f"Failed to validate the lookup response of interface: {link_name} before assigning an address, err: {validation_response}"
        )
        return False, response

    if len(dynamic_response) > 1:
        response["msg"] = (
            f"Found multiple links to attach address to: {dynamic_response}"
        )
        return False, response

    if "/" in address:
        address_part, mask_part = address.split("/", 1)
    else:
        address_part = address
        mask_part = None

    if "mask" in assign_kwargs and assign_kwargs["mask"]:
        mask_part = assign_kwargs.pop("mask")

    func_name = discover_pyroute2_function_name(ADDRESS)
    func_args = discover_pyroute2_func_args(CREATE)
    func_kwargs = discover_pyroute2_func_kwargs(
        ADDRESS, address=address_part, mask=mask_part, **assign_kwargs
    )
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
        response["msg"] = f"Failed to assign address: {address} to: {link_name}"
        if operation_msg:
            response["msg"] += f", err: {operation_msg}"
        return False, response

    response["link"] = link_name
    response["address"] = address
    if mask_part:
        response["mask"] = mask_part
    response["msg"] = f"Assigned address: {address} to: {link_name}"
    return True, response

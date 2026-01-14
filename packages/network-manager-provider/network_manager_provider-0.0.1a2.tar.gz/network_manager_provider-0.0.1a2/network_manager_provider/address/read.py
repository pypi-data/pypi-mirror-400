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

from network_manager_provider.defaults import DUMP, ADDRESS
from network_manager_provider.helpers.pyroute2 import (
    discover_pyroute2_function_name,
    discover_pyroute2_func_args,
    discover_pyroute2_func_kwargs,
    perform_pyroute2_operation,
    discover_pyroute2_func_dynamic_kwargs,
    validate_pyroute2_func_response,
)


DEFAULT_LINK_READ_OPTIONS = [ADDRESS, "broadcast", "label"]


async def read(link_name, read_args=None, ip_route_init_kwargs=None):
    if not read_args:
        read_args = []

    if not ip_route_init_kwargs:
        ip_route_init_kwargs = {}

    response = {}
    # Find the interface
    found_dynamic, dynamic_response = await discover_pyroute2_func_dynamic_kwargs(
        "link_lookup", ifname=link_name, ip_route_init_kwargs=ip_route_init_kwargs
    )
    if not found_dynamic:
        response["msg"] = (
            f"Failed to find interface to read address from: {dynamic_response}"
        )
        return False, response

    validated, validation_response = validate_pyroute2_func_response(
        response=dynamic_response, expected_types=(list, tuple, set)
    )
    if not validated:
        response["msg"] = (
            f"Failed to validate the lookup response of interface: {link_name} before reading, err: {validation_response}"
        )
        return False, response

    if len(dynamic_response) > 1:
        response["msg"] = (
            f"Found multiple interface indicies to read address from: {dynamic_response}"
        )
        return False, response

    func_name = discover_pyroute2_function_name(ADDRESS)
    func_args = discover_pyroute2_func_args(DUMP)
    func_kwargs = discover_pyroute2_func_kwargs(ADDRESS)
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
        response["msg"] = f"Failed to read address from link: {link_name}"
        if operation_msg:
            response["msg"] += f", err: {operation_msg}"
        return False, response

    link = {}
    if "results" in operation_response:
        link = operation_response["results"][0]

    if not link:
        response["msg"] = f"Failed to find address on link with name: {link_name}"
        return False, response

    response["link"] = {
        "name": link_name,
    }
    for option in read_args or DEFAULT_LINK_READ_OPTIONS:
        if option in link:
            response["link"][option] = link[option]
        elif link.get(f"IFA_{option}", None):
            response["link"][option] = link.get(f"IFA_{option}")
        else:
            response["link"][option] = f"Option: {option} not found"
    return True, response

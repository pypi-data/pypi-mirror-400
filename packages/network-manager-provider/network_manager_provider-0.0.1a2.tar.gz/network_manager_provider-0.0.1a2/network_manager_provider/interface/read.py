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

from network_manager_provider.defaults import INTERFACE, READ
from network_manager_provider.helpers.pyroute2 import (
    discover_pyroute2_function_name,
    discover_pyroute2_func_args,
    discover_pyroute2_func_kwargs,
    perform_pyroute2_operation,
)


DEFAULT_LINK_READ_OPTIONS = ["state", "index"]


async def read(name, read_args=None, ip_route_init_kwargs=None):
    if not ip_route_init_kwargs:
        ip_route_init_kwargs = {}

    func_name = discover_pyroute2_function_name(INTERFACE)
    func_args = discover_pyroute2_func_args(READ)
    func_kwargs = discover_pyroute2_func_kwargs(INTERFACE, name=name)

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
        response["msg"] = f"Failed to read link: {name}"
        if operation_msg:
            response["msg"] += f", err: {operation_msg}"
        return False, response

    if "results" not in operation_response or not operation_response["results"]:
        response["msg"] = f"Failed to find link with name: {name}"
        return False, response
    links = operation_response["results"]

    response["link"] = {}
    for link in links:
        for option in read_args or DEFAULT_LINK_READ_OPTIONS:
            if option in link:
                response["link"][option] = link[option]
            elif link.get(f"IFLA_{option}", None):
                response["link"][option] = link.get(f"IFLA_{option}")
            else:
                response["link"][option] = f"Option: {option} not found"

    response["link"]["name"] = link.get("IFLA_IFNAME", None)
    return True, response

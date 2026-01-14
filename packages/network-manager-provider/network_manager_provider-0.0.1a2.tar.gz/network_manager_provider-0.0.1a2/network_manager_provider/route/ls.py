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

import re
from network_manager_provider.defaults import ROUTE, LS
from network_manager_provider.helpers.pyroute2 import (
    discover_pyroute2_function_name,
    perform_pyroute2_operation,
)


async def ls(to_regex=None, ip_route_init_kwargs=None):
    if not ip_route_init_kwargs:
        ip_route_init_kwargs = {}

    func_name = discover_pyroute2_function_name(f"{ROUTE}_{LS}")

    response = {}
    success, operation_response = await perform_pyroute2_operation(
        func_name,
        ip_route_init_kwargs=ip_route_init_kwargs,
    )
    operation_msg = None
    if "msg" in operation_response:
        operation_msg = operation_response["msg"]

    if not success:
        response["msg"] = "Failed to list routes"
        if operation_msg:
            response["msg"] += f", err: {operation_msg}"
        return False, response

    response["routes"], routes = [], []
    if "results" in operation_response:
        routes = operation_response["results"]

    for route in routes:
        to = route.get("RTA_DST", "default")
        dst_len = route.get("dst_len", None)
        to = f"{to}/{dst_len}" if dst_len else f"{to}"
        via = route.get("RTA_GATEWAY", None)

        route_info = {"to": to}
        if via:
            route_info["via"] = via
        if not to_regex:
            response["routes"].append(route_info)
        if to_regex and re.match(to_regex, to):
            response["routes"].append(route_info)

    if not response["routes"]:
        response["msg"] = "No routes found"
    else:
        response["msg"] = "Found routes"
    return True, response

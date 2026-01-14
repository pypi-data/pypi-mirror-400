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
from network_manager_provider.defaults import INTERFACE, LS
from network_manager_provider.helpers.pyroute2 import (
    discover_pyroute2_function_name,
    perform_pyroute2_operation,
)


async def ls(regex=None, link_types=None, ip_route_init_kwargs=None):
    if not ip_route_init_kwargs:
        ip_route_init_kwargs = {}

    if not link_types:
        link_types = []

    func_name = discover_pyroute2_function_name(f"{INTERFACE}_{LS}")

    response = {}
    success, operation_response = await perform_pyroute2_operation(
        func_name,
        ip_route_init_kwargs=ip_route_init_kwargs,
    )
    operation_msg = None
    if "msg" in operation_response:
        operation_msg = operation_response["msg"]

    if not success:
        response["msg"] = "Failed to list links"
        if operation_msg:
            response["msg"] += f", err: {operation_msg}"
        return False, response

    response["links"], links = [], []
    if "results" in operation_response:
        links = operation_response["results"]

    for link in links:
        link_list_entry = {}

        link_name = link.get("IFLA_IFNAME")
        link_info = link.get("IFLA_LINKINFO", {})
        link_kind = link_info.get("IFLA_INFO_KIND", None)

        link_list_entry["name"] = link_name
        if not link_kind:
            link_list_entry["type"] = "UNKNOWN"
        else:
            link_list_entry["type"] = link_kind

        if link_types:
            if "any" not in link_types and link_list_entry["type"] not in link_types:
                continue

        if not regex:
            response["links"].append(link_list_entry)
        if regex and re.match(regex, link_list_entry["name"]):
            response["links"].append(link_list_entry)

    if not response["links"]:
        response["msg"] = "No links found"
    else:
        response["msg"] = "Found links"
    return True, response

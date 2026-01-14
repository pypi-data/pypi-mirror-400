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


from network_manager_provider.namespace.ls import ls as ls_namespace
from network_manager_provider.interface.ls import ls as ls_interface
from network_manager_provider.route.ls import ls as ls_route


async def read(name):
    response = {}

    list_namespace_success, list_namespace_resp = await ls_namespace()
    if not list_namespace_success:
        response["msg"] = "Failed to list namespaces."
        return False, response

    if name not in list_namespace_resp.get("namespaces", []):
        response["msg"] = f"Namespace {name} does not exist."
        return False, response

    ip_route_init_kwargs = {"netns": name}
    list_interface_success, list_interface_resp = await ls_interface(
        ip_route_init_kwargs=ip_route_init_kwargs
    )
    if list_interface_success:
        response["interfaces"] = list_interface_resp.get("interfaces", [])
    else:
        response["intefaces"] = []

    list_route_success, list_route_resp = await ls_route(
        ip_route_init_kwargs=ip_route_init_kwargs
    )
    if list_route_success:
        response["routes"] = list_route_resp.get("routes", [])
    else:
        response["routes"] = []

    response["name"] = name
    response["msg"] = "Namespace details."
    return True, response

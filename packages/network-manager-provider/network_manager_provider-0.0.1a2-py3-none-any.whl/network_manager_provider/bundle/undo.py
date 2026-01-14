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

import asyncio
from network_manager_provider.bundle.read import read
from network_manager_provider.interface.delete import delete as delete_interface
from network_manager_provider.interface.ls import ls as ls_interface
from network_manager_provider.route.delete import delete as delete_route
from network_manager_provider.route.ls import ls as ls_route
from network_manager_provider.namespace.delete import delete as delete_namespace


async def remove_interfaces(interfaces, ip_route_init_kwargs=None):
    remove_interface_task = [
        delete_interface(name, ip_route_init_kwargs=ip_route_init_kwargs)
        for name in interfaces
    ]
    interface_remove_results = await asyncio.gather(*remove_interface_task)
    remove_successes = [
        response for success, response in interface_remove_results if success
    ]
    remove_failures = [
        response for success, response in interface_remove_results if not success
    ]
    return remove_successes, remove_failures


async def remove_routes(routes, ip_route_init_kwargs=None):
    remove_routes_tasks = []
    for route in routes:
        if "via" in route:
            remove_routes_tasks.append(
                delete_route(
                    route.pop("to"),
                    route.pop("via"),
                    ip_route_init_kwargs=ip_route_init_kwargs,
                )
            )
        else:
            remove_routes_tasks.append(
                delete_route(route.pop("to"), ip_route_init_kwargs=ip_route_init_kwargs)
            )

    remove_routes_results = await asyncio.gather(*remove_routes_tasks)
    successes = [response for success, response in remove_routes_results if success]
    failures = [response for success, response in remove_routes_results if not success]
    return successes, failures


async def remove_namespace(name, settings):
    interfaces = settings.get("interfaces", {})
    ip_route_init_kwargs = {"netns": name}
    list_interface_success, list_interface_resp = await ls_interface(
        ip_route_init_kwargs=ip_route_init_kwargs
    )
    if not list_interface_success:
        return False, list_interface_resp
    existing_interfaces = list_interface_resp.get("interfaces", [])

    delete_interfaces = [
        name for name in interfaces.keys() if name in existing_interfaces
    ]
    interfaces_success, interfaces_failures = await remove_interfaces(
        delete_interfaces, ip_route_init_kwargs=ip_route_init_kwargs
    )

    routes = settings.get("routes", [])
    list_route_success, list_route_resp = await ls_route(
        ip_route_init_kwargs=ip_route_init_kwargs
    )
    if not list_route_success:
        return False, list_route_resp
    existing_routes = list_route_resp.get("routes", [])

    delete_routes = []
    # TODO speedup
    for route in routes:
        for existing_route in existing_routes:
            if route.get("to") == existing_route.get("to"):
                if "via" in route and "via" in existing_route:
                    if route.get("via") == existing_route.get("via"):
                        delete_routes.append(route)
                elif "via" not in route and "via" not in existing_route:
                    delete_routes.append(route)
    routes_success, routes_failures = await remove_routes(
        delete_routes, ip_route_init_kwargs=ip_route_init_kwargs
    )
    return await delete_namespace(name)


async def remove_namespaces(namespaces):
    remove_namespace_task = [
        remove_namespace(name, settings) for name, settings in namespaces.items()
    ]
    namespace_remove_results = await asyncio.gather(*remove_namespace_task)
    remove_successes = [
        response for success, response in namespace_remove_results if success
    ]
    remove_failures = [
        response for success, response in namespace_remove_results if not success
    ]
    return remove_successes, remove_failures


async def undo(bundle_id, directory=None):
    response = {}

    read_success, read_response = await read(bundle_id, directory=directory)
    if not read_success:
        response["msg"] = read_response
        return False, response

    bundle = read_response["bundle"]
    # Namespaces
    namespaces = bundle["config"].get("namespaces", {})
    remove_ns_success, remove_ns_failures = await remove_namespaces(namespaces)
    response["namespaces"] = {
        "successes": remove_ns_success,
        "failures": remove_ns_failures,
    }

    # Interfaces
    interfaces = bundle["config"].get("interfaces", {})
    remove_if_success, remove_if_failures = await remove_interfaces(interfaces)
    response["interfaces"] = {
        "successes": remove_if_success,
        "failures": remove_if_failures,
    }

    # Bridges
    bridges = bundle["config"].get("bridges", {})
    remove_br_success, remove_br_failures = await remove_interfaces(bridges)
    response["bridges"] = {
        "successes": remove_br_success,
        "failures": remove_br_failures,
    }

    return True, response

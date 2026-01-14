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
from pyroute2 import AsyncIPRoute
from network_manager_provider.bundle.config import (
    get_lookup_variables,
    prepare_lookup_variables,
    recursively_format,
)
from network_manager_provider.defaults import BUNDLE, HOST, INTERFACE, BRIDGE, ROUTE
from network_manager_provider.storage.dictdatabase import DictDatabase
from network_manager_provider.address.assign import assign as assign_address
from network_manager_provider.interface.create import create as create_interface
from network_manager_provider.interface.read import read
from network_manager_provider.interface.update import update as update_interface
from network_manager_provider.interface.ls import ls as ls_interface
from network_manager_provider.route.create import create as create_route
from network_manager_provider.namespace.create import create as create_namespace
from network_manager_provider.namespace.read import read as read_namespace


async def gather_func_results(tasks):
    results = await asyncio.gather(*tasks)
    successes = [response for success, response in results if success]
    failures = [response for success, response in results if not success]
    return successes, failures


async def provision_link(name, settings, ip_route_init_kwargs=None):
    interface_type = settings.get("type", None)
    if not interface_type:
        return False, {
            "msg": "The interface 'type' is required on interface: {}.".format(name)
        }
    found, _ = await read(name, interface_type)
    if found:
        return False, {
            "msg": "An interface with the name: {} already exists.".format(name)
        }
    return await create_interface(
        name,
        interface_type,
        create_kwargs=settings,
        ip_route_init_kwargs=ip_route_init_kwargs,
    )


async def provision_links(links, ip_route_init_kwargs=None):
    interface_tasks = [
        provision_link(name, settings, ip_route_init_kwargs=ip_route_init_kwargs)
        for name, settings in links.items()
    ]
    return await gather_func_results(interface_tasks)


async def update_link_state(name, settings, ip_route_init_kwargs=None):
    state = settings.get("state", None)
    if not state:
        return False, {
            "msg": "The 'state' attribute is required to update the link state for: {}.".format(
                name
            )
        }

    update_kwargs = {
        "state": state,
    }
    return await update_interface(
        name,
        update_kwargs=update_kwargs,
        ip_route_init_kwargs=ip_route_init_kwargs,
    )


async def update_links_state(links, ip_route_init_kwargs=None):
    interface_tasks = [
        update_link_state(name, settings, ip_route_init_kwargs=ip_route_init_kwargs)
        for name, settings in links.items()
    ]
    return await gather_func_results(interface_tasks)


async def assign_address_to_link(
    address, link_name, assign_kwargs=None, ip_route_init_kwargs=None
):
    return await assign_address(
        address,
        link_name,
        assign_kwargs=assign_kwargs,
        ip_route_init_kwargs=ip_route_init_kwargs,
    )


async def assign_addresses_to_link(
    addresses, link_name, assign_kwargs=None, ip_route_init_kwargs=None
):
    address_tasks = [
        assign_address_to_link(
            address,
            link_name,
            assign_kwargs=assign_kwargs,
            ip_route_init_kwargs=ip_route_init_kwargs,
        )
        for address in addresses
    ]
    return await gather_func_results(address_tasks)


async def assign_addresses_to_links(links, ip_route_init_kwargs=None):
    assign_tasks = [
        assign_addresses_to_link(
            addresses, link_name, ip_route_init_kwargs=ip_route_init_kwargs
        )
        for link_name, addresses in links.items()
    ]
    if not assign_tasks:
        return [], []

    success_results, failure_results = zip(*await asyncio.gather(*assign_tasks))
    successes = [success for success in success_results if success]
    failures = [failure for failure in failure_results if failure]
    return successes, failures


async def assign_link_to_bridge(link_name, bridge_name, ip_route_init_kwargs=None):
    found, _ = await read(link_name, read_args=["index"], ip_route_init_kwargs=ip_route_init_kwargs)
    if not found:
        return False, {"msg": f"Link: {link_name} does not exist."}
    found, bridge = await read(bridge_name, read_args=["index"], ip_route_init_kwargs=ip_route_init_kwargs)
    if not found:
        return False, {"msg": f"Bridge: {bridge_name} does not exist."}

    if "link" not in bridge:
        return False, {"msg": f"Failed to get link details for bridge: {bridge}"}

    if "index" not in bridge["link"]:
        return False, {"msg": f"Failed to get index for bridge: {bridge}"}

    update_kwargs = {"master": bridge["link"]["index"]}
    return await update_interface(
        link_name,
        update_kwargs=update_kwargs,
        ip_route_init_kwargs=ip_route_init_kwargs,
    )


async def assign_links_to_bridge(links, bridge_name, ip_route_init_kwargs=None):
    interface_tasks = [
        assign_link_to_bridge(
            name, bridge_name, ip_route_init_kwargs=ip_route_init_kwargs
        )
        for name in links
    ]
    return await gather_func_results(interface_tasks)


async def provision_route(to, via, create_kwargs=None, ip_route_init_kwargs=None):
    return await create_route(
        to, via, create_kwargs=create_kwargs, ip_route_init_kwargs=ip_route_init_kwargs
    )


async def provision_routes(routes, ip_route_init_kwargs=None):
    provision_routes_tasks = [
        provision_route(
            route.pop("to"),
            route.pop("via"),
            create_kwargs=route,
            ip_route_init_kwargs=ip_route_init_kwargs,
        )
        for route in routes
    ]
    return await gather_func_results(provision_routes_tasks)


async def move_interface_to_namespace(interface_name, namespace_name):
    return await update_interface(
        interface_name,
        update_kwargs={"net_ns_fd": namespace_name},
    )


async def move_interfaces_to_namespace(
    interfaces, namespace, ip_route_init_kwargs=None
):
    move_interface_tasks = [
        move_interface_to_namespace(interface_name, namespace)
        for interface_name in interfaces
    ]
    return await gather_func_results(move_interface_tasks)


async def provision_namespace(name, settings):
    # Initialisation
    namespace_successes, namespace_failures = [], []
    found, _ = await read_namespace(name)
    if not found:
        create_namespace_success, create_namespace_response = await create_namespace(
            name
        )
        if not create_namespace_success:
            namespace_failures.append(create_namespace_response)
            return namespace_successes, namespace_failures
        namespace_successes.append(create_namespace_response)
    else:
        namespace_successes.append({"msg": f"Namespace: {name} already exists."})

    ip_route_init_kwargs = {"netns": name}

    # Initialisation tasks
    initialisation_tasks = settings.get("initialisation", {})

    # Handle move tasks
    init_move_tasks = initialisation_tasks.pop("move", [])
    interfaces_move_namespace = []
    for move_task in init_move_tasks:
        move_from = move_task.get("from", HOST)
        move_type = move_task.get("type", None)
        move_name = move_task.get("name", None)
        if not move_from:
            namespace_failures.append(
                {
                    "msg": f"Initialisation move task is missing the 'from' attribute in namespace: {name}."
                }
            )
            continue

        if not move_type or not move_name:
            namespace_failures.append(
                {
                    "msg": f"Initialisation move task is missing the 'type' or 'name' attribute in namespace: {name}."
                }
            )
            continue

        if move_type in [INTERFACE, "link"] and move_from == HOST:
            interfaces_move_namespace.append(move_name)

    # Move interfaces to namespace
    move_success, move_failures = await move_interfaces_to_namespace(
        interfaces_move_namespace, name
    )
    if move_success:
        namespace_successes.extend(move_success)
    if move_failures:
        namespace_failures.extend(move_failures)

    # Interfaces and bridges
    interfaces = settings.get("interfaces", {})
    bridges = settings.get("bridges", {})

    ## Update existing interfaces and bridges and create new ones
    interface_types = [
        interface["type"]
        for interface in interfaces.values()
        if "type" in interface and interface["type"]
    ]
    _, found_link_resp = await ls_interface(
        link_types=interface_types, ip_route_init_kwargs=ip_route_init_kwargs
    )
    existing_interfaces = found_link_resp.get("links", [])

    _, existing_bridges_resp = await ls_interface(
        link_types=[BRIDGE], ip_route_init_kwargs=ip_route_init_kwargs
    )
    existing_bridges = existing_bridges_resp.get("links", [])
    existing_links = existing_interfaces + existing_bridges

    for links in [interfaces, bridges]:
        links_to_update = {}
        for existing_link in existing_links:
            if existing_link["name"] not in links:
                continue

            if not links[existing_link["name"]].get("type", None):
                continue

            if links[existing_link["name"]]["type"] == existing_link["type"]:
                links_to_update[existing_link["name"]] = links[existing_link["name"]]

        updated_links, updated_links_response = await update_links_addresses_and_state(
            links=links_to_update,
            ip_route_init_kwargs=ip_route_init_kwargs,
        )
        addresses_response = updated_links_response.get("addresses", {})
        state_response = updated_links_response.get("state", {})
        if updated_links:
            namespace_successes.extend(addresses_response.get("successes", []))
            namespace_successes.extend(state_response.get("successes", []))
        else:
            namespace_failures.extend(addresses_response.get("failures", []))
            namespace_failures.extend(state_response.get("failures", []))

    existing_interface_names = [
        existing_link["name"] for existing_link in existing_interfaces
    ]
    missing_links = {
        link_name: link_settings
        for link_name, link_settings in interfaces.items()
        if link_name not in existing_interface_names
    }
    existing_bridge_names = [
        existing_link["name"] for existing_link in existing_bridges
    ]
    missing_bridges = {
        link_name: link_settings
        for link_name, link_settings in bridges.items()
        if link_name not in existing_bridge_names
    }

    # Bridges and routes
    routes = settings.get("routes", [])

    ip_route_init_kwargs = {"netns": name}
    create_stack_success, create_stack_response = await create_stack(
        interfaces=missing_links,
        bridges=missing_bridges,
        routes=routes,
        ip_route_init_kwargs=ip_route_init_kwargs,
    )
    if not create_stack_success:
        namespace_failures.append(
            {
                "msg": f"Failed to create stack inside namespace: {name}",
                "details": create_stack_response,
            }
        )
    return namespace_successes, namespace_failures


async def provision_namespaces(namespaces):
    provision_namespace_tasks = [
        provision_namespace(name, settings) for name, settings in namespaces.items()
    ]
    if not provision_namespace_tasks:
        return [], []

    provision_successes, provision_failures = zip(
        *await asyncio.gather(*provision_namespace_tasks)
    )
    provision_successes = [success for success in provision_successes if success]
    provision_failures = [failure for failure in provision_failures if failure]
    return provision_successes, provision_failures


async def create_stack(
    interfaces=None, bridges=None, routes=None, ip_route_init_kwargs=None
):
    if not ip_route_init_kwargs:
        ip_route_init_kwargs = {}

    if not interfaces:
        interfaces = {}

    if not bridges:
        bridges = {}

    if not routes:
        routes = []

    response = {}
    # Interfaces
    interface_successes, interface_failures = await provision_links(
        interfaces, ip_route_init_kwargs=ip_route_init_kwargs
    )
    response["interfaces"] = {
        "provision": {},
    }
    if interface_successes:
        response["interfaces"]["provision"]["successes"] = interface_successes
    if interface_failures:
        response["interfaces"]["provision"]["failures"] = interface_failures

    # Assign addresses and set state for interfaces
    updated_interfaces, updated_interfaces_response = (
        await update_links_addresses_and_state(
            links=interfaces, ip_route_init_kwargs=ip_route_init_kwargs
        )
    )
    response["interfaces"]["addresses"] = updated_interfaces_response.get(
        "addresses", {}
    )
    response["interfaces"]["state"] = updated_interfaces_response.get("state", {})

    # Create and configure bridges
    bridge_successes, bridge_failures = await provision_links(
        bridges, ip_route_init_kwargs=ip_route_init_kwargs
    )
    response["bridges"] = {
        "provision": {},
    }
    if bridge_successes:
        response["bridges"]["provision"]["successes"] = bridge_successes
    if bridge_failures:
        response["bridges"]["provision"]["failures"] = bridge_failures

    # Assign addresses and set state for bridges
    updated_bridges, updated_bridges_response = await update_links_addresses_and_state(
        links=bridges, ip_route_init_kwargs=ip_route_init_kwargs
    )
    response["bridges"]["addresses"] = updated_bridges_response.get("addresses", {})
    response["bridges"]["state"] = updated_bridges_response.get("state", {})

    # Assign links to bridges
    bridge_links = {
        bridge_name: bridge_settings.get("interfaces", [])
        for bridge_name, bridge_settings in bridges.items()
        if bridge_settings.get("interfaces", [])
    }

    assign_links_successes, assign_links_failures = [], []
    for bridge_name, links in bridge_links.items():
        assign_success, assign_failures = await assign_links_to_bridge(
            links, bridge_name, ip_route_init_kwargs=ip_route_init_kwargs
        )
        assign_links_successes.extend(assign_success)
        assign_links_failures.extend(assign_failures)

    response["bridges"]["links"] = {}
    if assign_links_successes:
        response["bridges"]["links"]["successes"] = assign_links_successes
    if assign_links_failures:
        response["bridges"]["links"]["failures"] = assign_links_failures

    # Set bridge state
    bridge_state_successes, bridge_state_failures = await update_links_state(
        bridges,
        ip_route_init_kwargs=ip_route_init_kwargs,
    )
    response["bridges"]["state"] = {}
    if bridge_state_successes:
        response["bridges"]["state"]["successes"] = bridge_state_successes
    if bridge_state_failures:
        response["bridges"]["state"]["failures"] = bridge_state_failures

    # Routes
    routes_success, routes_failures = await provision_routes(
        routes, ip_route_init_kwargs=ip_route_init_kwargs
    )
    response["routes"] = {}
    if routes_success:
        response["routes"]["successes"] = routes_success
    if routes_failures:
        response["routes"]["failures"] = routes_failures

    if (
        interface_failures
        or assign_links_failures
        or bridge_state_failures
        or routes_failures
    ):
        return False, response
    return True, response


async def update_links_addresses_and_state(links=None, ip_route_init_kwargs=None):
    response = {}

    if not links:
        links = {}

    # Assign addresses to links
    link_addresses = {
        link_name: link_settings.get("addresses", [])
        for link_name, link_settings in links.items()
        if link_settings.get("addresses", [])
    }
    assign_link_successes, assign_link_failures = await assign_addresses_to_links(
        link_addresses,
        ip_route_init_kwargs=ip_route_init_kwargs,
    )
    response["addresses"] = {}
    if assign_link_successes:
        response["addresses"]["successes"] = assign_link_successes
    if assign_link_failures:
        response["addresses"]["failures"] = assign_link_failures

    # Set link state
    link_state_successes, link_state_failures = await update_links_state(
        links,
        ip_route_init_kwargs=ip_route_init_kwargs,
    )
    response["state"] = {}
    if link_state_successes:
        response["state"]["successes"] = link_state_successes
    if link_state_failures:
        response["state"]["failures"] = link_state_failures
    if assign_link_failures or link_state_failures:
        return False, response
    return True, response


async def apply(bundle_id, directory=None):
    response = {}

    bundle_db = DictDatabase(BUNDLE, directory=directory)
    if not await bundle_db.exists():
        if not await bundle_db.touch():
            response["msg"] = (
                "The Bundle database: {} did not exist in directory: {}, and it could not be created.".format(
                    bundle_db.name, directory
                )
            )
            return False, response

    bundle = await bundle_db.get(bundle_id)
    if not bundle:
        response["msg"] = (
            "Failed to find a Bundle inside the database with name: {} to update.".format(
                bundle_id
            )
        )
        return False, response
    response["id"] = bundle_id
    if "config" not in bundle or not bundle["config"]:
        response["msg"] = "The Bundle does not have a 'config' to apply."
        return False, response
    bundle_config = bundle["config"]

    # Prepare lookup variables
    lookup_variables = get_lookup_variables(bundle_config)
    prepared_lookup_variables = {}
    for lookup_type in [INTERFACE, BRIDGE, ROUTE]:
        lookup_vars = f"{lookup_type}s"
        if lookup_vars not in lookup_variables:
            continue

        prepared_variables, prepared_interfaces_variables = (
            await prepare_lookup_variables(
                lookup_variables[lookup_vars], lookup_type=lookup_type
            )
        )
        if not prepared_variables:
            response["msg"] = prepared_interfaces_variables
            return False, response

        prepared_lookup_variables[lookup_type] = prepared_interfaces_variables

    # Prepare config with lookup variables
    create_stack_configs = {}

    for config_types in [INTERFACE, BRIDGE, ROUTE]:
        config_vars = f"{config_types}s"
        if config_types not in prepared_lookup_variables:
            create_stack_configs[config_types] = bundle["config"].get(config_vars, {})
        else:
            create_stack_configs[config_types] = await recursively_format(
                prepared_lookup_variables[config_types],
                bundle["config"].get(config_vars, {}),
            )

    # Create stack
    create_stack_success, create_stack_response = await create_stack(
        interfaces=create_stack_configs.get(INTERFACE, {}),
        bridges=create_stack_configs.get(BRIDGE, {}),
        routes=create_stack_configs.get(ROUTE, []),
    )

    if not create_stack_success:
        response["msg"] = "Failed to create network stack."
        response["details"] = create_stack_response
        return False, response
    response.update(create_stack_response)

    # Namespaces
    namespaces = bundle["config"].get("namespaces", {})
    namespace_successes, namespace_failures = await provision_namespaces(namespaces)
    response["namespaces"] = {}
    if namespace_successes:
        response["namespaces"]["successes"] = namespace_successes
    if namespace_failures:
        response["namespaces"]["failures"] = namespace_failures

    if namespace_failures:
        return False, response
    return True, response

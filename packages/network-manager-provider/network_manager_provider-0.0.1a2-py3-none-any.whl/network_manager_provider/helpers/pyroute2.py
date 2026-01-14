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

import copy
import inspect
from collections.abc import AsyncGenerator
from pyroute2 import AsyncIPRoute

from network_manager_provider.defaults import (
    ADDRESS,
    INTERFACE,
    ROUTE,
    CREATE,
    READ,
    UPDATE,
    DELETE,
    DUMP,
    LS,
)


pyroute2_integer_options = [
    "mtu",
    "IFLA_MTU",
    "txqlen",
    "vlan",
    "vf",
    "vlan_id",
    "ipip_ttl",
    "cost",
    "index",
    "master",
    "mask",
]


async def execute_ndb_function(ndb_object, nbd_func_name, *args, **kwargs):
    ndb_func = getattr(ndb_object, nbd_func_name)
    try:
        if inspect.iscoroutinefunction(ndb_func):
            return_code = await ndb_func(*args, **kwargs)
        else:
            return_code = ndb_func(*args, **kwargs)
        return True, return_code
    except Exception as err:
        return False, str(err)
    return False, "Failed to execute function: {}, unknown error".format(nbd_func_name)


async def perform_pyroute2_operation(
    function_name, *function_args, function_kwargs=None, ip_route_init_kwargs=None
):
    if not function_kwargs:
        function_kwargs = {}

    if not ip_route_init_kwargs:
        ip_route_init_kwargs = {}

    response = {}
    async with AsyncIPRoute(**ip_route_init_kwargs) as ipr:
        success, return_object = await execute_ndb_function(
            ipr, function_name, *function_args, **function_kwargs
        )
        if isinstance(return_object, str):
            response["msg"] = return_object
        elif isinstance(return_object, AsyncGenerator):
            response["results"] = [item async for item in return_object]
        elif isinstance(return_object, (list, set, tuple)):
            response["results"] = [item for item in return_object]
        else:
            response["result"] = return_object

        if not success:
            return False, response
        return True, response
    return False, response


def discover_pyroute2_function_name(library_operation):
    if library_operation == INTERFACE:
        return "link"
    if library_operation == ROUTE:
        return "route"
    if library_operation == ADDRESS:
        return "addr"
    if library_operation == f"{ROUTE}_{LS}":
        return "get_routes"
    if library_operation == f"{INTERFACE}_{LS}":
        return "get_links"
    return None


def discover_pyroute2_func_args(library_action):
    if library_action == CREATE:
        return ["add"]
    if library_action == READ:
        return ["get"]
    if library_action in [UPDATE]:
        return ["set"]
    if library_action == DELETE:
        return ["del"]
    if library_action == DUMP:
        return ["dump"]
    return None


def discover_pyroute2_func_kwargs(library_operation, **kwargs):
    input_kwargs = copy.deepcopy(kwargs)
    pyroute2_function_dict = {}

    # Translate Interface related kwargs
    if library_operation == INTERFACE:
        if "name" in input_kwargs:
            pyroute2_function_dict["ifname"] = input_kwargs.pop("name")
        if "interface_type" in input_kwargs:
            pyroute2_function_dict["kind"] = input_kwargs.pop("interface_type")

    # Translate Route related kwargs
    if library_operation == ROUTE:
        if "to" in input_kwargs:
            pyroute2_function_dict["dst"] = input_kwargs.pop("to")
        if "via" in input_kwargs and input_kwargs["via"]:
            pyroute2_function_dict["gateway"] = input_kwargs.pop("via")

    for key, value in input_kwargs.items():
        if not value:
            continue

        _value = value
        if key in pyroute2_integer_options:
            _value = int(value)
        pyroute2_function_dict[key] = _value
    return pyroute2_function_dict


async def discover_pyroute2_func_dynamic_kwargs(
    func_name, ip_route_init_kwargs=None, **kwargs
):
    if not ip_route_init_kwargs:
        ip_route_init_kwargs = {}

    async with AsyncIPRoute(**ip_route_init_kwargs) as ipr:
        return await execute_ndb_function(ipr, func_name, **kwargs)


def validate_pyroute2_func_response(
    response=None, expected_types=None, allow_empty=False
):
    if response is None:
        return False, "No response from pyroute2"

    if expected_types and not isinstance(response, expected_types):
        return (
            False,
            f"Invalid type of response, expected: {expected_types}, got: {type(response)}",
        )

    if not response and not allow_empty:
        return False, "Invalid empty response from pyroute2"

    return True, None
